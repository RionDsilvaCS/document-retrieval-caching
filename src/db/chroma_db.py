__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import Settings, StorageContext
import time
import os
from dotenv import load_dotenv

load_dotenv()

Settings.llm = None

class UploadStore:
    def __init__(self) -> None:

        self.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
                
        self.chroma_client = chromadb.HttpClient(host="localhost", port=8000)
        self.chroma_collection = self.chroma_client.get_or_create_collection(os.getenv("COLLECTION_NAME"))
        vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        self.storage_context = StorageContext.from_defaults(vector_store=vector_store)
        self.path = ""

    def upload(self) -> bool:
        self.documents = SimpleDirectoryReader(self.path).load_data()
        index = VectorStoreIndex.from_documents(
            self.documents, storage_context=self.storage_context, embed_model=self.embed_model
        )

        return True
    
class SearchStore:
    def __init__(self) -> None:

        self.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
                
        self.chroma_client = chromadb.HttpClient(host="localhost", port=8000)
        self.chroma_collection = self.chroma_client.get_or_create_collection(os.getenv("COLLECTION_NAME"))
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)

        self.index = VectorStoreIndex.from_vector_store(
            self.vector_store,
            embed_model=self.embed_model,
        )

        self.retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=12,
        )

    def search_top_k(self, text: str, top_k: int, threshold: float):
        start = time.time()

        top_k_results = []
        inc = 0
        nodes = self.retriever.retrieve(text)

        for node in nodes:
            if inc < top_k and threshold < node.score:
                top_k_results.append({"message":node.text})
                inc += 1
        
        inf_time = float(time.time() - start)

        return top_k_results, inf_time

