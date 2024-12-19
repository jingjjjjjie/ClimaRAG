# RAG-Summarizer

基于检索增强生成（RAG）的问答系统

## 项目简介

RAG-Summarizer 是一个检索增强生成系统，能够根据用户的检索请求，从向量数据库中检索相关文档，并生成总结或回答。若遇到超出数据库范围的问题，则调用谷歌搜索结合大模型进行回答。

## 系统要求

- Python >= 3.8 （当前的`requirements.txt`和`setup.py`已在Python 3.9上进行测试）

## 安装方法

1. 克隆仓库：
```bash
git clone [仓库地址]
```

2. 安装后端依赖：
```bash
cd src
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
# 编辑 .env 文件，填入必要的 API 密钥
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
├── tests/                      # 测试文件
├── chroma_db/                  # 向量数据库存储
├── app.py                      # FastAPI 应用入口
├── main.py                     # 测试主程序入口
├── requirements.txt            # 项目依赖
├── setup.py                    # 安装配置
└── .env.example                # 环境变量示例
```

## 开发状态

当前版本：0.1.0 (Alpha)

项目处于积极开发阶段，API 可能会有变动。

## 许可证

MIT License

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 注意事项

- 本项目仍处于 Alpha 阶段，不建议用于生产环境
- 使用前请确保已正确配置所有必要的 API 密钥
- 建议在虚拟环境中运行项目
