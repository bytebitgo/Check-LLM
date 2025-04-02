import pytest
from src.services.openai_service import OpenAIService
from src.services.base import Message
from src.utils.exceptions import APIKeyNotFoundError

@pytest.mark.asyncio
async def test_openai_service_initialization():
    """测试OpenAI服务初始化"""
    try:
        service = OpenAIService()
        assert service is not None
        assert service.default_model == "gpt-4"
    except APIKeyNotFoundError:
        pytest.skip("OpenAI API key not found")

@pytest.mark.asyncio
async def test_generate_text():
    """测试文本生成"""
    try:
        service = OpenAIService()
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
        pytest.skip("OpenAI API key not found")

@pytest.mark.asyncio
async def test_chat_complete():
    """测试聊天完成"""
    try:
        service = OpenAIService()
        messages = [
            Message(role="user", content="What is the capital of France?")
        ]
        response = await service.chat_complete(
            messages=messages,
            temperature=0.7
        )
        assert response.text is not None
        assert "Paris" in response.text
        assert response.model is not None
    except APIKeyNotFoundError:
        pytest.skip("OpenAI API key not found")

@pytest.mark.asyncio
async def test_get_model_info():
    """测试获取模型信息"""
    try:
        service = OpenAIService()
        info = await service.get_model_info()
        assert info.id == "gpt-4"
        assert info.provider == "OpenAI"
        assert info.pricing is not None
    except APIKeyNotFoundError:
        pytest.skip("OpenAI API key not found")

@pytest.mark.asyncio
async def test_validate_connection():
    """测试API连接验证"""
    try:
        service = OpenAIService()
        is_valid = await service.validate_connection()
        assert is_valid is True
    except APIKeyNotFoundError:
        pytest.skip("OpenAI API key not found") 