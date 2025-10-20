"""
Main entry point for the RAG (Retrieval-Augmented Generation) Summarization System.

This script is designed for **standalone execution** (e.g., `python main.py`)
and is **not used** when running the system as a FastAPI app.

It performs the following key functions:
1. Checks whether preprocessed vector stores (embeddings) already exist.
2. If not found, it triggers the data preprocessing and embedding pipeline.
3. Loads the resulting vector databases for abstracts and full-text content.
4. Initializes the RAGSystem, which enables retrieval + summarization queries.

Typical usage:
---------------
$ python main.py

The script can later be extended for interactive or batch query processing.
"""

import os
import logging
from .config.settings import DATA_PATH, PERSIST_DIRECTORY
from .services.business_logic import RAGSystem
from .services.data_processor import preprocess_and_store_data, DataProcessor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Check if vector stores already exist
    if not os.path.exists(PERSIST_DIRECTORY):
        logger.info("Vector stores not found. Processing data...")
        abstract_store, content_store, stats = preprocess_and_store_data(DATA_PATH, PERSIST_DIRECTORY)
        logger.info(f"Vector store statistics: {stats}")
    else:
        logger.info("Loading existing vector stores...")
        processor = DataProcessor(PERSIST_DIRECTORY)
        abstract_store, content_store = processor.create_vector_stores()
        stats = processor.get_store_stats()
        logger.info(f"Loaded vector store statistics: {stats}")
    
    # Initialize RAG system with memory
    rag_system = RAGSystem(abstract_store, content_store)
    
    # # Example queries
    # queries = [
    #     "summarize advancements in the field natural language processing on the year 2020",
    #     "Tell me about the transformer architecture in detail",
    #     "What did we discuss about transformers earlier?",
    # ]
    
    # # Process queries
    # for query in queries:
    #     result = rag_system.process_query(query)
    #     # display_results(result)
    #     print(result)
    #     print('\n')

if __name__ == "__main__":
    main()