import os
import streamlit as st
from typing import Dict
import json

def get_project_root():
    """获取项目根目录"""
    current_path = os.path.abspath(__file__)
    # 从当前文件位置向上查找，直到找到包含 src 目录的目录
    while current_path != '/':
        if os.path.basename(os.path.dirname(current_path)) == 'src':
            return os.path.dirname(os.path.dirname(current_path))
        current_path = os.path.dirname(current_path)
    # 如果找不到，返回当前文件所在的目录的上两级目录
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_env_path():
    """获取环境变量文件路径"""
    # 总是返回项目根目录下的 .env 文件路径
    root_dir = get_project_root()
    return os.path.join(root_dir, '.env')

def load_env_config() -> Dict[str, str]:
    """加载环境变量配置"""
    config = {}
    env_path = get_env_path()
    
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            current_section = None
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    if line.startswith('#'):
                        current_section = line[1:].strip()
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = {
                        'value': value.strip(),
                        'section': current_section
                    }
    
    # 显示当前使用的配置文件路径
    st.sidebar.info(f"当前配置文件: {env_path}")
    return config

def save_env_config(config: Dict[str, Dict[str, str]]):
    """保存环境变量配置"""
    env_path = get_env_path()
    
    # 确保目录存在
    os.makedirs(os.path.dirname(env_path), exist_ok=True)
    
    # 按section分组
    sections = {}
    for key, data in config.items():
        section = data['section']
        if section not in sections:
            sections[section] = []
        sections[section].append((key, data['value']))
    
    # 写入文件
    with open(env_path, 'w', encoding='utf-8') as f:
        for section, items in sections.items():
            f.write(f"# {section}\n")
            for key, value in items:
                f.write(f"{key}={value}\n")
            f.write("\n")

def config_page():
    """配置管理页面"""
    st.title("配置管理")
    
    # 初始化session state
    if 'env_config' not in st.session_state:
        st.session_state.env_config = load_env_config()
    if 'show_values' not in st.session_state:
        st.session_state.show_values = {}
    
    # 添加新配置的表单
    with st.expander("添加新配置", expanded=False):
        with st.form("add_config"):
            sections = sorted(set(
                data['section'] for data in st.session_state.env_config.values()
                if data['section']
            ))
            
            col1, col2 = st.columns(2)
            with col1:
                new_section = st.selectbox(
                    "配置分类",
                    options=["新建分类"] + sections
                )
                
                if new_section == "新建分类":
                    new_section = st.text_input("输入新分类名称")
            
            with col2:
                new_key = st.text_input("配置键名")
                new_value = st.text_input("配置值", type="password")
            
            if st.form_submit_button("添加"):
                if new_section and new_key:
                    st.session_state.env_config[new_key] = {
                        'value': new_value,
                        'section': new_section
                    }
                    save_env_config(st.session_state.env_config)
                    st.success(f"已添加配置: {new_key}")
                    st.rerun()
    
    # 显示和编辑现有配置
    if st.session_state.env_config:
        # 按section分组显示
        sections = {}
        for key, data in st.session_state.env_config.items():
            section = data['section']
            if section not in sections:
                sections[section] = []
            sections[section].append((key, data))
        
        for section, items in sorted(sections.items()):
            st.subheader(section)
            for key, data in sorted(items):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                # 初始化显示状态
                if key not in st.session_state.show_values:
                    st.session_state.show_values[key] = False
                
                with col1:
                    # 根据显示状态决定是否隐藏值
                    input_type = "default" if st.session_state.show_values[key] else "password"
                    new_value = st.text_input(
                        key,
                        value=data['value'],
                        type=input_type,
                        key=f"input_{key}"
                    )
                    if new_value != data['value']:
                        st.session_state.env_config[key]['value'] = new_value
                        save_env_config(st.session_state.env_config)
                        st.success(f"已更新配置: {key}")
                
                with col2:
                    # 显示/隐藏按钮
                    if st.button(
                        "显示" if not st.session_state.show_values[key] else "隐藏",
                        key=f"show_{key}"
                    ):
                        st.session_state.show_values[key] = not st.session_state.show_values[key]
                        st.rerun()
                
                with col3:
                    # 删除按钮
                    if st.button("删除", key=f"delete_{key}"):
                        del st.session_state.env_config[key]
                        if key in st.session_state.show_values:
                            del st.session_state.show_values[key]
                        save_env_config(st.session_state.env_config)
                        st.success(f"已删除配置: {key}")
                        st.rerun()
    else:
        st.info("暂无配置项")
    
    # 导出配置按钮
    if st.button("导出配置"):
        # 创建用于导出的配置（不包含敏感信息）
        export_config = {
            key: "******" for key in st.session_state.env_config.keys()
        }
        st.download_button(
            "下载配置模板",
            data=json.dumps(export_config, indent=2, ensure_ascii=False),
            file_name="config_template.json",
            mime="application/json"
        ) 