# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import Settings, StorageContext
import time
import os
from dotenv import load_dotenv
import numpy as np

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

        self.cached_query = []
        self.query_look_up = {}

    def search_top_k(self, text: str, top_k: int, threshold: float):

        top_k_results = []
        inc = 0
        nodes = self.retriever.retrieve(text)

        for node in nodes:
            if inc < top_k and threshold < node.score:
                top_k_results.append({"message":node.text})
                inc += 1

        if len(self.cached_query) > 10:  
            del_text, del_enc_text = self.cached_query.pop(0)
            del self.query_look_up[del_text]

        encoded_text = self.embed_model.get_text_embedding(text)   
        self.cached_query.append([text, encoded_text])
        self.query_look_up[text] = nodes

        return top_k_results

    def cosine_similarity(self, vector_a, vector_b):
        vector_a = np.array(vector_a)
        vector_b = np.array(vector_b)

        dot_product = np.dot(vector_a, vector_b)
        magnitude_a = np.linalg.norm(vector_a)
        magnitude_b = np.linalg.norm(vector_b)

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0  # Handle zero vectors

        return dot_product / (magnitude_a * magnitude_b)
    
    def cached_search(self, text:str, top_k:int, threshold: float):

        top_k_results = []
        inc = 0
        temp_score = (0.0, None)
        
        if len(self.cached_query) != 0:
            encoded_text = self.embed_model.get_text_embedding(text)
            for row in self.cached_query:
                score = float(self.cosine_similarity(encoded_text, row[1]))
                if  score > 0.9 and score > temp_score[0]:
                    temp_score = (score, row[0])
            
            if temp_score[1] is not None:
                nodes = self.query_look_up[temp_score[1]]

                for node in nodes:
                    if inc < top_k and threshold < node.score:
                        top_k_results.append({"message":node.text})
                        inc += 1

        return top_k_results