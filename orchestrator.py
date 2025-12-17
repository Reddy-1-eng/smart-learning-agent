import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from query_agent import QueryAgent
from youtube_agent import YouTubeAgent
from pdf_agent import PDFAgent
from embedding_agent import EmbeddingAgent

import uuid

class Orchestrator:
    def __init__(self, model_path="./models/llama-2-7b-chat-hf"):
        self.query_agent = QueryAgent(model_path)
        self.youtube_agent = YouTubeAgent()
        self.pdf_agent = PDFAgent(model_path)
        self.embedding_agent = EmbeddingAgent(model_path)

    def run(self, topic: str):
        clean_topic = self.query_agent.process(topic)

        # Fetch resources
        videos = self.youtube_agent.fetch(clean_topic, 10)
        pdfs = self.pdf_agent.fetch(clean_topic, 10)

        # Prepare docs for embeddings
        docs = []
        for v in videos:
            docs.append({
                "id": str(uuid.uuid4()),
                "text": v["title"] + " " + v["description"],
                "metadata": {"type": "video", "url": v["url"], "title": v["title"]}
            })
        for p in pdfs:
            # extract some text from PDF
            pdf_text = self.pdf_agent.extract_text(p["pdf_url"])
            docs.append({
                "id": str(uuid.uuid4()),
                "text": p["title"] + " " + p["summary"] + " " + pdf_text,
                "metadata": {"type": "pdf", "url": p["pdf_url"], "title": p["title"]}
            })

        # Store embeddings
        if docs:
            self.embedding_agent.add(docs)

        return {"topic": clean_topic, "videos": videos, "pdfs": pdfs}

    def semantic_search(self, query: str):
        return self.embedding_agent.search(query)
