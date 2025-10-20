import os
import logging
from typing import List, Dict, Any
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from uuid import uuid4
from ..config.settings import EMBEDDING_MODEL, PERSIST_DIRECTORY
from ..utils.helpers import load_corpus
from chromadb.utils.batch_utils import create_batches

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, persist_directory=PERSIST_DIRECTORY):
        """Initialize the data processor with embedding model and storage paths"""
        logger.info(f"Initializing DataProcessor with persist directory: {persist_directory}")
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.persist_directory = persist_directory
        
        # Create persist directories if they don't exist
        self.abstract_persist_dir = os.path.join(persist_directory, "abstract")
        self.content_persist_dir = os.path.join(persist_directory, "content")
        os.makedirs(self.abstract_persist_dir, exist_ok=True)
        os.makedirs(self.content_persist_dir, exist_ok=True)

    def create_vector_stores(self):
        """Create or load vector stores for abstract and content"""
        logger.info("Creating vector stores")
        
        self.abstract_store = Chroma(
            collection_name="abstract_collection",
            embedding_function=self.embeddings,
            persist_directory=self.abstract_persist_dir
        )
        
        self.content_store = Chroma(
            collection_name="content_collection",
            embedding_function=self.embeddings,
            persist_directory=self.content_persist_dir
        )
        
        return self.abstract_store, self.content_store
    
    def add_documents_in_batches(self, store, documents, ids, batch_size=5000):
        """
        Safely add documents to a vector store in multiple batches.
        Works with LangChain vector stores (Chroma, FAISS, etc.).
        """
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            logging.info(f"Adding batch {i // batch_size + 1} with {len(batch_docs)} documents")
            store.add_documents(documents=batch_docs, ids=batch_ids)

    def process_documents(self, corpus: List[Dict[str, Any]]):
        """Process documents and store them in appropriate vector stores"""
        logger.info("Processing documents")
        
        # Create text splitter for content documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500, 
            chunk_overlap=100
        )
        
        # Process both abstracts and content in one loop
        abstract_docs = []
        content_docs = []
        
        for thesis in corpus:
            # Filter out the thesis with no full_text
            if 'full_text' not in thesis:
                continue

            try:
                year = int(thesis['Year'])
            except (ValueError, TypeError):
                # Skip this thesis if year conversion fails
                continue

            # Create abstract document
            abstract_doc = Document(
                page_content=thesis['Abstract'],
                metadata={
                    "title": thesis['Title'],
                    "year": year,
                    "source": thesis['clickable_url']
                }
            )
            abstract_docs.append(abstract_doc)

            # Create content document
            content_doc = Document(
                page_content=thesis['full_text'],
                metadata={
                    "title": thesis['Title'],
                    "year": year,
                    "source": thesis['clickable_url']
                }
            )
            content_docs.append(content_doc)
        
        # Split content documents into chunks
        logger.info("Splitting content documents into chunks")
        content_splits = text_splitter.split_documents(content_docs)
        logger.info(f"Created {len(content_splits)} chunks from {len(content_docs)} documents")
        
        # Generate UUIDs for documents
        abstract_uuids = [str(uuid4()) for _ in range(len(abstract_docs))]
        content_uuids = [str(uuid4()) for _ in range(len(content_splits))]
        
        # Add documents to vector stores
        logger.info(f"Adding {len(abstract_docs)} documents to abstract store")
        self.abstract_store.add_documents(documents=abstract_docs, ids=abstract_uuids)
        
        logger.info(f"Adding {len(content_splits)} chunks to content store")
        self.add_documents_in_batches(self.content_store, content_splits, content_uuids)
        
        return abstract_docs, content_splits
    
    def get_store_stats(self):
        """Get statistics about the vector stores"""
        logger.info("Retrieving vector store statistics")
        
        abstract_count = len(self.abstract_store.get()['ids'])
        content_count = len(self.content_store.get()['ids'])
        
        stats = {
            'abstract_store_count': abstract_count,
            'content_store_count': content_count,
            'total_documents': abstract_count + content_count
        }
        
        logger.info(f"Vector store stats: {stats}")
        return stats

def preprocess_and_store_data(data_path: str, persist_directory: str = PERSIST_DIRECTORY):
    """
    Main function to preprocess and store data
    """
    try:
        # Initialize processor
        processor = DataProcessor(persist_directory)
        
        # Create vector stores
        abstract_store, content_store = processor.create_vector_stores()
        
        # Load corpus from file
        corpus = load_corpus(data_path)
        
        # Process and store documents
        abstract_docs, content_splits = processor.process_documents(corpus)
        
        # Get store statistics
        stats = processor.get_store_stats()
        
        logger.info("Data preprocessing and storage completed successfully")
        return abstract_store, content_store, stats
        
    except Exception as e:
        logger.error(f"Error in preprocessing data: {str(e)}")
        raise 