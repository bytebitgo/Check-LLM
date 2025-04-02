import streamlit as st
import pandas as pd
import plotly.express as px

def stats_page():
    """统计页面"""
    st.title("性能统计")
    
    # 检查是否有性能记录
    if not st.session_state.get("performance_records", []):
        st.warning("暂无性能数据。请先进行一些对话测试。")
        return
        
    # 转换数据为DataFrame
    df = pd.DataFrame(st.session_state.performance_records)
    
    # 显示性能仪表板
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "平均响应时间",
            f"{df['response_time'].mean():.2f}秒",
            f"{df['response_time'].std():.2f}秒"
        )
    
    with col2:
        st.metric(
            "平均Token使用量",
            f"{df['total_tokens'].mean():.0f}",
            f"{df['total_tokens'].std():.0f}"
        )
    
    with col3:
        st.metric(
            "总成本",
            f"${df['cost'].sum():.4f}",
            f"${df['cost'].mean():.4f}/次"
        )
    
    # 显示详细图表
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("响应时间分析")
        fig = px.box(
            df,
            x="model",
            y="response_time",
            color="provider",
            title="各模型响应时间分布"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Token使用分析")
        fig = px.bar(
            df,
            x="model",
            y=["prompt_tokens", "completion_tokens"],
            title="Token使用情况",
            barmode="group"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    st.subheader("成本分析")
    fig = px.line(
        df,
        x=df.index,
        y="cost",
        color="model",
        title="成本趋势"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 显示原始数据
    st.subheader("详细数据")
    st.dataframe(
        df.style.format({
            "response_time": "{:.2f}秒",
            "cost": "${:.4f}"
        })
    ) 