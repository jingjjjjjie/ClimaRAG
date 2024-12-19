import unittest
import logging
from concurrent.futures import ThreadPoolExecutor
from ..services.system_manager import SystemManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestRAGSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the RAG system once before all tests"""
        logger.info("Setting up RAG system for tests...")
        cls.rag_system = SystemManager.initialize()
        cls.initial_instance_id = id(cls.rag_system)
        logger.info(f"Initial RAG system instance ID: {cls.initial_instance_id}")

    def test_singleton_instance(self):
        """Test that multiple initializations return the same instance"""
        logger.info("Testing singleton pattern...")
        
        # Get multiple instances
        instance1 = SystemManager.get_instance()
        instance2 = SystemManager.get_instance()
        instance3 = SystemManager.initialize()
        
        # Check they're the same instance
        self.assertEqual(id(instance1), self.initial_instance_id)
        self.assertEqual(id(instance2), self.initial_instance_id)
        self.assertEqual(id(instance3), self.initial_instance_id)
        
        logger.info("Singleton pattern verified - all instances have the same ID")

    def test_query_consistency(self):
        """Test that multiple queries use the same RAG instance"""
        logger.info("Testing query consistency...")
        
        test_queries = [
            "What is natural language processing?",
            "Explain transformer architecture",
            "What are embeddings?",
        ]
        
        instance_ids = set()
        results = []
        
        for query_text in test_queries:
            # Get instance and process query
            rag_system = SystemManager.get_instance()
            instance_ids.add(id(rag_system))
            
            # Process query and store result
            result = rag_system.process_query(query_text)
            results.append(result)
            
            logger.info(f"Query processed with instance ID: {id(rag_system)}")
            logger.info(f"Query: {query_text}")
            logger.info(f"Answer length: {len(result['answer'])}")
        
        # Verify all queries used the same instance
        self.assertEqual(len(instance_ids), 1)
        self.assertEqual(list(instance_ids)[0], self.initial_instance_id)
        
        # Verify we got meaningful responses
        for result in results:
            self.assertIn('answer', result)
            self.assertTrue(len(result['answer']) > 0)

    def test_concurrent_access(self):
        """Test that concurrent access returns the same instance"""
        logger.info("Testing concurrent access...")
        
        def get_instance_id():
            instance = SystemManager.get_instance()
            return id(instance)
        
        # Test with multiple threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            instance_ids = list(executor.map(lambda _: get_instance_id(), range(10)))
        
        # Verify all threads got the same instance
        self.assertTrue(all(id == self.initial_instance_id for id in instance_ids))
        logger.info("Concurrent access verified - all threads received the same instance")

    def test_reset_and_reinitialize(self):
        """Test resetting and reinitializing the system"""
        logger.info("Testing reset and reinitialization...")
        
        # Store original instance ID
        original_id = id(SystemManager.get_instance())
        
        # Reset the system
        SystemManager.reset()
        self.assertIsNone(SystemManager._instance)
        
        # Reinitialize
        new_instance = SystemManager.initialize()
        new_id = id(new_instance)
        
        # Verify it's a new instance
        self.assertNotEqual(original_id, new_id)
        logger.info(f"Reset and reinitialization successful. New instance ID: {new_id}")

def run_tests():
    """Run the test suite"""
    logger.info("Starting RAG system tests...")
    unittest.main(verbosity=2)

if __name__ == "__main__":
    run_tests() 