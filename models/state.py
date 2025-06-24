from langchain_core.documents import Document
from pydantic import BaseModel


class State(BaseModel):
    question: str | None = None
    context: list[Document] | None = None
    answer: str | None = None