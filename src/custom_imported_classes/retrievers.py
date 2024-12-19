from langchain_community.retrievers.web_research import (
    WebResearchRetriever as BaseWebResearchRetriever,
    DEFAULT_LLAMA_SEARCH_PROMPT,
    DEFAULT_SEARCH_PROMPT
)
from pydantic import Field
from typing import Any
from langchain.chains import LLMChain
from langchain.chains.prompt_selector import ConditionalPromptSelector
from langchain.llms import LlamaCpp
from .search import FilteredGoogleSearchAPIWrapper
from .parsers import QuestionListOutputParser

class CustomWebResearchRetriever(BaseWebResearchRetriever):
    """Custom WebResearchRetriever that uses our FilteredGoogleSearchAPIWrapper"""
    
    search: FilteredGoogleSearchAPIWrapper = Field(..., description="Google Search API Wrapper")
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize with our custom search wrapper."""
        if not isinstance(kwargs.get('search'), FilteredGoogleSearchAPIWrapper):
            raise ValueError("search must be an instance of FilteredGoogleSearchAPIWrapper")
        super().__init__(**kwargs)
    
    @classmethod
    def from_llm(
        cls,
        vectorstore,
        llm,
        search: FilteredGoogleSearchAPIWrapper,
        **kwargs
    ):
        """Create WebResearchRetriever from LLM."""
        if not isinstance(search, FilteredGoogleSearchAPIWrapper):
            raise ValueError("search must be an instance of FilteredGoogleSearchAPIWrapper")
            
        # Create the default prompt selector
        if isinstance(llm, LlamaCpp):
            prompt_selector = ConditionalPromptSelector(
                default_prompt=DEFAULT_LLAMA_SEARCH_PROMPT,
                conditionals=[]
            )
        else:
            prompt_selector = ConditionalPromptSelector(
                default_prompt=DEFAULT_SEARCH_PROMPT,
                conditionals=[]
            )

        # Create the LLM chain
        llm_chain = LLMChain(
            llm=llm,
            prompt=prompt_selector.get_prompt(llm),
            output_parser=QuestionListOutputParser()
        )

        return cls(
            vectorstore=vectorstore,
            llm_chain=llm_chain,
            search=search,
            **kwargs
        ) 