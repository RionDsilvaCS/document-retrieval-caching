import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings, StorageContext

Settings.llm = None

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

chroma_client = chromadb.HttpClient(host="localhost", port=8000)

print("Starting...")

chroma_collection = chroma_client.get_or_create_collection("cook_book")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

PATH = "./data/"

documents = SimpleDirectoryReader(PATH).load_data()
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context, embed_model=embed_model
)

print("Done...")