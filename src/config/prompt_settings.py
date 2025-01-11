# Data source descriptions
ABSTRACT_STORE_DESC = """Abstract_Store is a Database of climate & environmental research abstracts, including topics related to causes and impacts of climate change, climate anxiety and human activities on the environment."""

CONTENT_STORE_DESC = """Content_Store is a Database of climate & environmental research full-texts, including topics related to causes and impacts of climate change, climate anxiety and human activities on the environment."""

ROUTING_DESCRIPTION = f"""Given that {ABSTRACT_STORE_DESC} and {CONTENT_STORE_DESC}:
 Return 'Abstract_Store' for summaries and general queries
 Return 'Content_Store' for specific content/concept details
 Return 'OTHER' for unrelated or invalid queries"""

# Router prompts
ROUTER_SYSTEM_PROMPT = "Expert router that directs queries to appropriate data sources and preserves conversation history"

ROUTER_HUMAN_PROMPT = """Route the last message in conversation history to appropriate data source.

Conversation History:
{messages}
"""

EVALUATION_DESCRIPTION = f"""Check if the query is a evaluation process, it is mentioned in the query with [This is a evaluation process]
Return True if the query mentioned that it is a evaluation process 
Return False if it did not mention"""



# RAG Fusion prompts
RAG_FUSION_QUERY_TEMPLATE = """Generate 4 progressive search queries for {question}:
. Basic concept/overview
. Key components/factors
. Detailed analysis/process
. Advanced implications/applications
Response (4 queries): """


# RAG prompts
RAG_TEMPLATE = """Answer the last message using only provided context. 
Context:
{context}
Chat History:
{question}
Requirements:
 Use numbered citations [1]
 Include references list at the end in APA REFERENCE STYLE, attach a clickable link to the source in the reference list.
 Format in markdown
 Focus on relevant information only"""

# RAG prompts
EVALUATE_TEMPLATE = """Answer the last message using only provided context. 
Context:
{context}
Chat History:
{question}
Requirements:
 Use numbered citations [1]
 Include references in APA reference style, attach a clickable link to the source link, and return the 1-3 sentences of groundtruth of the references,Example: [1] Author. (Year). _Source Title._ [https://www.example.com](https://www.example.com) \n Groundtruth:""
 Format in markdown
 Focus on relevant information only"""



# Document content description
DOCUMENT_CONTENT_DESCRIPTION = "Thesis in the climate change field"