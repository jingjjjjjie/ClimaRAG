import logging
import json
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import SystemMessage, AIMessage

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGMemoryManager:
    def __init__(self, rag_system):
        logger.info("Initializing RAGMemoryManager")
        self.rag_system = rag_system
        self.memory = MemorySaver()
        self.workflow = StateGraph(state_schema=MessagesState)
        self.setup_workflow()

    def setup_workflow(self):
        logger.info("Setting up workflow with memory")
        
        # Define the function that processes queries with memory
        def process_with_memory(state: MessagesState):
            logger.info("Processing query with memory")
            messages = state["messages"]

            print("---messages--- in process_with_memory")
            print(messages)
            
            # Process the last message using RAG system
            query = messages[-1].content
            logger.info(f"Current query in memory context: {query}")
            logger.info(f"Total messages in memory: {len(messages)}")
            
            # Use the direct processing method instead of process_query
            answer = self.rag_system.full_chain.invoke({"messages": messages})

            print("---answer--- in process_with_memory")
            print(answer)
            
            if answer == 'abstract_chain':
                logger.info("Query routed to abstract chain")
                docs = self.rag_system.abstract_retriever.invoke(query)
                response = self.rag_system.abstract_chain.invoke(query)
                result = {'type': 'abstract', 'docs': docs, 'response': response}
            
            elif answer == 'content_chain':
                logger.info("Query routed to content chain")
                docs = self.rag_system.content_retriever.invoke(query)
                response = self.rag_system.content_chain.invoke(query)
                result = {'type': 'content', 'docs': docs, 'response': response}
            
            else:
                logger.info("Query could not be routed")
                result = {'type': 'other', 'response': answer}
            
            logger.info("Query processed through RAG system")

            print("---result--- in process_with_memory")
            print(result)
            
            # Create an AI message with just the response
            ai_message = AIMessage(content=result['response'])

            print("---ai_message--- in process_with_memory")
            print(ai_message)
            
            # Return both the message for memory and the full result
            return {
                "messages": [ai_message],
                "_result": result  # Use a different key that won't be processed as a message
            }

        # Define the workflow
        self.workflow.add_node("rag_processor", process_with_memory)
        self.workflow.add_edge(START, "rag_processor")
        
        # Compile the workflow with memory
        logger.info("Compiling workflow with memory checkpointing")
        self.app = self.workflow.compile(checkpointer=self.memory)

    def process_query_with_memory(self, query, message_history=None):
        """
        Process a query while maintaining conversation history
        
        Args:
            query: Can be either a string or a list of messages
            message_history: Optional previous conversation history
        """
        try:
            logger.info(f"Processing query with memory")

            result = self.app.invoke(
                {"messages": query},
                config={"configurable": {"thread_id": "1"}}
            )
            logger.info("Successfully processed query with memory")
            
            # Return the full result dictionary that includes type, docs, and response
            if "_result" in result:
                return result["_result"]
            else:
                # Fallback to create a response from the message content
                return {
                    'type': 'other',
                    'docs': [],
                    'response': result["messages"][0].content
                }
                
        except Exception as e:
            logger.error(f"Error processing query with memory: {str(e)}")
            raise