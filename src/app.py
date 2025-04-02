import os
import asyncio
import streamlit as st
from dotenv import load_dotenv
from pages.home.home_page import home_page
from pages.chat.chat_page import chat_page
from pages.stats.stats_page import stats_page
from pages.config.config_page import config_page, get_env_path

# 加载环境变量
def load_environment():
    env_path = get_env_path()
    if env_path and os.path.exists(env_path):
        load_dotenv(env_path)
        st.sidebar.success(f"已加载配置文件: {env_path}")
    else:
        st.sidebar.error("未找到配置文件")

async def main():
    """主函数"""
    # 设置页面配置
    st.set_page_config(
        page_title="LLM测试工具",
        page_icon="🤖",
        layout="wide"
    )
    
    # 加载环境变量
    load_environment()
    
    # 初始化session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # 侧边栏导航
    pages = {
        "首页": home_page,
        "对话": chat_page,
        "统计": stats_page,
        "配置管理": config_page
    }
    
    page = st.sidebar.selectbox("导航", list(pages.keys()))
    
    # 根据选择显示页面
    if page == "对话":
        await pages[page]()
    else:
        pages[page]()

if __name__ == "__main__":
    asyncio.run(main()) 