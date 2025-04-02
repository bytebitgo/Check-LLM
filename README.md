# LLM测试工具

一个用于测试和评估各种大语言模型(LLM)服务的工具。

## 功能特点

- 支持多个LLM服务商
  - OpenAI
  - Azure OpenAI
  - Anthropic
  - Google
  - 更多...
- 交互式对话测试
- 性能统计和分析
  - 响应时间分析
  - Token使用量统计
  - 成本分析
- 美观的用户界面
- 实时数据可视化

## 安装

1. 克隆仓库
```bash
git clone https://github.com/yourusername/llm-test-tool.git
cd llm-test-tool
```

2. 创建并激活虚拟环境
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# macOS/Linux:
source .venv/bin/activate
# Windows:
.\.venv\Scripts\activate
```

3. 安装依赖
```bash
# 确保pip是最新版本
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp config/config.template.env .env
# 编辑.env文件，添加必要的API密钥
```

## 使用方法

1. 确保虚拟环境已激活
```bash
# macOS/Linux:
source .venv/bin/activate
# Windows:
.\.venv\Scripts\activate
```

2. 启动应用
```bash
# 确保在项目根目录下运行
python -m streamlit run src/app.py
```

3. 在浏览器中访问应用（默认地址：http://localhost:8501）

4. 选择要测试的服务商和模型

5. 开始对话测试

6. 查看性能统计

## 配置说明

在`.env`文件中配置以下环境变量：

```env
OPENAI_API_KEY=your_openai_api_key
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key
```

## 版本历史

查看[更新日志](CHANGELOG.md)了解详细的版本历史。

## 贡献

欢迎提交Issue和Pull Request。

## 许可证

MIT 