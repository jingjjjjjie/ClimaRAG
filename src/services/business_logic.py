from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.retrievers.self_query.base import SelfQueryRetriever
from ..models.data_models import METADATA_FIELD_INFO, DOCUMENT_CONTENT_DESCRIPTION, RouteQuery
from ..tools.custom_chat_model import RedPillChatModel
from ..tools.customllm import RedPillLLM
from ..config.settings import RED_PILL_API_KEY, LLM_MODEL
from .memory_manager import RAGMemoryManager
import logging

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
        prompt = ChatPromptTemplate.from_template(
            """Answer the question based only on the following context:
            {context}
            This is the conversation history:
            {question}
            The last message in the history is the current question.
            """
             # Question: {question}
        )

        # self.abstract_chain = (
        #     # {"context": self.abstract_retriever, "question": RunnablePassthrough()} |
        #     prompt
        #     | self.llm
        #     | StrOutputParser()
        # )

        # self.content_chain = (
        #     # {"context": self.content_retriever, "question": RunnablePassthrough()}
        #     prompt
        #     | self.llm
        #     | StrOutputParser()
        # )

        # self.hyde_chain_abstract = RunnablePassthrough.assign(hypothetical_document=self.abstract_chain)
        # self.hyde_chain_content = RunnablePassthrough.assign(hypothetical_document=self.content_chain)

    def setup_router(self):
        logger.info("Setting up router")
        system_prompt = "You are an expert at routing a user question to the appropriate data source. You also faithfully return the conversation history with the user without modifications."
        
        # Modified to handle message history
        router_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Given the following query and conversation history, determine the appropriate data source to route the query to. The query is the last message in the conversation history.\n\nConversation History:\n{messages}\n")
        ])
        
        routing_llm = self.chat_llm.with_structured_output(RouteQuery)
        router = router_prompt | routing_llm
        
        self.full_chain = router | RunnableLambda(self.choose_route)

    def choose_route(self, result):
        logger.info(f"Choosing route for result: {result}")

        logger.info(f"Result datasource: {result.datasource.lower()}")

        prompt = ChatPromptTemplate.from_template(
            """Answer the question based only on the following context:
            {context}
            This is the conversation history:
            {question}
            The last message in the history is the current question.
            """
        )

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
            return 'The answer that you are looking for is not here :)'

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