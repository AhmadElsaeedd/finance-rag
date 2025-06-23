from typing import Final

from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.prompt_values import PromptValue
from langchain_core.prompts import PromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from pydantic import BaseModel


class State(BaseModel):
    question: str | None = None
    context: list[Document] | None = None
    answer: str | None = None


class RAGService:
    
    def __init__(
        self,
        *,
        vector_store: InMemoryVectorStore,
        prompt: PromptTemplate,
        llm: BaseChatModel,
    ):
        self.vector_store = vector_store
        self.prompt = prompt
        self.llm = llm
    
    def retrieve(self, *, state: State) -> State:
        if state.question is None:
            raise ValueError("Question is required to retrieve context.")
        
        retrieved_docs: Final[list[Document]] = self.vector_store.similarity_search(
            query=state.question,
        )
        
        return State(
            question=state.question,
            context=retrieved_docs,
            answer=state.answer,
        )


    def generate(self, *, state: State) -> State:
        if state.context is None or len(state.context) == 0 or state.question is None:
            raise ValueError("Context and question are required to generate an answer.")
        
        documents_content: Final[str] = "\n\n".join(document.page_content for document in state.context)
        
        target_prompt: Final[PromptValue] = self.prompt.invoke(
            input={
                "question": state.question,
                "context": documents_content,
            },
        )
        
        response: Final[BaseMessage] = self.llm.invoke(input=target_prompt)
        
        return State(
            question=state.question,
            context=state.context,
            answer=response.content,
        )