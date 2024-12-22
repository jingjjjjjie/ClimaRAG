# Data source descriptions
ABSTRACT_STORE_DESC = """Abstract_Store is a Database of climate & environmental research abstracts"""

CONTENT_STORE_DESC = """Content_Store is a Database of climate & environmental research full-texts"""

ROUTING_DESCRIPTION = f"""Given {ABSTRACT_STORE_DESC} and {CONTENT_STORE_DESC}:
 Return 'Abstract_Store' for summaries and general queries
 Return 'Content_Store' for specific content/concept details
 Return 'OTHER' for unrelated or invalid queries"""

# Router prompts
ROUTER_SYSTEM_PROMPT = "Expert router that directs queries to appropriate data sources and preserves conversation history"

ROUTER_HUMAN_PROMPT = """Route the last message in conversation history to appropriate data source.

Conversation History:
{messages}
"""



# RAG Fusion prompts
RAG_FUSION_QUERY_TEMPLATE = """Generate 4 progressive search queries for {question}:
. Basic concept/overview
. Key components/factors
. Detailed analysis/process
. Advanced implications/applications"""


# RAG prompts
RAG_TEMPLATE = """Answer the last message using only provided context. 
Context:
{context}
Chat History:
{question}
Requirements:
 Use numbered citations [1]
 Include references in APA reference style, attach a clickable link to the source link, Example: [1] Author. (Year). _Source Title._ [https://www.example.com](https://www.example.com)
 Format in markdown
 Focus on relevant information only"""



# Document content description
DOCUMENT_CONTENT_DESCRIPTION = "Thesis in the climate change field"