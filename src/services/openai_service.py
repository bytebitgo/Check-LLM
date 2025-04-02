import os
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from datetime import datetime
from .base import LLMService, ModelInfo, CompletionResponse
from .factory import LLMServiceFactory

@LLMServiceFactory.register("openai")
class OpenAIService(LLMService):
    """OpenAI服务"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API密钥未设置。请在.env文件中设置OPENAI_API_KEY环境变量。"
            )
            
        self.client = AsyncOpenAI(
            api_key=api_key,
            organization=os.getenv("OPENAI_ORG_ID")
        )
        
        self.models = {
            "gpt-4": ModelInfo(
                name="gpt-4",
                max_tokens=8192,
                pricing={"input": 0.03, "output": 0.06}
            ),
            "gpt-4-turbo-preview": ModelInfo(
                name="gpt-4-turbo-preview",
                max_tokens=128000,
                pricing={"input": 0.01, "output": 0.03}
            ),
            "gpt-3.5-turbo": ModelInfo(
                name="gpt-3.5-turbo",
                max_tokens=4096,
                pricing={"input": 0.0005, "output": 0.0015}
            )
        }
    
    async def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return list(self.models.keys())
    
    async def get_model_info(self, model_name: str = None) -> ModelInfo:
        """获取模型信息"""
        if not model_name:
            model_name = "gpt-3.5-turbo"
        if model_name not in self.models:
            raise ValueError(f"未知的模型: {model_name}")
        return self.models[model_name]
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        **kwargs
    ) -> Dict:
        """聊天补全"""
        try:
            if not model:
                model = "gpt-3.5-turbo"
                
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            
            return {
                "content": response.choices[0].message.content,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        except Exception as e:
            raise ValueError(f"OpenAI API调用失败: {str(e)}")
        
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> CompletionResponse:
        """生成文本"""
        try:
            model = kwargs.get('model', 'gpt-3.5-turbo')
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            return CompletionResponse(
                text=response.choices[0].message.content,
                model=model,
                created_at=datetime.now(),
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )
        except Exception as e:
            raise ValueError(f"OpenAI API调用失败: {str(e)}")
    
    async def count_tokens(self, text: str) -> int:
        """计算文本的token数量"""
        # 使用简单的估算方法
        return len(text.split()) * 1.3
    
    async def validate_connection(self) -> bool:
        """验证API连接是否正常"""
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False 