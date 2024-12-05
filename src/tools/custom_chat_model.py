import logging
from operator import itemgetter
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    Type,
    Union,
    cast,
)
from uuid import uuid4
import json

import requests
from langchain.schema import AIMessage, ChatGeneration, ChatResult, HumanMessage
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import LanguageModelInput
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessageChunk,
    BaseMessage,
    SystemMessage,
    ToolCall,
    ToolMessage,
)
from langchain_core.messages.tool import tool_call
from langchain_core.output_parsers import (
    JsonOutputParser,
    PydanticOutputParser,
)
from langchain_core.output_parsers.base import OutputParserLike
from langchain_core.output_parsers.openai_tools import (
    JsonOutputKeyToolsParser,
    PydanticToolsParser,
)
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.runnables.base import RunnableMap
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_core.utils.pydantic import is_basemodel_subclass
from pydantic import BaseModel, Field

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
_logger = logging.getLogger(__name__)


def _is_pydantic_class(obj: Any) -> bool:
    return isinstance(obj, type) and is_basemodel_subclass(obj)


def _convert_messages_to_redpill_messages(
    messages: List[BaseMessage],
) -> List[Dict[str, Any]]:
    """Convert LangChain messages to Red Pill AI format."""
    redpill_messages = []
    msg: Dict[str, Any]
    for message in messages:
        # Base structure for each message
        msg = {
            "role": "",
            "content": message.content if isinstance(message.content, str) else "",
        }

        # Determine role and additional fields based on message type
        if isinstance(message, HumanMessage):
            msg["role"] = "user"
        elif isinstance(message, AIMessage):
            msg["role"] = "assistant"
            # If the AIMessage includes tool calls, format them as needed
            if message.tool_calls:
                tool_calls = [
                    {"name": tool_call["name"], "arguments": tool_call["args"]}
                    for tool_call in message.tool_calls
                ]
                msg["tool_calls"] = tool_calls
        elif isinstance(message, SystemMessage):
            msg["role"] = "system"
        elif isinstance(message, ToolMessage):
            msg["role"] = "tool"
            msg["tool_call_id"] = (
                message.tool_call_id
            )  # Use tool_call_id if it's a ToolMessage

        # Add the formatted message to the list
        redpill_messages.append(msg)

    return redpill_messages


def _get_tool_calls_from_response(response: requests.Response) -> List[ToolCall]:
    """Get tool calls from ollama response."""
    tool_calls = []
    if "tool_calls" in response.json()["result"]:
        for tc in response.json()["result"]["tool_calls"]:
            tool_calls.append(
                tool_call(
                    id=str(uuid4()),
                    name=tc["name"],
                    args=tc["arguments"],
                )
            )
    return tool_calls


class RedPillChatModel(BaseChatModel):
    """Custom chat model for Red Pill AI"""

    api_key: str = Field(...)
    model: str = Field(...)

    def __init__(self, **kwargs: Any) -> None:
        """Initialize with necessary credentials."""
        super().__init__(**kwargs)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a response based on the messages provided."""
        formatted_messages = _convert_messages_to_redpill_messages(messages)
        
        url = "https://api.red-pill.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": kwargs.get("temperature", 0)
        }
        
        if "tools" in kwargs:
            payload["tools"] = kwargs["tools"] if isinstance(kwargs["tools"], list) else [kwargs["tools"]]
        
        _logger.info(f"Sending request to Red Pill AI: {payload}")
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise ValueError(f"Error from API: {response.status_code} - {response.text}")
        
        response_data = response.json()
        
        # Ensure we have a valid content string
        content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if content is None:
            content = ""  # Ensure content is always a string
        
        tool_calls = []
        
        # Check for tool calls in the response
        if "tool_calls" in response_data.get("choices", [{}])[0].get("message", {}):
            tool_calls_data = response_data["choices"][0]["message"]["tool_calls"]
            for tc in tool_calls_data:
                # Parse the arguments string into a dictionary if it's a string
                args = tc["function"]["arguments"]
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        args = {}  # Fallback if JSON parsing fails
                
                tool_calls.append(
                    tool_call(
                        id=str(uuid4()),
                        name=tc["function"]["name"],
                        args=args,  # Now guaranteed to be a dictionary
                    )
                )
        
        ai_message = AIMessage(
            content=content,  # Now guaranteed to be a string
            tool_calls=tool_calls if tool_calls else None  # Only include if we have tool calls
        )
        
        return ChatResult(generations=[ChatGeneration(message=ai_message)])

    def bind_tools(
        self,
        tools: Sequence[Union[Dict[str, Any], Type, Callable[..., Any], BaseTool]],
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, BaseMessage]:
        """Bind tools for use in model generation."""
        formatted_tools = [convert_to_openai_tool(tool) for tool in tools]
        return super().bind(tools=formatted_tools, **kwargs)

    def with_structured_output(
        self,
        schema: Union[Dict, Type[BaseModel]],
        *,
        include_raw: bool = False,
        method: Optional[Literal["json_mode", "function_calling"]] = "function_calling",
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, Union[Dict, BaseModel]]:
        """Model wrapper that returns outputs formatted to match the given schema."""

        if kwargs:
            raise ValueError(f"Received unsupported arguments {kwargs}")
        is_pydantic_schema = _is_pydantic_class(schema)
        if method == "function_calling":
            if schema is None:
                raise ValueError(
                    "schema must be specified when method is 'function_calling'. "
                    "Received None."
                )
            tool_name = convert_to_openai_tool(schema)["function"]["name"]
            llm = self.bind_tools([schema], tool_choice=tool_name)
            if is_pydantic_schema:
                output_parser: OutputParserLike = PydanticToolsParser(
                    tools=[schema],  # type: ignore[list-item]
                    first_tool_only=True,  # type: ignore[list-item]
                )
            else:
                output_parser = JsonOutputKeyToolsParser(
                    key_name=tool_name, first_tool_only=True
                )
        elif method == "json_mode":
            llm = self.bind(response_format={"type": "json_object"})
            output_parser = (
                PydanticOutputParser(pydantic_object=schema)  # type: ignore[type-var, arg-type]
                if is_pydantic_schema
                else JsonOutputParser()
            )
        else:
            raise ValueError(
                f"Unrecognized method argument. Expected one of 'function_calling' or "
                f"'json_mode'. Received: '{method}'"
            )

        if include_raw:
            parser_assign = RunnablePassthrough.assign(
                parsed=itemgetter("raw") | output_parser, parsing_error=lambda _: None
            )
            parser_none = RunnablePassthrough.assign(parsed=lambda _: None)
            parser_with_fallback = parser_assign.with_fallbacks(
                [parser_none], exception_key="parsing_error"
            )
            return RunnableMap(raw=llm) | parser_with_fallback
        else:
            return llm | output_parser

    @property
    def _llm_type(self) -> str:
        """Return the type of the LLM (for Langchain compatibility)."""
        return "redpill-ai"