import streamlit as st
from typing import Tuple
from services import LLMServiceFactory

async def model_selector() -> Tuple[str, str]:
    """模型选择器组件
    
    Returns:
        Tuple[str, str]: (provider, model_name)
    """
    # 获取可用的服务提供商
    providers = LLMServiceFactory.get_available_providers()
    
    # 创建两列布局
    col1, col2 = st.columns(2)
    
    with col1:
        provider = st.selectbox(
            "选择服务提供商",
            options=providers,
            format_func=lambda x: {
                "openai": "OpenAI",
                "azure-openai": "Azure OpenAI",
                "anthropic": "Anthropic",
                "google": "Google",
                "huggingface": "Hugging Face"
            }.get(x, x.title())
        )
    
    # 获取选中服务商的可用模型
    if provider:
        service = LLMServiceFactory.get_service(provider)
        models = await service.get_available_models()
        
        with col2:
            model = st.selectbox(
                "选择模型",
                options=models,
                format_func=lambda x: x.split("/")[-1] if "/" in x else x
            )
    else:
        model = None
    
    return provider, model

def model_parameters(provider: str = None) -> dict:
    """模型参数设置
    
    Args:
        provider: 服务提供商
    
    Returns:
        dict: 模型参数
    """
    parameters = {}
    
    with st.expander("模型参数设置", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            parameters["temperature"] = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=0.7,
                step=0.1,
                help="控制输出的随机性，值越大输出越随机"
            )
            
            parameters["max_tokens"] = st.number_input(
                "最大Token数",
                min_value=1,
                max_value=32000,
                value=2000,
                help="生成文本的最大长度"
            )
            
        with col2:
            # OpenAI和Azure OpenAI支持top_p
            if provider in ["openai", "azure-openai"]:
                parameters["top_p"] = st.slider(
                    "Top P",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.95,
                    step=0.05,
                    help="控制输出的多样性"
                )
            
            # 只有OpenAI支持top_k
            if provider == "openai":
                parameters["top_k"] = st.number_input(
                    "Top K",
                    min_value=1,
                    max_value=100,
                    value=40,
                    help="控制每一步生成时考虑的词数量"
                )
            
            # Anthropic特有的参数
            if provider == "anthropic":
                parameters["stop_sequences"] = st.text_input(
                    "停止序列",
                    value="",
                    help="当生成的文本包含这些序列时停止（用逗号分隔）"
                )
                if parameters["stop_sequences"]:
                    parameters["stop_sequences"] = [
                        s.strip() 
                        for s in parameters["stop_sequences"].split(",")
                    ]
                else:
                    del parameters["stop_sequences"]
    
    return parameters 