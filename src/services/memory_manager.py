import logging
import traceback
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import AIMessage

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from ..config.settings import MEMORY_LIMIT

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
            # messages = state["messages"]
            
            # Limit to the last k messages
            messages = []
            for m in state["messages"][::-1]:
                messages.append(m)
                if len(messages) >= MEMORY_LIMIT:
                    if messages[-1].type != "tool":
                        break
                    
            messages = messages[::-1]

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
            
            logger.info("Query processed through RAG system")
            
            # Create an AI message with just the response
            ai_message = AIMessage(content=answer)

            print("---ai_message--- in process_with_memory")
            print(ai_message)
            
            # Return both the message for memory and the full result
            return {
                "messages": [ai_message],
                # only messages will actually be returned
                # "type": result['type'],
                # "docs": result['docs'] if 'docs' in result else [],
                # "_result": result  # Use a different key that won't be processed as a message
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

            print("---result--- in process_query_with_memory")
            print(result)

            print("result['messages'][-1]")
            print(result["messages"][-1])
            
            # Return the full result dictionary that includes type, docs, and response
            return {
                'answer': result["messages"][-1].content,
            }
                
        except Exception as e:
            logger.error(f"Error processing query with memory: {str(e)}")
            traceback.print_exc()
            raise