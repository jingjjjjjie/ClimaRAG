from setuptools import setup, find_packages

setup(
    name="rag-summarizer",
    version="0.1.0",
    description="A RAG-based document summarization and QA system",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "python-dotenv",
        "langchain",
        "langchain-community",
        "langchain-core",
        "langchain-huggingface",
        "chromadb",
        "sentence-transformers",
        "requests",
        "google-api-python-client",
        "typing-extensions",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 