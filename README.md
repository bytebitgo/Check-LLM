# LLM测试工具

一个用于测试和评估各种大语言模型性能的Streamlit应用。

## 功能特点

- 支持多个LLM提供商（OpenAI、Anthropic、Google、Hugging Face等）
- 交互式对话测试界面
- 批量测试和性能评估
- 详细的分析报告和可视化
- 历史记录管理和数据导出

## 安装说明

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/llm-testing-tool.git
cd llm-testing-tool
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
```bash
cp config/config.template.env .env
```
然后编辑 `.env` 文件，填入你的API密钥和其他配置信息。

## 使用方法

启动应用：
```bash
streamlit run src/app.py
```

访问 http://localhost:8501 查看应用界面。

## 项目结构

```
.
├── src/
│   ├── services/    # LLM服务接口
│   ├── utils/       # 工具函数
│   ├── pages/       # Streamlit页面
│   └── components/  # UI组件
├── tests/           # 测试文件
├── data/            # 数据存储
├── config/          # 配置文件
└── README.md
```

## 开发说明

- 遵循PEP 8编码规范
- 使用pytest进行测试
- 提交前运行测试套件

## 版本历史

### v0.1.0 (2024-04-02)
- 初始版本
- 基本项目结构搭建
- 配置文件模板创建

## 许可证

MIT License 