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
            lines = f.readlines()
            
        current_group = None
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('## '):  # 使用双井号标记配置组
                current_group = line[3:].strip()
                continue
                
            if line.startswith('# '):  # 单井号标记配置分类
                current_section = line[1:].strip()
                continue
                
            if '=' in line and current_group:  # 配置项
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # 使用默认值处理 None 的情况
                group = current_group if current_group else '默认配置'
                section = current_section if current_section else '默认分类'
                
                # 使用组名作为前缀创建唯一键名
                unique_key = f"{group}_{key}"
                
                config[unique_key] = {
                    'value': value,
                    'section': section,
                    'group': group,
                    'original_key': key  # 保存原始键名
                }
    
    # 显示当前使用的配置文件路径
    st.sidebar.info(f"当前配置文件: {env_path}")
    
    return config

def save_env_config(config: Dict[str, Dict[str, str]]):
    """保存环境变量配置"""
    env_path = get_env_path()
    
    # 确保目录存在
    os.makedirs(os.path.dirname(env_path), exist_ok=True)
    
    # 按配置组和section分组
    groups = {}
    for key, data in config.items():
        group = data.get('group', '默认配置')
        section = data.get('section', '默认分类')
        if group not in groups:
            groups[group] = {}
        if section not in groups[group]:
            groups[group][section] = []
        # 使用原始键名保存配置
        original_key = data.get('original_key', key.split('_', 1)[1] if '_' in key else key)
        groups[group][section].append((original_key, data['value']))
    
    # 写入文件
    with open(env_path, 'w', encoding='utf-8') as f:
        # 按字母顺序排序所有组
        for group in sorted(groups.keys()):
            # 写入组标记
            f.write(f"## {group}\n\n")
            
            sections = groups[group]
            if not sections:  # 如果组没有分类，添加默认分类
                f.write("# 默认分类\n\n")
                continue
            
            # 按字母顺序排序分类
            for section in sorted(sections.keys()):
                # 写入分类标记
                f.write(f"# {section}\n")
                
                # 写入配置项
                items = sections[section]
                if items:  # 只有当有配置项时才写入
                    for key, value in sorted(items):
                        f.write(f"{key}={value}\n")
                f.write("\n")

def config_page():
    """配置管理页面"""
    st.title("配置管理")
    
    # 初始化session state
    if 'env_config' not in st.session_state:
        st.session_state.env_config = {}
    if 'show_values' not in st.session_state:
        st.session_state.show_values = {}
    
    # 每次页面加载时重新读取配置
    st.session_state.env_config = load_env_config()
    
    # 添加新配置的表单
    with st.expander("添加新配置", expanded=False):
        with st.form("add_config"):
            # 获取现有的配置组和分类，确保处理 None 值
            groups = list(set(
                data.get('group', '默认配置') for data in st.session_state.env_config.values()
            ))
            groups = sorted([g for g in groups if g is not None] + ['默认配置'])
            
            sections = list(set(
                data.get('section', '默认分类') for data in st.session_state.env_config.values()
            ))
            sections = sorted([s for s in sections if s is not None] + ['默认分类'])
            
            # 配置组选择
            col1, col2 = st.columns(2)
            with col1:
                new_group = st.selectbox(
                    "配置组",
                    options=["新建配置组"] + groups,
                    key="new_group"
                )
                
                if new_group == "新建配置组":
                    new_group = st.text_input("输入配置组名称")
            
            # 配置类型选择
            with col2:
                config_type = st.selectbox(
                    "配置类型",
                    options=["Azure OpenAI", "自定义配置"],
                    key="config_type"
                )
            
            if config_type == "Azure OpenAI":
                # Azure OpenAI 配置模板
                st.markdown("### Azure OpenAI 配置")
                col1, col2 = st.columns(2)
                with col1:
                    api_key = st.text_input("API Key", type="password", key="azure_api_key")
                    endpoint = st.text_input("Endpoint", key="azure_endpoint")
                with col2:
                    deployment = st.text_input("Deployment Name", key="azure_deployment")
                    api_version = st.text_input("API Version", value="2024-02-15-preview", key="azure_api_version")
                
                if st.form_submit_button("添加 Azure OpenAI 配置"):
                    if new_group and api_key and endpoint and deployment:
                        # 添加一组 Azure OpenAI 配置
                        configs = {
                            "AZURE_OPENAI_API_KEY": api_key,
                            "AZURE_OPENAI_ENDPOINT": endpoint,
                            "AZURE_DEPLOYMENT_NAME": deployment,
                            "AZURE_OPENAI_API_VERSION": api_version
                        }
                        
                        for key, value in configs.items():
                            st.session_state.env_config[key] = {
                                'value': value,
                                'section': 'Azure OpenAI配置',
                                'group': new_group
                            }
                        
                        save_env_config(st.session_state.env_config)
                        st.success(f"已添加 Azure OpenAI 配置组: {new_group}")
                        st.experimental_rerun()
            else:
                # 自定义配置
                st.markdown("### 自定义配置")
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_section = st.selectbox(
                        "配置分类",
                        options=["新建分类"] + sections,
                        key="new_section"
                    )
                    if new_section == "新建分类":
                        new_section = st.text_input("输入新分类名称")
                
                with col2:
                    new_key = st.text_input("配置键名", key="new_key")
                
                with col3:
                    new_value = st.text_input("配置值", type="password", key="new_value")
                
                if st.form_submit_button("添加配置"):
                    if new_group and new_section and new_key:
                        st.session_state.env_config[new_key] = {
                            'value': new_value,
                            'section': new_section,
                            'group': new_group
                        }
                        save_env_config(st.session_state.env_config)
                        st.success(f"已添加配置: {new_key}")
                        st.experimental_rerun()
    
    # 配置组操作
    if st.session_state.env_config:
        # 按配置组和section分组显示
        groups = {}
        for key, data in st.session_state.env_config.items():
            group = data.get('group', '默认配置')  # 使用默认值处理 None
            section = data.get('section', '默认分类')  # 使用默认值处理 None
            if group not in groups:
                groups[group] = {}
            if section not in groups[group]:
                groups[group][section] = []
            groups[group][section].append((key, data))
        
        # 显示所有配置组
        for group in sorted(groups.keys()):
            sections = groups[group]
            with st.expander(f"配置组: {group}", expanded=True):
                # 配置组操作按钮
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"导出配置组: {group}", key=f"export_{group}"):
                        # 创建用于导出的配置（不包含敏感信息）
                        export_config = {}
                        for section, items in sections.items():
                            for key, data in items:
                                if key not in export_config:
                                    export_config[key] = "******"
                        
                        st.download_button(
                            f"下载 {group} 配置模板",
                            data=json.dumps(export_config, indent=2, ensure_ascii=False),
                            file_name=f"{group}_template.json",
                            mime="application/json",
                            key=f"download_{group}"
                        )
                
                with col2:
                    if st.button(f"复制配置组: {group}", key=f"copy_{group}"):
                        new_group_name = f"{group}_copy"
                        # 复制配置组中的所有配置
                        for section, items in sections.items():
                            for key, data in items:
                                new_key = f"{key}_copy"
                                st.session_state.env_config[new_key] = {
                                    'value': data['value'],
                                    'section': data.get('section', '默认分类'),
                                    'group': new_group_name
                                }
                        save_env_config(st.session_state.env_config)
                        st.success(f"已复制配置组: {new_group_name}")
                        st.experimental_rerun()
                
                with col3:
                    if st.button(f"删除配置组: {group}", key=f"delete_{group}"):
                        # 删除配置组中的所有配置
                        keys_to_delete = []
                        for section, items in sections.items():
                            for key, _ in items:
                                keys_to_delete.append(key)
                                if key in st.session_state.show_values:
                                    del st.session_state.show_values[key]
                        
                        for key in keys_to_delete:
                            del st.session_state.env_config[key]
                        
                        save_env_config(st.session_state.env_config)
                        st.success(f"已删除配置组: {group}")
                        st.experimental_rerun()
                
                # 显示每个分类下的配置
                for section in sorted(sections.keys()):
                    items = sections[section]
                    if items:  # 只显示有配置项的分类
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
                                    st.experimental_rerun()
                            
                            with col3:
                                # 删除按钮
                                if st.button("删除", key=f"delete_{key}"):
                                    del st.session_state.env_config[key]
                                    if key in st.session_state.show_values:
                                        del st.session_state.show_values[key]
                                    save_env_config(st.session_state.env_config)
                                    st.success(f"已删除配置: {key}")
                                    st.experimental_rerun()
    else:
        st.info("暂无配置项") 