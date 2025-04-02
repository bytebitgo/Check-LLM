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
        return all([
            os.getenv("AZURE_OPENAI_API_KEY"),
            os.getenv("AZURE_OPENAI_ENDPOINT"),
            os.getenv("AZURE_DEPLOYMENT_NAME")
        ])
    elif service_name == "Anthropic":
        return bool(os.getenv("ANTHROPIC_API_KEY"))
    return False

async def get_service_provider():
    """获取服务提供商"""
    providers = {
        "OpenAI": OpenAIService,
        "Azure OpenAI": AzureOpenAIService,
        "Anthropic": AnthropicService
    }
    
    # 获取已配置的服务提供商
    available_providers = {
        name: cls for name, cls in providers.items()
        if check_service_config(name)
    }
    
    if not available_providers:
        st.error("未找到任何可用的服务提供商，请先在配置管理页面设置相关API密钥")
        return None, None
    
    # 选择服务提供商
    provider_name = st.selectbox(
        "选择服务提供商",
        options=list(available_providers.keys())
    )
    
    if not provider_name:
        return None, None
    
    # 实例化服务
    try:
        service = available_providers[provider_name]()
        models = await service.get_available_models()
        
        if not models:
            st.error(f"{provider_name} 未获取到可用模型，请检查配置是否正确")
            return None, None
        
        model = st.selectbox("选择模型", options=models)
        return service, model
        
    except Exception as e:
        st.error(f"初始化 {provider_name} 服务失败: {str(e)}")
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
                    response_generator = await provider.chat_completion(
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
                            model_info = await provider.get_model_info(model)
                            
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
                                    "provider": provider.__class__.__name__,
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