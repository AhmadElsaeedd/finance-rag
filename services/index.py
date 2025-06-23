from pathlib import Path
from typing import Final

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings


class IndexService:
    
    class MetadataKeys:
        SOURCE: Final[str] = "source"
        FILENAME: Final[str] = "filename"
        FILE_TYPE: Final[str] = "file_type"
    
    __KNOWLEDGE_BASE_PATH: Final[Path] = Path("knowledge_base")
    
    @staticmethod
    def index_knowledge_base() -> InMemoryVectorStore:
        """
        Load text files from the knowledge_base directory and create an in-memory vector index.
        
        Returns:
            InMemoryVectorStore: The created vector store with indexed documents
        """
        if not IndexService.__KNOWLEDGE_BASE_PATH.exists():
            raise FileNotFoundError(f"Knowledge base directory not found: {IndexService.__KNOWLEDGE_BASE_PATH}")
        
        text_documents: Final[list[Document]] = IndexService._load_text_files(directory_path=IndexService.__KNOWLEDGE_BASE_PATH)
        
        if len(text_documents) == 0:
            raise ValueError("No text files found in the knowledge base directory")
        
        text_splitter: Final[RecursiveCharacterTextSplitter] = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
        )
        
        split_documents: Final[list[Document]] = text_splitter.split_documents(text_documents)
        
        embeddings: Final[OllamaEmbeddings] = OllamaEmbeddings(model="nomic-embed-text")
        
        return InMemoryVectorStore.from_documents(
            documents=split_documents,
            embedding=embeddings
        )
    
    @staticmethod
    def _load_text_files(*, directory_path: Path) -> list[Document]:
        """
        Load all text files from the specified directory and convert them to Document objects.
        """
        documents: list[Document] = []
        
        text_files: list[Path] = list(directory_path.glob("*.txt"))
        
        for file_path in text_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content: str = file.read()
                
                # Create metadata for the document
                document_metadata: dict[str, str] = {
                    IndexService.MetadataKeys.SOURCE: str(file_path),
                    IndexService.MetadataKeys.FILENAME: file_path.name,
                    IndexService.MetadataKeys.FILE_TYPE: "text",
                }
                
                document: Document = Document(
                    page_content=content,
                    metadata=document_metadata
                )
                
                documents.append(document)
                
            except Exception as e:
                print(f"Error loading file {file_path}: {e}")
                continue
        
        return documents