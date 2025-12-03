import os
import glob
from typing import List, Tuple, Optional
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

load_dotenv()

def get_openai_api_key() -> str:
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("OPENAI_API_KEY", "")

def load_brand_docs(folder: str = "data/brand_cases") -> List[Document]:
    docs: List[Document] = []
    if not os.path.exists(folder):
        return docs

    for path in glob.glob(os.path.join(folder, "*")):
        if path.endswith((".txt", ".md")):
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            docs.append(
                Document(
                    page_content=text, metadata={"source": os.path.basename(path)}
                )
            )
    return docs

class BrandRAG:
    def __init__(
        self, folder: str = "data/brand_cases", openai_api_key: Optional[str] = None
    ):
        self.folder = folder
        self.openai_api_key = openai_api_key or get_openai_api_key()
        self.vectorstore: Optional[FAISS] = None
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?"],
        )
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)

        docs = load_brand_docs(folder)
        if docs:
            split_docs = self.splitter.split_documents(docs)
            self.vectorstore = FAISS.from_documents(split_docs, self.embeddings)
        else:
            print(f"[BrandRAG] No documents found in {folder}. RAG will be disabled.")

    def add_document(self, text: str, metadata: Optional[dict] = None) -> None:
        """Add a new document to the vector store."""
        doc = Document(
            page_content=text,
            metadata=metadata or {"source": "uploaded_file"}
        )
        split_docs = self.splitter.split_documents([doc])
        
        if self.vectorstore is None:
            # Create new vectorstore if it doesn't exist
            self.vectorstore = FAISS.from_documents(split_docs, self.embeddings)
        else:
            # Add to existing vectorstore
            self.vectorstore.add_documents(split_docs)

    def add_file(self, file_content: bytes, filename: str) -> None:
        """Add a file to the vector store from bytes."""
        try:
            text = file_content.decode("utf-8")
            self.add_document(text, metadata={"source": filename})
        except UnicodeDecodeError:
            print(f"[BrandRAG] Warning: Could not decode {filename} as UTF-8. Skipping.")

    def search(self, query: str, k: int = 4) -> Tuple[str, List[Document]]:
        if self.vectorstore is None:
            return "", []

        results = self.vectorstore.similarity_search(query, k=k)
        context = "\n\n---\n\n".join(
            [
                f"[DOC {i+1} from {r.metadata.get('source', 'unknown')}]\n{r.page_content}"
                for i, r in enumerate(results)
            ]
        )
        return context, results

