import os
from typing import List, Dict, Optional
from anthropic import AsyncAnthropic
from datetime import datetime
from .base import LLMService, ModelInfo, CompletionResponse
from .factory import LLMServiceFactory

@LLMServiceFactory.register("anthropic")
class AnthropicService(LLMService):
    """Anthropic服务"""
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key:
            raise ValueError(
                "Anthropic配置未完成。请在.env文件中设置ANTHROPIC_API_KEY。"
            )
            
        self.client = AsyncAnthropic(api_key=api_key)
        
        self.models = {
            "claude-3-opus": ModelInfo(
                name="claude-3-opus",
                max_tokens=200000,
                pricing={"input": 0.015, "output": 0.075}
            ),
            "claude-3-sonnet": ModelInfo(
                name="claude-3-sonnet",
                max_tokens=200000,
                pricing={"input": 0.003, "output": 0.015}
            ),
            "claude-3-haiku": ModelInfo(
                name="claude-3-haiku",
                max_tokens=200000,
                pricing={"input": 0.0025, "output": 0.00125}
            )
        }
    
    async def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return list(self.models.keys())
    
    async def get_model_info(self, model_name: str = None) -> ModelInfo:
        """获取模型信息"""
        if not model_name:
            model_name = "claude-3-sonnet"
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
                model = "claude-3-sonnet"
                
            # 将消息格式转换为Anthropic格式
            formatted_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    formatted_messages.append({
                        "role": "user",
                        "content": msg["content"]
                    })
                elif msg["role"] == "assistant":
                    formatted_messages.append({
                        "role": "assistant",
                        "content": msg["content"]
                    })
            
            response = await self.client.messages.create(
                model=model,
                messages=formatted_messages,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7)
            )
            
            return {
                "content": response.content[0].text,
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        except Exception as e:
            raise ValueError(f"Anthropic API调用失败: {str(e)}")
        
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> CompletionResponse:
        """生成文本"""
        try:
            model = kwargs.get('model', 'claude-3-sonnet')
            response = await self.client.messages.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return CompletionResponse(
                text=response.content[0].text,
                model=model,
                created_at=datetime.now(),
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens
            )
        except Exception as e:
            raise ValueError(f"Anthropic API调用失败: {str(e)}")
    
    async def count_tokens(self, text: str) -> int:
        """计算文本的token数量"""
        # 使用简单的估算方法
        return len(text.split()) * 1.3
    
    async def validate_connection(self) -> bool:
        """验证API连接是否正常"""
        try:
            await self.client.messages.create(
                model="claude-3-haiku",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception:
            return False 