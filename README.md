# RAG-Summarizer

基于检索增强生成（RAG）的问答系统

![完整流程图](assets/Pipeline.png)

## 项目简介

RAG-Summarizer 是一个检索增强生成系统，能够根据用户的检索请求，从向量数据库中检索相关文档，并生成总结或回答。若遇到超出数据库范围的问题，则调用谷歌搜索结合大模型进行回答。

## 系统要求

- Python >= 3.8 （建议Python 3.9，当前的`requirements.txt`和`setup.py`已在Python 3.9上进行测试）

## VPN要求
- 由于本RAG系统需要连接Huggingface下载模型，也涉及OpenAI API、Google网络检索API等，请在打开VPN后使用。

## 安装方法

1. 克隆仓库：
```bash
git clone [仓库地址]
```

2. 安装后端依赖：
```bash
cd RagSummarizer
# 建议使用虚拟环境 e.g. conda create -n rag python=3.9 && conda activate rag
pip install -r requirements.txt
```

或者直接通过 setup.py 安装：
```bash
pip install . # OR
pip install -e . # 如果需要开发
```

3. 安装前端依赖：
```bash
cd frontend
npm install
```

## 主要依赖

- FastAPI - Web 框架
- LangChain - RAG 系统核心
- LangGraph - 对话记忆管理
- ChromaDB - 向量数据库
- Sentence-Transformers - 文本嵌入
- 其他重要组件：
  - langchain-chroma
  - langchain-community
  - langchain-core
  - langchain-huggingface
  - python-dotenv（环境配置）
  - uvicorn（ASGI 服务器）

## 使用方法

1. 配置环境变量：
```bash
cd src
cp .env.example .env
# 复制 .env.example 文件，重命名为 .env 文件
# 编辑 .env 文件，填入必要的 API 密钥、代理地址（如有需要）等
```

2. 启动服务：
```bash
# 在RagSummarizer目录下
python -m src.app
```

3. 启动前端：
```bash
cd frontend
npm run dev
```

4. 访问前端：
```bash
# 默认端口为3000
http://localhost:3000/
```


## FAQ

1. 运行这个项目需要VPN吗？

需要。用于连接HuggingFace、OpenAI API、Google Search API。

2. 什么时候需要修改`.env`文件里的 `HTTP_PROXY`和`HTTPS_PROXY`？

- 如果您的VPN环境需要使用代理，请根据实际情况修改`.env`文件中的`HTTP_PROXY`和`HTTPS_PROXY`环境变量。
- 如果您的VPN环境不需要使用代理，请将`HTTP_PROXY`和`HTTPS_PROXY`设置为空。

3. 调用这个项目的API时，我遇到了"Remote Error"，这是什么意思？

若在调用API过程中遇到"Remote Error"类问题，这表示您的VPN网络不稳定，请检查您的VPN，或使用其他VPN。

4. 我只想要使用数据库RAG，不想要使用Google网络检索，应该怎么办？

如果您不想使用网络检索，请将`.env`文件中的`WEB_SEARCH_ENABLED`设置为`false`，您将不能使用Google搜索，但可以继续使用数据库RAG。



## 项目参数设置

可在`src/configs/settings.py`和`src/configs/prompt_settings.py`中进行设置。
## 项目结构

```
python/                         # 开发和测试代码
frontend/                       # 前端代码
src/
├── api/                        # API 接口层
├── services/                   # 核心服务层
├── models/                     # 数据模型定义
├── config/                     # 配置文件
├── custom_imported_classes/    # 自定义组件，用于重写langchain的类函数
├── custom_classes/             # 自定义大模型类
├── utils/                      # 通用工具
├── data/                       # 数据源文件，初次运行时会将其编码为嵌入向量，存入向量数据库
├── tests/                      # 测试文件（用于开发，请勿使用）
├── chroma_db/                  # 向量数据库存储
├── app.py                      # FastAPI 应用入口
├── main.py                     # 测试主程序入口（用于开发，请勿使用）
└── .env.example                # 环境变量示例
setup.py                    # 安装配置：用于pip install .
pyproject.toml              # 安装配置：用于pip install -e .
requirements.txt            # 项目依赖：用于pip install -r requirements.txt
```


## 开发状态

当前版本：0.1.0 (Alpha)

项目处于积极开发阶段，API 可能会有变动。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 注意事项

- 本项目仍处于 Alpha 阶段，不建议用于生产环境
- 使用前请确保已正确配置所有必要的 API 密钥
- 建议在虚拟环境中运行项目
