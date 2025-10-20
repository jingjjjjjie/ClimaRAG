from dotenv import load_dotenv
import os

load_dotenv()

# API Keys
RED_PILL_API_KEY = os.getenv("RED_PILL_API_KEY")

# Model Settings
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
LLM_MODEL = "gpt-4o"
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 100

# Memory limit: the number of the last k messages to remember
# This is used to limit the number of messages to remember in the memory
# This includes the user messages and the replies from the AI
MEMORY_LIMIT = 5

# Data Settings
# DATA_PATH = './src/data/data_info.txt'
DATA_PATH = './src/data/data.json'
PERSIST_DIRECTORY = "./src/chroma_db" 