from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from config.settings import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

class DocumentProcessor:
    def __init__(self):
        self.embedder = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, 
            chunk_overlap=CHUNK_OVERLAP
        )

    def create_document(self, content, metadata):
        return Document(
            page_content=content,
            metadata=metadata
        )

    def process_documents(self, corpus):
        print("---processing documents---")
        abstract_store = []
        content_store = []

        for thesis in corpus:
            abstract_doc = self.create_document(
                thesis['abstract'],
                {"title": thesis['title'], "year": thesis['year']}
            )
            content_doc = self.create_document(
                thesis['content'],
                {"title": thesis['title'], "year": thesis['year']}
            )
            abstract_store.append(abstract_doc)
            content_store.append(content_doc)

        print("---splitting content---")
        content_splits = self.text_splitter.split_documents(content_store)
        
        return abstract_store, content_splits

    def create_vector_stores(self, abstract_docs, content_splits, dev_mode=False):
        """
        Create vector stores for abstract and content documents
        
        Args:
            abstract_docs: List of abstract documents
            content_splits: List of content splits
            dev_mode (bool): If True, only use 10 documents for faster development
        """
        if dev_mode:
            abstract_docs = abstract_docs[:10]
            content_splits = content_splits[:10]
        
        print("---creating abstract store---")

        abstract_store = Chroma.from_documents(
            documents=abstract_docs, 
            embedding=self.embedder, 
            collection_name='abstract'
        )

        print("---creating content store---")
        content_store = Chroma.from_documents(
            documents=content_splits, 
            embedding=self.embedder, 
            collection_name='content'
        )

        print("---vector stores created---")
        return abstract_store, content_store 