import os
from typing import List, Dict, Optional, AsyncGenerator, Union
from openai import AsyncAzureOpenAI
from datetime import datetime
from .base import LLMService, ModelInfo, CompletionResponse
from .factory import LLMServiceFactory

@LLMServiceFactory.register("azure-openai")
class AzureOpenAIService(LLMService):
    """Azure OpenAI服务"""
    
    def __init__(self):
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME")
        
        if not all([api_key, endpoint, deployment_name]):
            raise ValueError(
                "Azure OpenAI配置未完成。请在.env文件中设置以下环境变量：\n"
                "- AZURE_OPENAI_API_KEY\n"
                "- AZURE_OPENAI_ENDPOINT\n"
                "- AZURE_DEPLOYMENT_NAME"
            )
            
        self.client = AsyncAzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        
        self.deployment_name = deployment_name
        # 根据部署名称判断模型类型
        self.model_type = "gpt-4" if "gpt-4" in deployment_name.lower() else "gpt-35-turbo"
        
        self.models = {
            deployment_name: ModelInfo(
                name=deployment_name,
                max_tokens=8192 if self.model_type == "gpt-4" else 4096,
                pricing={
                    "input": 0.03 if self.model_type == "gpt-4" else 0.0005,
                    "output": 0.06 if self.model_type == "gpt-4" else 0.0015
                }
            )
        }
    
    async def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return list(self.models.keys())
    
    async def get_model_info(self, model_name: str = None) -> ModelInfo:
        """获取模型信息"""
        if not model_name:
            model_name = self.deployment_name
        if model_name not in self.models:
            raise ValueError(f"未知的模型: {model_name}")
        return self.models[model_name]
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        stream: bool = True,  # 默认使用流式输出
        **kwargs
    ) -> Union[Dict, AsyncGenerator[str, None]]:
        """聊天补全"""
        try:
            if not model:
                model = self.deployment_name
                
            # 移除Azure OpenAI不支持的参数
            supported_params = {
                "temperature",
                "max_tokens",
                "top_p",
                "frequency_penalty",
                "presence_penalty",
                "stop"
            }
            filtered_kwargs = {
                k: v for k, v in kwargs.items() 
                if k in supported_params
            }
            
            async def stream_response():
                full_content = ""
                start_time = datetime.now()
                
                response = await self.client.chat.completions.create(
                    model=self.deployment_name,  # 使用部署名称作为模型名称
                    messages=messages,
                    stream=True,
                    **filtered_kwargs
                )
                
                async for chunk in response:
                    try:
                        if (chunk.choices and 
                            chunk.choices[0].delta and 
                            hasattr(chunk.choices[0].delta, 'content') and 
                            chunk.choices[0].delta.content):
                            content = chunk.choices[0].delta.content
                            full_content += content
                            yield {
                                "type": "content",
                                "content": content
                            }
                    except (IndexError, AttributeError):
                        continue
                
                # 在流式响应结束后获取完整的响应以获取token统计
                full_response = await self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages,
                    stream=False,
                    **filtered_kwargs
                )
                
                end_time = datetime.now()
                yield {
                    "type": "stats",
                    "stats": {
                        "content": full_content,
                        "prompt_tokens": full_response.usage.prompt_tokens,
                        "completion_tokens": full_response.usage.completion_tokens,
                        "total_tokens": full_response.usage.total_tokens,
                        "response_time": (end_time - start_time).total_seconds()
                    }
                }
            
            # 流式输出
            if stream:
                return stream_response()
            
            # 非流式输出
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                stream=False,
                **filtered_kwargs
            )
            
            return {
                "content": response.choices[0].message.content,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
                
        except Exception as e:
            raise ValueError(f"Azure OpenAI API调用失败: {str(e)}")
        
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> CompletionResponse:
        """生成文本"""
        try:
            # 移除Azure OpenAI不支持的参数
            supported_params = {
                "temperature",
                "max_tokens",
                "top_p",
                "frequency_penalty",
                "presence_penalty",
                "stop"
            }
            filtered_kwargs = {
                k: v for k, v in kwargs.items() 
                if k in supported_params
            }
            
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **filtered_kwargs
            )
            
            return CompletionResponse(
                text=response.choices[0].message.content,
                model=self.deployment_name,
                created_at=datetime.now(),
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )
        except Exception as e:
            raise ValueError(f"Azure OpenAI API调用失败: {str(e)}")
    
    async def count_tokens(self, text: str) -> int:
        """计算文本的token数量"""
        # 使用简单的估算方法
        return len(text.split()) * 1.3
    
    async def validate_connection(self) -> bool:
        """验证API连接是否正常"""
        try:
            await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception:
            return False 