from setuptools import setup, find_packages

setup(
    name="llm-test-tool",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "python-dotenv",
        "openai",
        "anthropic",
        "google-cloud-aiplatform",
        "pandas",
        "plotly",
    ],
) 