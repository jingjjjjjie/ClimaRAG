from dotenv import load_dotenv
import os

load_dotenv()

# API Keys
RED_PILL_API_KEY = os.getenv("RED_PILL_API_KEY_XN")

# Model Settings
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
LLM_MODEL = "gpt-4o"
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 100

# Data Settings
# DATA_PATH = './src/data/data_info.txt'
DATA_PATH = './src/data/output4.json'
PERSIST_DIRECTORY = "./src/chroma_db" 