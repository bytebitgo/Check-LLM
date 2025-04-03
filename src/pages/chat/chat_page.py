import os
import streamlit as st
import asyncio
from components.model_selector import model_selector, model_parameters
from services import LLMServiceFactory
from services.base import Message
from services.openai_service import OpenAIService
from services.azure_openai_service import AzureOpenAIService
from services.anthropic_service import AnthropicService

def check_service_config(service_name: str) -> bool:
    """检查服务配置是否完整"""
    if service_name == "OpenAI":
        return bool(os.getenv("OPENAI_API_KEY"))
    elif service_name == "Azure OpenAI":
        # 检查是否有任何Azure OpenAI配置组
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                current_group = None
                has_valid_config = False
                current_config = {}
                
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('## '):
                        # 检查上一个配置组是否有效
                        if current_config and all(key in current_config for key in [
                            'AZURE_OPENAI_API_KEY',
                            'AZURE_OPENAI_ENDPOINT',
                            'AZURE_DEPLOYMENT_NAME'
                        ]):
                            has_valid_config = True
                            break
                        current_group = line[3:].strip()
                        current_config = {}
                        continue
                    if line.startswith('#'):
                        continue
                    if '=' in line and current_group:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if key.startswith('AZURE_') and value and value != 'your_azure_openai_api_key':
                            current_config[key] = value
                
                # 检查最后一个配置组
                if current_config and all(key in current_config for key in [
                    'AZURE_OPENAI_API_KEY',
                    'AZURE_OPENAI_ENDPOINT',
                    'AZURE_DEPLOYMENT_NAME'
                ]):
                    has_valid_config = True
                
                return has_valid_config
        return False
    elif service_name == "Anthropic":
        return bool(os.getenv("ANTHROPIC_API_KEY"))
    return False

async def get_service_provider():
    """获取服务提供商"""
    # 初始化session state
    if 'provider' not in st.session_state:
        st.session_state.provider = None
    if 'model' not in st.session_state:
        st.session_state.model = None
    
    providers = {
        "openai": "OpenAI",
        "azure-openai": "Azure OpenAI",
        "anthropic": "Anthropic",
        "google": "Google"
    }
    
    # 获取已配置的服务提供商
    available_providers = {
        key: name for key, name in providers.items()
        if check_service_config(name)
    }
    
    if not available_providers:
        st.error("未找到任何可用的服务提供商，请先在配置管理页面设置相关API密钥")
        return None, None
    
    # 选择服务提供商
    provider = st.selectbox(
        "选择服务提供商",
        options=list(available_providers.keys()),
        format_func=lambda x: available_providers[x]
    )
    
    if not provider:
        return None, None
    
    # 实例化服务
    try:
        service = LLMServiceFactory.get_service(provider)
        models = await service.get_available_models()
        
        if not models:
            st.error(f"{providers[provider]} 未获取到可用模型，请检查配置是否正确")
            return None, None
        
        model = st.selectbox(
            "选择模型",
            options=models,
            format_func=lambda x: x.split(" - ")[-1] if " - " in x else x
        )
        
        return provider, model
        
    except Exception as e:
        st.error(f"初始化 {providers[provider]} 服务失败: {str(e)}")
        return None, None

async def chat_page():
    """聊天页面"""
    st.title("模型对话测试")
    
    try:
        # 初始化session state
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "performance_records" not in st.session_state:
            st.session_state.performance_records = []
        
        # 侧边栏配置
        with st.sidebar:
            st.header("模型配置")
            provider, model = await get_service_provider()
            
            if not provider or not model:
                return
            
            # 清空聊天按钮
            if st.button("清空聊天记录", type="secondary"):
                st.session_state.messages = []
                st.session_state.performance_records = []  # 同时清空性能记录
                st.rerun()
        
        # 显示聊天历史
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # 用户输入
        if prompt := st.chat_input():
            # 添加用户消息
            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # 调用API
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                stats_placeholder = st.empty()
                full_response = ""
                
                try:
                    message_placeholder.markdown("🤔 思考中...")
                    
                    # 获取流式响应
                    response_generator = await LLMServiceFactory.get_service(provider).chat_completion(
                        messages=[
                            {"role": msg["role"], "content": msg["content"]}
                            for msg in st.session_state.messages
                        ],
                        model=model,
                        stream=True
                    )
                    
                    # 处理流式响应
                    async for chunk in response_generator:
                        if chunk["type"] == "content":
                            full_response += chunk["content"]
                            message_placeholder.markdown(full_response + "▌")
                        elif chunk["type"] == "stats":
                            # 显示最终响应（不带光标）
                            message_placeholder.markdown(full_response)
                            
                            # 添加助手消息到历史记录
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": full_response
                            })
                            
                            # 获取模型信息以计算成本
                            model_info = await LLMServiceFactory.get_service(provider).get_model_info(model)
                            
                            if model_info and model_info.pricing:
                                # 计算成本
                                prompt_cost = (
                                    model_info.pricing["input"] *
                                    chunk["stats"]["prompt_tokens"] / 1000
                                )
                                completion_cost = (
                                    model_info.pricing["output"] *
                                    chunk["stats"]["completion_tokens"] / 1000
                                )
                                total_cost = prompt_cost + completion_cost
                                
                                # 显示统计信息
                                stats_placeholder.caption(
                                    f"响应时间: {chunk['stats']['response_time']:.2f}秒 | "
                                    f"输入tokens: {chunk['stats']['prompt_tokens']} | "
                                    f"输出tokens: {chunk['stats']['completion_tokens']} | "
                                    f"总tokens: {chunk['stats']['total_tokens']} | "
                                    f"成本: ${total_cost:.4f}"
                                )
                                
                                # 添加性能记录
                                performance_record = {
                                    "provider": provider,
                                    "model": model,
                                    "response_time": chunk["stats"]["response_time"],
                                    "prompt_tokens": chunk["stats"]["prompt_tokens"],
                                    "completion_tokens": chunk["stats"]["completion_tokens"],
                                    "total_tokens": chunk["stats"]["total_tokens"],
                                    "cost": total_cost
                                }
                                
                                if "performance_records" not in st.session_state:
                                    st.session_state.performance_records = []
                                st.session_state.performance_records.append(performance_record)
                    
                    # 检查是否有响应
                    if not full_response:
                        message_placeholder.error("模型没有生成任何响应")
                        if st.session_state.messages:
                            st.session_state.messages.pop()  # 移除用户消息
                        return
                    
                except Exception as e:
                    error_msg = str(e)
                    if "未收到模型响应" in error_msg:
                        message_placeholder.error("模型没有生成响应，请重试")
                    else:
                        message_placeholder.error(f"生成响应时出错: {error_msg}")
                    
                    # 移除用户消息（仅在完全失败时）
                    if not full_response and st.session_state.messages:
                        st.session_state.messages.pop()
                
    except Exception as e:
        st.error(f"页面加载出错: {str(e)}") 