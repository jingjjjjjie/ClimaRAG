import os
import logging
import re
import json

from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.load import dumps, loads
from operator import itemgetter

from .memory_manager import RAGMemoryManager
from ..models.data_models import METADATA_FIELD_INFO, RouteQuery
from ..custom_classes.custom_chat_model import RedPillChatModel
from ..custom_classes.customllm import RedPillLLM
from ..custom_imported_classes.search import FilteredGoogleSearchAPIWrapper
from ..custom_imported_classes.retrievers import CustomWebResearchRetriever
from ..config.settings import RED_PILL_API_KEY, LLM_MODEL
from ..config.prompt_settings import (
    ROUTER_SYSTEM_PROMPT,
    ROUTER_HUMAN_PROMPT,
    RAG_TEMPLATE,
    DOCUMENT_CONTENT_DESCRIPTION,
    RAG_FUSION_QUERY_TEMPLATE
)


# Get the HTTP_PROXY environment variable
http_proxy = os.getenv('HTTP_PROXY')
https_proxy = os.getenv('HTTPS_PROXY')

if http_proxy:
    # Set proxy environment variables (for VPN)
    os.environ['http_proxy'] = http_proxy
else:
    print('cant find http_proxy')
if https_proxy:
    os.environ['https_proxy'] = https_proxy
else:
    print('cant find https_proxy')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGSystem:
    _instance = None
    
    @classmethod
    def initialize(cls, abstract_store, content_store):
        if cls._instance is None:
            cls._instance = cls(abstract_store, content_store)
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError("RAGSystem not initialized")
        return cls._instance
    
    def __init__(self, abstract_store, content_store):
        logger.info("Initializing RAGSystem")
        self.abstract_store = abstract_store
        self.content_store = content_store
        self.setup_components()
        
        # Initialize memory manager
        logger.info("Initializing memory manager")
        self.memory_manager = RAGMemoryManager(self)
        
        # Initialize web research components
        self.setup_web_research()

    def setup_components(self):
        logger.info("Setting up RAG components")
        try:
            self.setup_llms()
            self.setup_retrievers()
            self.setup_rag_fusion()
            self.setup_chains()
            self.setup_router()
            logger.info("Successfully set up all RAG components")
        except Exception as e:
            logger.error(f"Error setting up components: {str(e)}")
            raise

    def setup_llms(self):
        logger.info("Setting up LLMs")
        self.chat_llm = RedPillChatModel(
            model=LLM_MODEL,
            api_key=RED_PILL_API_KEY,
            temperature=0
        )
        self.llm = RedPillLLM(
            model=LLM_MODEL,
            api_key=RED_PILL_API_KEY,
            temperature=0.5
        )

    def setup_retrievers(self):
        logger.info("Setting up retrievers")
        self.abstract_retriever = SelfQueryRetriever.from_llm(
            self.llm,
            self.abstract_store,
            DOCUMENT_CONTENT_DESCRIPTION,
            METADATA_FIELD_INFO,
            verbose=True,
            enable_limit=True,
            search_kwargs={"k": 5}
        )
        
        self.content_retriever = SelfQueryRetriever.from_llm(
            self.llm,
            self.content_store,
            DOCUMENT_CONTENT_DESCRIPTION,
            METADATA_FIELD_INFO,
            verbose=True,
            enable_limit=True,
            search_kwargs={"k": 5}
        )

    def setup_rag_fusion(self):
        """Setup RAG Fusion components"""
        logger.info("Setting up RAG Fusion")
        
        # Setup query generation prompt
        self.prompt_rag_fusion = ChatPromptTemplate.from_template(RAG_FUSION_QUERY_TEMPLATE)
        
        # Setup query generation chain
        self.generate_queries = (
            self.prompt_rag_fusion 
            | self.llm
            | StrOutputParser() 
            | (lambda x: x.split("\n"))
        )
        
        # Setup Content Retriever with RAG Fusion
        self.content_retriever_with_rag_fusion = self.generate_queries | self.content_retriever.map() | self.reciprocal_rank_fusion
        
        # Setup Content RAG Fusion Chain
        self.content_rag_fusion_chain = (
            {"context": self.content_retriever_with_rag_fusion, 
             "question": itemgetter("question")} 
            | ChatPromptTemplate.from_template(RAG_TEMPLATE)
            | self.llm
            | StrOutputParser()
        )
        
        logger.info("RAG Fusion setup complete")

    def reciprocal_rank_fusion(self, results: list[list], k=60):
        """Reciprocal rank fusion that takes multiple lists of ranked documents"""
        logger.info("Performing reciprocal rank fusion")
        
        # Initialize a dictionary to hold fused scores for each unique document
        fused_scores = {}

        # Iterate through each list of ranked documents
        for docs in results:
            # Iterate through each document in the list
            for rank, doc in enumerate(docs):
                doc_str = dumps(doc)
                if doc_str not in fused_scores:
                    fused_scores[doc_str] = 0
                fused_scores[doc_str] += 1 / (rank + k)

        # Sort documents based on fused scores
        reranked_results = [
            (loads(doc), score)
            for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        ]

        return reranked_results

    def setup_chains(self):
        logger.info("Setting up chains")

    def setup_router(self):
        logger.info("Setting up router")
        router_prompt = ChatPromptTemplate.from_messages([
            ("system", ROUTER_SYSTEM_PROMPT),
            ("human", ROUTER_HUMAN_PROMPT)
        ])
        
        routing_llm = self.chat_llm.with_structured_output(RouteQuery)
        router = router_prompt | routing_llm
        
        self.full_chain = router | RunnableLambda(self.choose_route)

    def setup_web_research(self):
        """Initialize web research components"""
        logger.info("Setting up web research retriever")
        try:
            # Initialize our filtered Google Search
            self.search = FilteredGoogleSearchAPIWrapper()
            
            # Use our custom retriever with our filtered search
            self.web_research_retriever = CustomWebResearchRetriever.from_llm(
                vectorstore=self.content_store,
                llm=self.llm,
                search=self.search,
                allow_dangerous_requests=True,
                num_search_results=1,
                text_splitter=RecursiveCharacterTextSplitter(
                    chunk_size=500,
                    chunk_overlap=50
                )
            )
            
            self.web_qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
                self.llm, 
                retriever=self.web_research_retriever,
                return_source_documents=True
            )
            
            logger.info("Web research components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up web research: {str(e)}")
            raise

    def process_web_search(self, result):
        """Process a query using web search and format response with APA-style citations"""
        logger.info("Processing web search query")
        try:
            logger.info(f"Result: {result}")
            
            if result.messages:
                messages_str = str(result.messages)
                logger.info(f"Messages string: {messages_str}")
                
                matches = re.findall(r"content='(.*?)'", messages_str)
                
                if matches:
                    question = matches[-1]
                    logger.info(f"Extracted question: {question}")
                else:
                    try: 
                        # User call for web search in the first message, didn't get formatted correctly, so try this format
                        question = result.messages
                    except Exception as e:
                        logger.error(f"Error extracting question: {str(e)}")
                        logger.warning("Could not extract content from messages")
                        return "Could not process the question format."
            else:
                logger.warning("No messages found in result")
                return "No question found to process."

            logger.info(f"Question: {question}")
            
            web_result = self.web_qa_chain.invoke({
                "question": question
            })

            logger.info(f"Web result: {web_result}")
            
            response = f"{web_result['answer']}\n\n### References\n"
            logger.info(f"Response: {response}")

            # Deduplicate sources using a dictionary with URL as key
            sources = {}
            if 'source_documents' in web_result:
                for doc in web_result['source_documents']:
                    metadata = doc.metadata
                    
                    print("metadata", metadata)
                    
                    source_url = metadata.get('source', '').strip()
                    title = metadata.get('title', '').strip()
                    
                    if source_url and source_url not in sources:
                        sources[source_url] = {
                            'title': title,
                            'url': source_url,
                        }
                        
                        response += f"- {title}. Retrieved from [{source_url}]({source_url})\n"
            else:
                logger.warning("No source_documents found in web_result")
                logger.debug(f"Available keys in web_result: {web_result.keys()}")

            return response
            
        except Exception as e:
            logger.error(f"Error in web research: {str(e)}")
            return "I apologize, but I couldn't find a reliable answer to your question at this moment."

    def choose_route(self, result):
        logger.info(f"Choosing route for result: {result}")
        logger.info(f"Result datasource: {result.datasource.lower()}")

        prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)

        def return_messages(result):
            return result.messages

        if "abstract_store" in result.datasource.lower():
            return {"context": self.abstract_retriever, "question": RunnableLambda(return_messages)} | prompt | self.llm | StrOutputParser()
        elif "content_store" in result.datasource.lower():
            # Use RAG Fusion for content store queries
            return {"question": RunnableLambda(return_messages)} | self.content_rag_fusion_chain
        else:
            # Use web research for other queries
            logger.info("Using web research retriever for query")
            return self.process_web_search(result)

    # def format_message_history(self, messages):
    #     """Format message history into a readable string"""
    #     history = []
    #     for msg in messages[:-1]:  # Exclude the last message as it's the current question
    #         role = "Assistant" if isinstance(msg, AIMessage) else "Human"
    #         history.append(f"{role}: {msg.content}")
    #     return "\n".join(history)

    def process_query(self, query):
        """
        Process a query with message history support
        
        Args:
            query: Can be either a string or a list of messages
        """
        logger.info(f"Processing query")
        try:
            # Use the memory manager to process the query
            return self.memory_manager.process_query_with_memory(query)
                
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise