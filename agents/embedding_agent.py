import chromadb
from chromadb.config import Settings
import numpy as np
import ollama  # <-- use Ollama client
import os

class EmbeddingAgent:
    def __init__(self, model_name="llama3:instruct"):
        # Store Ollama model name (e.g., "llama2", "mistral", "nomic-embed-text")
        self.model_name = model_name  

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path="./chroma_db")
        try:
            self.collection = self.client.get_collection("resources")
        except:
            self.collection = self.client.create_collection("resources")

    def get_embeddings(self, texts):
        """Generate embeddings using Ollama's local model"""
        embeddings = []
        for text in texts:
            response = ollama.embeddings(model=self.model_name, prompt=text)
            embeddings.append(np.array(response["embedding"]))
        return embeddings

    def add(self, docs):
        texts = [d["text"] for d in docs]
        ids = [d["id"] for d in docs]
        metadatas = [d["metadata"] for d in docs]

        # Generate embeddings using Ollama
        embeddings = self.get_embeddings(texts)

        # Add to ChromaDB
        self.collection.add(
            documents=texts,
            ids=ids,
            metadatas=metadatas,
            embeddings=embeddings
        )

    def search(self, query: str, n=5):
        # Generate embedding for the query
        query_embedding = self.get_embeddings([query])[0]

        return self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n
        )
