from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel

class Message(BaseModel):
    """聊天消息模型"""
    role: str
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    
class CompletionResponse(BaseModel):
    """补全响应"""
    text: str
    model: str
    created_at: datetime
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
class ModelInfo(BaseModel):
    """模型信息"""
    name: str
    max_tokens: int
    pricing: Optional[Dict[str, float]] = None  # input和output的价格（每1k tokens）

class LLMService(ABC):
    """LLM服务基类"""
    
    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        pass
        
    @abstractmethod
    async def get_model_info(self, model_name: str = None) -> ModelInfo:
        """获取模型信息"""
        pass
        
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        **kwargs
    ) -> Dict:
        """聊天补全"""
        pass
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> CompletionResponse:
        """生成文本"""
        pass
    
    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """计算文本的token数量"""
        pass
    
    @abstractmethod
    async def validate_connection(self) -> bool:
        """验证API连接是否正常"""
        pass 