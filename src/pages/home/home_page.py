import streamlit as st

def home_page():
    """主页"""
    st.title("LLM测试工具")
    
    st.markdown("""
    ## 欢迎使用LLM测试工具
    
    这是一个用于测试和评估各种大语言模型(LLM)服务的工具。
    
    ### 主要功能
    
    - **模型对话**: 与不同的LLM服务进行对话测试
    - **性能统计**: 查看响应时间、Token使用量和成本分析
    - **多服务支持**: 支持OpenAI、Azure OpenAI、Anthropic、Google等多个服务商
    
    ### 使用说明
    
    1. 在侧边栏选择要测试的服务商和模型
    2. 配置模型参数（温度、最大Token等）
    3. 开始对话测试
    4. 在性能统计页面查看分析结果
    
    ### 注意事项
    
    - 请确保已正确配置相关服务的API密钥
    - 所有的对话记录和性能数据仅保存在当前会话中
    - 建议在正式使用前先进行小规模测试
    """)
    
    # 显示版本信息
    st.sidebar.markdown("---")
    st.sidebar.markdown("版本: v0.1.0")
    st.sidebar.markdown("[查看更新日志](https://github.com/yourusername/llm-test-tool/blob/main/CHANGELOG.md)") 