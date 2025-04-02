class LLMServiceError(Exception):
    """LLM服务相关的异常基类"""
    pass

class APIKeyNotFoundError(LLMServiceError):
    """API密钥未找到异常"""
    pass

class ModelNotFoundError(LLMServiceError):
    """模型未找到异常"""
    pass

class RateLimitError(LLMServiceError):
    """API速率限制异常"""
    pass

class TokenLimitError(LLMServiceError):
    """Token数量超限异常"""
    pass

class InvalidRequestError(LLMServiceError):
    """无效请求异常"""
    pass 