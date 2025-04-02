import os
from typing import Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """应用配置类"""
    # OpenAI配置
    openai_api_key: str = Field(..., env='OPENAI_API_KEY')
    openai_org_id: Optional[str] = Field(None, env='OPENAI_ORG_ID')
    
    # Azure OpenAI配置
    azure_openai_api_key: str = Field(..., env='AZURE_OPENAI_API_KEY')
    azure_openai_endpoint: str = Field(..., env='AZURE_OPENAI_ENDPOINT')
    azure_openai_api_version: str = Field("2024-02-15-preview", env='AZURE_OPENAI_API_VERSION')
    azure_deployment_name: str = Field("gpt-4", env='AZURE_DEPLOYMENT_NAME')
    
    # Anthropic配置
    anthropic_api_key: str = Field(..., env='ANTHROPIC_API_KEY')
    
    # Google配置
    google_api_key: str = Field(..., env='GOOGLE_API_KEY')
    
    # Hugging Face配置
    huggingface_api_key: str = Field(..., env='HUGGINGFACE_API_KEY')
    
    # 应用配置
    app_name: str = Field('LLM测试工具', env='APP_NAME')
    debug_mode: bool = Field(False, env='DEBUG_MODE')
    log_level: str = Field('INFO', env='LOG_LEVEL')
    
    # 数据存储配置
    data_dir: str = Field('./data', env='DATA_DIR')
    cache_dir: str = Field('./cache', env='CACHE_DIR')
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

# 创建全局配置实例
settings = Settings()

def ensure_directories():
    """确保必要的目录存在"""
    directories = [
        settings.data_dir,
        settings.cache_dir,
        os.path.join(settings.data_dir, 'logs'),
        os.path.join(settings.data_dir, 'results'),
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True) 