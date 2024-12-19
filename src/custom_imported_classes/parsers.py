from langchain_core.output_parsers import BaseOutputParser
from typing import List
import re

class QuestionListOutputParser(BaseOutputParser[List[str]]):
    """Output parser for a list of numbered questions."""

    def parse(self, text: str) -> List[str]:
        """Parse numbered questions from text."""
        lines = re.findall(r"\d+\..*?(?:\n|$)", text)
        return lines 