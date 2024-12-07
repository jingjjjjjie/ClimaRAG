from ..services.system_manager import SystemManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_rag_system():
    # Initialize the system
    logger.info("Initializing RAG system...")
    rag_system = SystemManager.initialize()
    initial_id = id(rag_system)
    logger.info(f"Initial instance ID: {initial_id}")
    
    # Test queries
    test_queries = [
        "What is natural language processing?",
        "Explain transformer architecture",
        "What are embeddings?",
    ]
    
    for query in test_queries:
        # Get instance for each query
        current_system = SystemManager.get_instance()
        current_id = id(current_system)
        
        logger.info(f"\nProcessing query with instance ID: {current_id}")
        logger.info(f"Same instance as initial? {current_id == initial_id}")
        logger.info(f"Query: {query}")
        
        # Process query
        result = current_system.process_query(query)
        logger.info(f"Answer length: {len(result['answer'])}")
        logger.info(f"Answer: {result['answer'][:100]}...")  # Show first 100 chars

if __name__ == "__main__":
    test_rag_system() 