import os
import logging
from typing import Optional
from ..config.settings import DATA_PATH, PERSIST_DIRECTORY
from .data_processor import preprocess_and_store_data, DataProcessor
from .business_logic import RAGSystem

logger = logging.getLogger(__name__)

class SystemManager:
    _instance: Optional[RAGSystem] = None
    
    @classmethod
    def initialize(cls, persist_directory: str = PERSIST_DIRECTORY) -> RAGSystem:
        """Initialize the RAG system if it hasn't been initialized yet."""
        if cls._instance is None:
            logger.info("Initializing new RAG system...")
            try:
                # Check if vector stores already exist
                if not os.path.exists(persist_directory):
                    logger.info("Vector stores not found. Processing data...")
                    abstract_store, content_store, stats = preprocess_and_store_data(DATA_PATH, persist_directory)
                    logger.info(f"Vector store statistics: {stats}")
                else:
                    logger.info("Loading existing vector stores...")
                    processor = DataProcessor(persist_directory)
                    abstract_store, content_store = processor.create_vector_stores()
                    stats = processor.get_store_stats()
                    logger.info(f"Loaded vector store statistics: {stats}")
                
                # Initialize RAG system
                cls._instance = RAGSystem.initialize(abstract_store, content_store)
                logger.info(f"RAG system initialized and ready. ID: {id(cls._instance)}")
                
            except Exception as e:
                logger.error(f"Error initializing RAG system: {str(e)}")
                raise
                
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> RAGSystem:
        """Get the RAG system instance, initializing it if necessary."""
        if cls._instance is None:
            return cls.initialize()
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """Reset the RAG system instance (useful for testing)."""
        cls._instance = None 