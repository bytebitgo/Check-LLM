import os
from typing import List, Dict, Optional, AsyncGenerator, Union
from openai import AsyncAzureOpenAI
from datetime import datetime
import tiktoken
from .base import LLMService, ModelInfo, CompletionResponse
from .factory import LLMServiceFactory

@LLMServiceFactory.register("azure-openai")
class AzureOpenAIService(LLMService):
    """Azure OpenAI服务"""
    
    def __init__(self):
        # 加载所有 Azure OpenAI 配置
        self.configs = self._load_azure_configs()
        if not self.configs:
            raise ValueError(
                "Azure OpenAI配置未完成。请在配置管理页面添加配置，每个配置组需要包含：\n"
                "- AZURE_OPENAI_API_KEY\n"
                "- AZURE_OPENAI_ENDPOINT\n"
                "- AZURE_DEPLOYMENT_NAME\n"
                "- AZURE_OPENAI_API_VERSION（可选）"
            )
        
        # 初始化所有配置的客户端和模型信息
        self.clients = {}
        self.models = {}
        self.encodings = {}
        
        for config_name, config in self.configs.items():
            try:
                client = AsyncAzureOpenAI(
                    api_key=config["api_key"],
                    api_version=config.get("api_version", "2024-02-15-preview"),
                    azure_endpoint=config["endpoint"]
                )
                
                deployment_name = config["deployment_name"]
                model_type = "gpt-4" if "gpt-4" in deployment_name.lower() else "gpt-35-turbo"
                
                self.clients[config_name] = client
                self.models[config_name] = {
                    deployment_name: ModelInfo(
                        name=f"{config_name} - {deployment_name}",
                        max_tokens=8192 if model_type == "gpt-4" else 4096,
                        pricing={
                            "input": 0.03 if model_type == "gpt-4" else 0.0005,
                            "output": 0.06 if model_type == "gpt-4" else 0.0015
                        }
                    )
                }
                
                # 初始化 tiktoken 编码器
                self.encodings[config_name] = tiktoken.get_encoding("cl100k_base")
                
            except Exception as e:
                st.warning(f"初始化配置 '{config_name}' 失败: {str(e)}")
    
    def _load_azure_configs(self):
        """从环境变量加载所有 Azure OpenAI 配置"""
        configs = {}
        
        # 获取所有环境变量
        env_vars = {}
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                current_group = None
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('## '):
                        current_group = line[3:].strip()
                        continue
                    if line.startswith('#'):
                        continue
                    if '=' in line and current_group:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        if key.startswith('AZURE_'):
                            if current_group not in env_vars:
                                env_vars[current_group] = {}
                            env_vars[current_group][key] = value.strip()
        
        # 解析配置
        for group, vars in env_vars.items():
            if all(key in vars for key in ['AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_ENDPOINT', 'AZURE_DEPLOYMENT_NAME']):
                configs[group] = {
                    "api_key": vars['AZURE_OPENAI_API_KEY'],
                    "endpoint": vars['AZURE_OPENAI_ENDPOINT'],
                    "deployment_name": vars['AZURE_DEPLOYMENT_NAME'],
                    "api_version": vars.get('AZURE_OPENAI_API_VERSION', "2024-02-15-preview")
                }
        
        return configs
    
    async def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        all_models = []
        for config_name, models in self.models.items():
            all_models.extend([f"{config_name} - {model}" for model in models.keys()])
        return all_models
    
    async def get_model_info(self, model_name: str = None) -> ModelInfo:
        """获取模型信息"""
        if not model_name:
            # 返回第一个可用的模型信息
            for models in self.models.values():
                if models:
                    return next(iter(models.values()))
            raise ValueError("没有可用的模型")
        
        # 解析配置名称和模型名称
        config_name, deployment_name = model_name.split(" - ", 1)
        if config_name not in self.models or deployment_name not in self.models[config_name]:
            raise ValueError(f"未知的模型: {model_name}")
        return self.models[config_name][deployment_name]
    
    def count_message_tokens(self, messages: List[Dict[str, str]], config_name: str) -> int:
        """使用 tiktoken 计算消息的 token 数量"""
        encoding = self.encodings[config_name]
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # 每个消息都有一个系统级别的格式标记
            for key, value in message.items():
                num_tokens += len(encoding.encode(str(value)))
                if key == "name":  # 如果消息中包含名字
                    num_tokens += -1  # 名字的 token 计数规则略有不同
        num_tokens += 2  # 对话的结束标记
        return num_tokens

    def count_completion_tokens(self, text: str, config_name: str) -> int:
        """使用 tiktoken 计算完成响应的 token 数量"""
        return len(self.encodings[config_name].encode(text))
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        stream: bool = True,
        **kwargs
    ) -> Union[Dict, AsyncGenerator[str, None]]:
        """聊天补全"""
        try:
            if not model:
                # 使用第一个可用的模型
                model = await self.get_available_models()[0]
            
            # 解析配置名称和部署名称
            config_name, deployment_name = model.split(" - ", 1)
            if config_name not in self.clients:
                raise ValueError(f"未知的配置: {config_name}")
            
            client = self.clients[config_name]
            
            # 计算输入消息的 token 数量
            input_tokens = self.count_message_tokens(messages, config_name)
            
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
                
                response = await client.chat.completions.create(
                    model=deployment_name,
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
                
                # 计算完成响应的 token 数量
                completion_tokens = self.count_completion_tokens(full_content, config_name)
                total_tokens = input_tokens + completion_tokens
                
                end_time = datetime.now()
                yield {
                    "type": "stats",
                    "stats": {
                        "content": full_content,
                        "prompt_tokens": input_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens,
                        "response_time": (end_time - start_time).total_seconds()
                    }
                }
            
            # 流式输出
            if stream:
                return stream_response()
            
            # 非流式输出
            response = await client.chat.completions.create(
                model=deployment_name,
                messages=messages,
                stream=False,
                **filtered_kwargs
            )
            
            completion_tokens = self.count_completion_tokens(response.choices[0].message.content, config_name)
            
            return {
                "content": response.choices[0].message.content,
                "prompt_tokens": input_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": input_tokens + completion_tokens
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