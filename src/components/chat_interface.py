import streamlit as st
from typing import List, Optional
import time
from ..services import Message, LLMServiceFactory

def init_chat_state():
    """初始化聊天状态"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_provider" not in st.session_state:
        st.session_state.current_provider = None
    if "current_model" not in st.session_state:
        st.session_state.current_model = None

def display_message(message: Message, is_user: bool = False):
    """显示聊天消息"""
    with st.chat_message("user" if is_user else "assistant"):
        st.markdown(message.content)

def display_chat_history():
    """显示聊天历史"""
    for message in st.session_state.messages:
        display_message(
            message,
            is_user=(message.role == "user")
        )

async def process_message(
    provider: str,
    model: str,
    content: str,
    parameters: dict
) -> Optional[str]:
    """处理用户消息
    
    Args:
        provider: 服务提供商
        model: 模型名称
        content: 消息内容
        parameters: 模型参数
    
    Returns:
        Optional[str]: 响应文本
    """
    try:
        # 获取服务实例
        service = LLMServiceFactory.get_service(provider)
        
        # 准备消息列表
        messages = [
            Message(role=msg.role, content=msg.content)
            for msg in st.session_state.messages
        ]
        messages.append(Message(role="user", content=content))
        
        # 显示生成中状态
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🤔 思考中...")
            
            # 记录开始时间
            start_time = time.time()
            
            # 调用API
            response = await service.chat_complete(
                messages=messages,
                model=model,
                **parameters
            )
            
            # 计算响应时间
            response_time = time.time() - start_time
            
            # 更新显示
            message_placeholder.markdown(response.text)
            
            # 显示统计信息
            st.caption(f"""
            响应时间: {response_time:.2f}秒 | 
            输入tokens: {response.prompt_tokens} | 
            输出tokens: {response.completion_tokens} | 
            总tokens: {response.total_tokens}
            """)
        
        return response.text
        
    except Exception as e:
        st.error(f"生成回复时出错: {str(e)}")
        return None

def chat_interface():
    """聊天界面组件"""
    # 初始化状态
    init_chat_state()
    
    # 显示聊天历史
    display_chat_history()
    
    # 输入框
    if prompt := st.chat_input("输入您的消息..."):
        # 添加用户消息
        user_message = Message(role="user", content=prompt)
        st.session_state.messages.append(user_message)
        display_message(user_message, is_user=True)
        
        return prompt
    
    return None 