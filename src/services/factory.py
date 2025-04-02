from typing import Dict, Type
from .base import LLMService

class LLMServiceFactory:
    """LLM服务工厂"""
    
    _services: Dict[str, Type[LLMService]] = {}
    
    @classmethod
    def register(cls, provider: str):
        """注册服务"""
        def decorator(service_class: Type[LLMService]):
            cls._services[provider] = service_class
            return service_class
        return decorator
    
    @classmethod
    def get_service(cls, provider: str) -> LLMService:
        """获取服务实例"""
        if provider not in cls._services:
            raise ValueError(f"未知的服务提供商: {provider}")
        return cls._services[provider]()
    
    @classmethod
    def get_available_providers(cls) -> list:
        """获取可用的服务提供商列表"""
        return list(cls._services.keys()) 