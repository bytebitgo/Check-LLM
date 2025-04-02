import pytest
from src.services.anthropic_service import AnthropicService
from src.services.base import Message
from src.utils.exceptions import APIKeyNotFoundError

@pytest.mark.asyncio
async def test_anthropic_service_initialization():
    """测试Anthropic服务初始化"""
    try:
        service = AnthropicService()
        assert service is not None
        assert service.default_model == "claude-3-opus-20240229"
    except APIKeyNotFoundError:
        pytest.skip("Anthropic API key not found")

@pytest.mark.asyncio
async def test_generate_text():
    """测试文本生成"""
    try:
        service = AnthropicService()
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
        pytest.skip("Anthropic API key not found")

@pytest.mark.asyncio
async def test_chat_complete():
    """测试聊天完成"""
    try:
        service = AnthropicService()
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
        pytest.skip("Anthropic API key not found")

@pytest.mark.asyncio
async def test_get_model_info():
    """测试获取模型信息"""
    try:
        service = AnthropicService()
        info = await service.get_model_info()
        assert info.id == "claude-3-opus-20240229"
        assert info.provider == "Anthropic"
        assert info.pricing is not None
        assert info.max_tokens == 200000
    except APIKeyNotFoundError:
        pytest.skip("Anthropic API key not found")

@pytest.mark.asyncio
async def test_count_tokens():
    """测试token计数"""
    try:
        service = AnthropicService()
        text = "Hello, this is a test message."
        token_count = await service.count_tokens(text)
        assert token_count > 0
    except APIKeyNotFoundError:
        pytest.skip("Anthropic API key not found")

@pytest.mark.asyncio
async def test_validate_connection():
    """测试API连接验证"""
    try:
        service = AnthropicService()
        is_valid = await service.validate_connection()
        assert is_valid is True
    except APIKeyNotFoundError:
        pytest.skip("Anthropic API key not found") 