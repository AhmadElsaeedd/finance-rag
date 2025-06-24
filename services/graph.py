

from typing import Final

from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from models.state import State
from services.rag import RAGService


class GraphService:
    
    __RETRIEVE_NODE: Final[str] = "retrieve"
    
    @staticmethod
    def build(*, rag_service: RAGService) -> CompiledStateGraph:
        graph_builder: Final[StateGraph] = StateGraph(
            state_schema=State,
        ).add_sequence(
            nodes=[rag_service.retrieve, rag_service.generate],
        )
        
        graph_builder.add_edge(
            start_key=START,
            end_key=GraphService.__RETRIEVE_NODE,
        )
        
        return graph_builder.compile()