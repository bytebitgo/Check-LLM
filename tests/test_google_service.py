import pytest
from src.services.google_service import GoogleService
from src.services.base import Message
from src.utils.exceptions import APIKeyNotFoundError

@pytest.mark.asyncio
async def test_google_service_initialization():
    """测试Google服务初始化"""
    try:
        service = GoogleService()
        assert service is not None
        assert service.default_model == "gemini-pro"
    except APIKeyNotFoundError:
        pytest.skip("Google API key not found")

@pytest.mark.asyncio
async def test_generate_text():
    """测试文本生成"""
    try:
        service = GoogleService()
        response = await service.generate_text(
            prompt="Hello, how are you?",
            temperature=0.7
        )
        assert response.text is not None
        assert response.model == "gemini-pro"
        assert response.prompt_tokens > 0
        assert response.completion_tokens > 0
        assert response.total_tokens > 0
    except APIKeyNotFoundError:
        pytest.skip("Google API key not found")

@pytest.mark.asyncio
async def test_chat_complete():
    """测试聊天完成"""
    try:
        service = GoogleService()
        messages = [
            Message(role="user", content="What is the capital of France?")
        ]
        response = await service.chat_complete(
            messages=messages,
            temperature=0.7
        )
        assert response.text is not None
        assert "Paris" in response.text.lower()
        assert response.model == "gemini-pro"
    except APIKeyNotFoundError:
        pytest.skip("Google API key not found")

@pytest.mark.asyncio
async def test_get_model_info():
    """测试获取模型信息"""
    try:
        service = GoogleService()
        info = await service.get_model_info()
        assert info.id == "gemini-pro"
        assert info.provider == "Google"
        assert info.pricing is not None
        assert info.max_tokens == 30720
    except APIKeyNotFoundError:
        pytest.skip("Google API key not found")

@pytest.mark.asyncio
async def test_count_tokens():
    """测试token计数"""
    try:
        service = GoogleService()
        text = "Hello, this is a test message."
        token_count = await service.count_tokens(text)
        assert token_count > 0
        assert isinstance(token_count, (int, float))
    except APIKeyNotFoundError:
        pytest.skip("Google API key not found")

@pytest.mark.asyncio
async def test_validate_connection():
    """测试API连接验证"""
    try:
        service = GoogleService()
        is_valid = await service.validate_connection()
        assert is_valid is True
    except APIKeyNotFoundError:
        pytest.skip("Google API key not found") 