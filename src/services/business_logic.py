import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain.retrievers.self_query.base import SelfQueryRetriever
from ..models.data_models import METADATA_FIELD_INFO, RouteQuery
from ..tools.custom_chat_model import RedPillChatModel
from ..tools.customllm import RedPillLLM
from ..config.settings import RED_PILL_API_KEY, LLM_MODEL
from ..config.prompt_settings import (
    ROUTER_SYSTEM_PROMPT,
    ROUTER_HUMAN_PROMPT,
    RAG_TEMPLATE,
    DOCUMENT_CONTENT_DESCRIPTION
)
from .memory_manager import RAGMemoryManager
from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
import logging
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..custom.search import FilteredGoogleSearchAPIWrapper
from ..custom.retrievers import CustomWebResearchRetriever

# Set proxy environment variables
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'

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
            search_kwargs={"k": 10}
        )
        
        self.content_retriever = SelfQueryRetriever.from_llm(
            self.llm,
            self.content_store,
            DOCUMENT_CONTENT_DESCRIPTION,
            METADATA_FIELD_INFO,
            verbose=True,
            enable_limit=True,
            search_kwargs={"k": 10}
        )

    def setup_chains(self):
        logger.info("Setting up chains")
        prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)

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

    def choose_route(self, result):
        logger.info(f"Choosing route for result: {result}")

        logger.info(f"Result datasource: {result.datasource.lower()}")

        prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)

        def return_messages(result):
            return result.messages

        if "abstract_store" in result.datasource.lower():
            # return 'abstract_chain'
            return {"context": self.abstract_retriever, "question": RunnableLambda(return_messages)} | prompt | self.llm | StrOutputParser()
            # return self.hyde_chain_abstract
        elif "content_store" in result.datasource.lower():
            # return 'content_chain'
            return {"context": self.content_retriever, "question": RunnableLambda(return_messages)} | prompt | self.llm | StrOutputParser()
            # return self.hyde_chain_content
        else:
            # Use web research for other queries
            logger.info("Using web research retriever for query")
            try:
                logger.info(f"Result: {result}")
                
                # Get the last message content using regex
                if result.messages:
                    messages_str = str(result.messages)
                    logger.info(f"Messages string: {messages_str}")
                    
                    # Extract content from the last message using regex
                    # This pattern matches the last occurrence of content='...' before the final ]
                    matches = re.findall(r"content='(.*?)'", messages_str)
                    
                    if matches:
                        question = matches[-1]
                        logger.info(f"Extracted question: {question}")
                    else:
                        logger.warning("Could not extract content from messages")
                        return "Could not process the question format."
                else:
                    logger.warning("No messages found in result")
                    return "No question found to process."

                logger.info(f"Question: {question}")
                
                # Get response from web research
                web_result = self.web_qa_chain.invoke({
                    "question": question
                })

                logger.info(f"Web result: {web_result}")
                
                # Format the response with answer
                response = f"{web_result['answer']}\n\nSources:\n"

                logger.info(f"Response: {response}")

                # Extract sources from source_documents
                if 'source_documents' in web_result:
                    for doc in web_result['source_documents']:
                        metadata = doc.metadata
                        source_url = metadata.get('source', '')
                        title = metadata.get('title', '')
                        if source_url:
                            response += f"- WebPageTitle: {title}\nWebPageLink: {source_url}\n"
                else:
                    logger.warning("No source_documents found in web_result")
                    logger.debug(f"Available keys in web_result: {web_result.keys()}")

                return response
                
            except Exception as e:
                logger.error(f"Error in web research: {str(e)}")
                return "I apologize, but I couldn't find a reliable answer to your question at this moment."

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