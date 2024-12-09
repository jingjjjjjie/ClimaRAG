import logging
from .config.settings import DATA_PATH, PERSIST_DIRECTORY
from .services.business_logic import RAGSystem
from .utils.helpers import display_results
from .services.data_processor import preprocess_and_store_data, DataProcessor
import os

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
    
    # Example queries
    queries = [
        "summarize advancements in the field natural language processing on the year 2020",
        "Tell me about the transformer architecture in detail",
        "What did we discuss about transformers earlier?",
    ]
    
    # Process queries
    for query in queries:
        result = rag_system.process_query(query)
        # display_results(result)
        print(result)
        print('\n')

if __name__ == "__main__":
    main()