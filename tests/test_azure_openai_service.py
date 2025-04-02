import pytest
from src.services.azure_openai_service import AzureOpenAIService
from src.services.base import Message
from src.utils.exceptions import APIKeyNotFoundError

@pytest.mark.asyncio
async def test_azure_openai_service_initialization():
    """测试Azure OpenAI服务初始化"""
    try:
        service = AzureOpenAIService()
        assert service is not None
        assert service.default_model is not None
    except APIKeyNotFoundError:
        pytest.skip("Azure OpenAI credentials not found")

@pytest.mark.asyncio
async def test_generate_text():
    """测试文本生成"""
    try:
        service = AzureOpenAIService()
        response = await service.generate_text(
            prompt="Hello, how are you?",
            temperature=0.7
        )
        assert response.text is not None
        assert response.model is not None
        assert response.prompt_tokens > 0
        assert response.completion_tokens > 0
        assert response.total_tokens > 0
    except APIKeyNotFoundError:
        pytest.skip("Azure OpenAI credentials not found")

@pytest.mark.asyncio
async def test_chat_complete():
    """测试聊天完成"""
    try:
        service = AzureOpenAIService()
        messages = [
            Message(role="user", content="What is the capital of France?")
        ]
        response = await service.chat_complete(
            messages=messages,
            temperature=0.7
        )
        assert response.text is not None
        assert "Paris" in response.text.lower()
        assert response.model is not None
    except APIKeyNotFoundError:
        pytest.skip("Azure OpenAI credentials not found")

@pytest.mark.asyncio
async def test_get_model_info():
    """测试获取模型信息"""
    try:
        service = AzureOpenAIService()
        info = await service.get_model_info()
        assert info.id is not None
        assert info.provider == "Azure OpenAI"
        assert info.pricing is not None
        assert info.max_tokens in [4096, 8192]  # 根据模型类型
    except APIKeyNotFoundError:
        pytest.skip("Azure OpenAI credentials not found")

@pytest.mark.asyncio
async def test_count_tokens():
    """测试token计数"""
    try:
        service = AzureOpenAIService()
        text = "Hello, this is a test message."
        token_count = await service.count_tokens(text)
        assert token_count > 0
        assert isinstance(token_count, (int, float))
    except APIKeyNotFoundError:
        pytest.skip("Azure OpenAI credentials not found")

@pytest.mark.asyncio
async def test_validate_connection():
    """测试API连接验证"""
    try:
        service = AzureOpenAIService()
        is_valid = await service.validate_connection()
        assert is_valid is True
    except APIKeyNotFoundError:
        pytest.skip("Azure OpenAI credentials not found") 