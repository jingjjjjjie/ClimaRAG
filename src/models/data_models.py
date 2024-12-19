from typing import Literal
from pydantic import BaseModel, Field
from langchain.chains.query_constructor.schema import AttributeInfo

class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""
    datasource: Literal["Abstract_Store", "Content_Store", "OTHER"] = Field(
        ...,
        description="Abstract_Store is a database with abstracts of papers related to climate change or the environment, Content_Store is a database with the full text of papers related to climate change or the environment. Given a user question choose which datasource would be most relevant for answering their question. For Summarization or more general use cases, route to Abstract_Store, only if asked on concepts or specific content route to Content_Store. Otherwise, if you encounter something weird or not related to climate change or the environment, return OTHER",
    )
    messages: str = Field(
        ...,
        description="The conversation history with the user in the format received from the API"
    )

# Metadata field information for retrievers
METADATA_FIELD_INFO = [
    AttributeInfo(
        name="title",
        description="The title of the thesis",
        type="string",
    ),
    AttributeInfo(
        name="year",
        description="The year the thesis was published",
        type="integer",
    ),
    AttributeInfo(
        name="abstract",
        description="The abstract of the thesis",
        type="integer",
    ),
]

DOCUMENT_CONTENT_DESCRIPTION = "Thesis in the natural language processing field" 