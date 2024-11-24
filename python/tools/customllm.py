"""
RedPillLLM.py

Defines a RedPillLLM class for interacting with the RedPill API.
"""
from typing import Any, Dict, Iterator, List, Mapping, Optional

import requests
import json
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk


class RedPillLLM(LLM):

    api_key: str = ""
    """API key for authentication."""
    model: str = ""
    """Name of the model to use."""
    temperature: float = 0
    """Temperature setting for randomness in the model's responses."""


    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:

        # Prepare the API request
        url = "https://api.red-pill.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature
        }

        # Send the request
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code != 200:
            raise ValueError(
                f"Error in API call: {response.status_code}, {response.text}"
            )
        
        # Parse the response
        response_data = response.json()
        generated_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")

        return generated_text

    def _llm_type(self) -> str:
        """
        Get the type of language model used by this LLM. Used for logging purposes.
        """
        return "custom"