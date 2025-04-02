import streamlit as st
import pandas as pd
import plotly.express as px
from typing import List, Dict
from datetime import datetime

def display_response_time_chart(data: List[Dict]):
    """显示响应时间图表"""
    if not data:
        return
    
    df = pd.DataFrame(data)
    fig = px.box(
        df,
        x="model",
        y="response_time",
        color="provider",
        title="模型响应时间对比",
        labels={
            "model": "模型",
            "response_time": "响应时间 (秒)",
            "provider": "服务提供商"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

def display_token_usage_chart(data: List[Dict]):
    """显示Token使用量图表"""
    if not data:
        return
    
    df = pd.DataFrame(data)
    fig = px.bar(
        df,
        x="model",
        y=["prompt_tokens", "completion_tokens"],
        color="provider",
        title="Token使用量统计",
        barmode="group",
        labels={
            "model": "模型",
            "value": "Token数量",
            "provider": "服务提供商",
            "variable": "Token类型"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

def display_cost_analysis(data: List[Dict]):
    """显示成本分析"""
    if not data:
        return
    
    df = pd.DataFrame(data)
    total_cost = df["cost"].sum()
    avg_cost = df["cost"].mean()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("总成本 (USD)", f"${total_cost:.4f}")
    
    with col2:
        st.metric("平均成本 (USD)", f"${avg_cost:.4f}")
    
    with col3:
        st.metric(
            "每千字成本 (USD)",
            f"${(total_cost / df['total_tokens'].sum() * 1000):.4f}"
        )
    
    # 成本趋势图
    fig = px.line(
        df,
        x="timestamp",
        y="cost",
        color="provider",
        title="成本趋势",
        labels={
            "timestamp": "时间",
            "cost": "成本 (USD)",
            "provider": "服务提供商"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

def performance_dashboard(data: List[Dict]):
    """性能统计仪表板"""
    if not data:
        st.info("暂无性能数据")
        return
    
    # 创建选项卡
    tab1, tab2, tab3 = st.tabs([
        "响应时间分析",
        "Token使用统计",
        "成本分析"
    ])
    
    with tab1:
        display_response_time_chart(data)
        
        # 显示详细统计
        df = pd.DataFrame(data)
        st.dataframe(
            df.groupby(["provider", "model"])["response_time"].agg([
                "count",
                "mean",
                "std",
                "min",
                "max"
            ]).round(3),
            use_container_width=True
        )
    
    with tab2:
        display_token_usage_chart(data)
        
        # Token使用量统计
        token_stats = df.groupby(["provider", "model"]).agg({
            "prompt_tokens": ["sum", "mean"],
            "completion_tokens": ["sum", "mean"],
            "total_tokens": ["sum", "mean"]
        }).round(2)
        st.dataframe(token_stats, use_container_width=True)
    
    with tab3:
        display_cost_analysis(data)
        
        # 成本明细
        cost_details = df.groupby(["provider", "model"]).agg({
            "cost": ["sum", "mean", "count"]
        }).round(4)
        st.dataframe(cost_details, use_container_width=True)

def add_performance_record(
    provider: str,
    model: str,
    response_time: float,
    prompt_tokens: int,
    completion_tokens: int,
    cost: float
):
    """添加性能记录
    
    Args:
        provider: 服务提供商
        model: 模型名称
        response_time: 响应时间（秒）
        prompt_tokens: 输入token数
        completion_tokens: 输出token数
        cost: 成本（美元）
    """
    if "performance_records" not in st.session_state:
        st.session_state.performance_records = []
    
    record = {
        "timestamp": datetime.now(),
        "provider": provider,
        "model": model,
        "response_time": response_time,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "cost": cost
    }
    
    st.session_state.performance_records.append(record) 