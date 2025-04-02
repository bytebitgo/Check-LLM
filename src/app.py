import os
import streamlit as st
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def init_session_state():
    """初始化会话状态"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_model' not in st.session_state:
        st.session_state.current_model = None

def main():
    # 页面配置
    st.set_page_config(
        page_title=os.getenv('APP_NAME', 'LLM测试工具'),
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 初始化会话状态
    init_session_state()
    
    # 侧边栏
    st.sidebar.title("LLM测试工具")
    page = st.sidebar.radio(
        "选择功能",
        ["对话测试", "性能评估", "批量测试", "历史记录"]
    )
    
    # 主页面
    if page == "对话测试":
        st.title("模型对话测试")
        st.write("选择模型并开始对话测试")
        
    elif page == "性能评估":
        st.title("模型性能评估")
        st.write("评估模型的性能指标")
        
    elif page == "批量测试":
        st.title("批量测试")
        st.write("进行批量测试并分析结果")
        
    else:  # 历史记录
        st.title("历史记录")
        st.write("查看历史测试记录")

if __name__ == "__main__":
    main() 