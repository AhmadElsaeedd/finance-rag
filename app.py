from typing import Any, Final

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import ChatOllama
from langgraph.graph.state import CompiledStateGraph

from models.state import State
from services.chat import ChatService
from services.graph import GraphService
from services.index import IndexService
from services.langsmith import LangSmithService
from services.rag import RAGService
from settings.variables import Variables


def get_model_name() -> str:
    """Get the model name from environment variable or use default."""
    if Variables.OLLAMA_MODEL is None:
        raise ValueError("OLLAMA_MODEL is not set in the environment variables")
    
    return Variables.OLLAMA_MODEL


def main() -> None:
    # Load environment variables from .env file
    load_dotenv()
    
    vector_store: Final[InMemoryVectorStore] = IndexService.index_knowledge_base()
    
    prompt: Final[PromptTemplate] = LangSmithService.get_prompt(prompt_id="rlm/rag-prompt")
    
    model_name: str = get_model_name()
    llm: Final[BaseChatModel] = ChatOllama(model=model_name)
    
    rag_service: Final[RAGService] = RAGService(
        vector_store=vector_store,
        prompt=prompt,
        llm=llm,
    )
    
    graph: Final[CompiledStateGraph] = GraphService.build(rag_service=rag_service)
    
    thread_id: Final[str] = "1"
    
    print("🚀 Investment RAG Assistant Started!")
    print("=" * 50)
    print(f"Using model: {model_name}")
    print("=" * 50)
    
    while True:
        user_input: str = ChatService.get_user_input()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye! Thanks for using Investment RAG Assistant.")
            break
        
        if not user_input:
            print("❌ Please enter a question or command.")
            continue
        
        try:
            result: Final[dict[str, Any]] = graph.invoke(
                input={"question": user_input},
                config={"configurable": {"thread_id": thread_id}},
            )
            
            serialized_result: Final[State] = State(**result)
            
            ChatService.display_response(state=serialized_result)
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again with a different question.")


if __name__ == "__main__":
    main()