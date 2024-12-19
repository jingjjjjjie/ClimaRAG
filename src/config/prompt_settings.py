# Router prompts
ROUTER_SYSTEM_PROMPT = """You are an expert at routing a user question to the appropriate data source. 
You also faithfully return the conversation history with the user without modifications."""

ROUTER_HUMAN_PROMPT = """Given the following query and conversation history, determine the appropriate data source 
to route the query to. The query is the last message in the conversation history.

Conversation History:
{messages}
"""

# RAG prompts
RAG_TEMPLATE = """Answer the question based only on the following context:
{context}
This is the conversation history:
{question}
The last message in the history is the current question.
"""

# Data source descriptions
ABSTRACT_STORE_DESC = """Abstract_Store is a database with abstracts of papers related to climate change 
or the environment"""

CONTENT_STORE_DESC = """Content_Store is a database with the full text of papers related to climate change 
or the environment"""

ROUTING_DESCRIPTION = f"""{ABSTRACT_STORE_DESC}. {CONTENT_STORE_DESC}. Given a user question choose which 
datasource would be most relevant for answering their question. For Summarization or more general use cases, 
route to Abstract_Store, only if asked on concepts or specific content route to Content_Store. Otherwise, if 
you encounter something weird or not related to climate change or the environment, return OTHER"""

# Document content description
DOCUMENT_CONTENT_DESCRIPTION = "Thesis in the climate change field"