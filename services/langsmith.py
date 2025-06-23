from typing import Final

from langchain_core.prompts import PromptTemplate
from langsmith import Client

from settings.variables import Variables


class LangSmithService:
    
    LANGSMITH_CLIENT: Final[Client] = Client(
        api_key=Variables.LANGSMITH_API_KEY
    )
    
    @classmethod
    def get_prompt(cls, *, prompt_id: str) -> PromptTemplate:
        return cls.LANGSMITH_CLIENT.pull_prompt(prompt_identifier=prompt_id)