from typing import List, Optional, Dict
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseLLMService, Message, CompletionResponse, ModelInfo
from ..utils.exceptions import (
    APIKeyNotFoundError,
    ModelNotFoundError,
    RateLimitError,
    InvalidRequestError,
    LLMServiceError
)
from ..utils.config import settings

class GoogleService(BaseLLMService):
    """Google PaLM服务实现"""
    
    def __init__(self):
        """初始化Google PaLM客户端"""
        if not settings.google_api_key:
            raise APIKeyNotFoundError("Google API key not found")
        
        genai.configure(api_key=settings.google_api_key)
        self.default_model = "gemini-pro"
        
        # 初始化模型
        try:
            self.model = genai.GenerativeModel(self.default_model)
        except Exception as e:
            raise LLMServiceError(f"Failed to initialize Google PaLM model: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> CompletionResponse:
        """生成文本"""
        try:
            generation_config = {
                "temperature": temperature,
                "top_p": kwargs.get("top_p", 0.95),
                "top_k": kwargs.get("top_k", 40),
                "max_output_tokens": max_tokens
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # 计算token数量（Google API目前不直接提供token计数）
            prompt_tokens = await self.count_tokens(prompt)
            completion_tokens = await self.count_tokens(response.text)
            
            return CompletionResponse(
                text=response.text,
                model=self.default_model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens
            )
            
        except Exception as e:
            if "quota" in str(e).lower():
                raise RateLimitError(f"Google PaLM API rate limit exceeded: {str(e)}")
            elif "invalid" in str(e).lower():
                raise InvalidRequestError(f"Invalid request to Google PaLM API: {str(e)}")
            else:
                raise LLMServiceError(f"Google PaLM API error: {str(e)}")
    
    async def chat_complete(
        self,
        messages: List[Message],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> CompletionResponse:
        """聊天完成"""
        try:
            chat = self.model.start_chat(history=[])
            
            for message in messages:
                if message.role == "user":
                    response = chat.send_message(
                        message.content,
                        generation_config={
                            "temperature": temperature,
                            "top_p": kwargs.get("top_p", 0.95),
                            "top_k": kwargs.get("top_k", 40),
                            "max_output_tokens": max_tokens
                        }
                    )
            
            # 计算token数量
            prompt_tokens = sum(await self.count_tokens(msg.content) for msg in messages)
            completion_tokens = await self.count_tokens(response.text)
            
            return CompletionResponse(
                text=response.text,
                model=self.default_model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens
            )
            
        except Exception as e:
            raise LLMServiceError(f"Google PaLM chat completion error: {str(e)}")
    
    async def get_model_info(self) -> ModelInfo:
        """获取模型信息"""
        # Google PaLM的定价信息（美元/1K tokens）
        pricing = {
            "gemini-pro": {
                "input": 0.00025,   # $0.00025/1K tokens
                "output": 0.0005    # $0.0005/1K tokens
            },
            "gemini-pro-vision": {
                "input": 0.00025,
                "output": 0.0005
            }
        }
        
        return ModelInfo(
            id=self.default_model,
            name="Gemini Pro",
            provider="Google",
            description="Google的最新大语言模型，具有强大的理解和生成能力",
            max_tokens=30720,  # Gemini Pro的上下文窗口
            pricing=pricing.get(self.default_model)
        )
    
    async def count_tokens(self, text: str) -> int:
        """计算文本的token数量"""
        try:
            # Google目前没有提供直接的token计数API
            # 使用简单估算方法：按照GPT-3的统计，每个单词平均对应1.3个token
            return len(text.split()) * 1.3
        except Exception:
            return len(text.split()) * 1.3
    
    async def validate_connection(self) -> bool:
        """验证API连接是否正常"""
        try:
            # 发送一个简单的测试消息
            response = self.model.generate_content("test")
            return response.text is not None
        except Exception:
            return False 