from pydantic import BaseModel, ConfigDict, model_validator
from typing import Optional, Dict, List, Any
from langchain.utils import get_from_dict_or_env

class FilteredGoogleSearchAPIWrapper(BaseModel):
    """Wrapper for Google Search API with YouTube filtering."""
    
    search_engine: Any = None  #: :meta private:
    google_api_key: Optional[str] = None
    google_cse_id: Optional[str] = None
    k: int = 10
    siterestrict: bool = False

    model_config = ConfigDict(
        extra="forbid",
    )

    def _google_search_results(self, search_term: str, **kwargs: Any) -> List[dict]:
        cse = self.search_engine.cse()
        if self.siterestrict:
            cse = cse.siterestrict()
        res = cse.list(q=search_term, cx=self.google_cse_id, **kwargs).execute()
        return res.get("items", [])

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        google_api_key = get_from_dict_or_env(
            values, "google_api_key", "GOOGLE_API_KEY"
        )
        google_cse_id = get_from_dict_or_env(
            values, "google_cse_id", "GOOGLE_CSE_ID"
        )

        try:
            from googleapiclient.discovery import build
        except ImportError:
            raise ImportError(
                "google-api-python-client is not installed. "
                "Please install it with `pip install google-api-python-client"
                ">=2.100.0`"
            )

        return {
            **values,
            "google_api_key": google_api_key,
            "google_cse_id": google_cse_id,
            "search_engine": build("customsearch", "v1", developerKey=google_api_key)
        }

    def results(self, query: str, num_results: int, search_params: Optional[Dict[str, str]] = None) -> List[Dict]:
        """Run query through GoogleSearch and return metadata."""
        metadata_results = []
        results = self._google_search_results(
            query, num=num_results, **(search_params or {})
        )
        if len(results) == 0:
            return [{"Result": "No good Google Search Result was found"}]
            
        
        websites_to_ignore = ['https://www.youtube.com', 'https://www.google.com']
        for result in results:
            if not any(result.get('link', '').startswith(website) for website in websites_to_ignore):
                metadata_result = {
                    "title": result["title"],
                    "link": result["link"],
                }
                if "snippet" in result:
                    metadata_result["snippet"] = result["snippet"]
                metadata_results.append(metadata_result)
        
        if not metadata_results:
            return [{"Result": "No good Google Search Result was found"}]
            
        return metadata_results

    def run(self, query: str) -> str:
        """Run query through GoogleSearch and parse result."""
        snippets = []
        results = self._google_search_results(query, num=self.k)
        if len(results) == 0:
            return "No good Google Search Result was found"
        for result in results:
            if "snippet" in result:
                snippets.append(result["snippet"])

        return " ".join(snippets) 