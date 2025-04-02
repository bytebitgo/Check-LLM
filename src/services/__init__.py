"""
LLM服务模块
"""

from .base import LLMService, ModelInfo, CompletionResponse
from .factory import LLMServiceFactory

# 导入所有服务实现，这样它们会被注册到工厂中
from .openai_service import OpenAIService
from .azure_openai_service import AzureOpenAIService
from .anthropic_service import AnthropicService

__all__ = [
    'LLMService',
    'ModelInfo',
    'CompletionResponse',
    'LLMServiceFactory',
    'OpenAIService',
    'AzureOpenAIService',
    'AnthropicService'
] 