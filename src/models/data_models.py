from typing import Literal
from pydantic import BaseModel, Field
from langchain.chains.query_constructor.schema import AttributeInfo
from ..config.prompt_settings import ROUTING_DESCRIPTION

class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""
    datasource: Literal["Abstract_Store", "Content_Store", "OTHER"] = Field(
        ...,
        description=ROUTING_DESCRIPTION,
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