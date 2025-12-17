from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add agents directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from query_agent import QueryAgent
from youtube_agent import YouTubeAgent
from pdf_agent import PDFAgent
from embedding_agent import EmbeddingAgent

class Orchestrator:
    def __init__(self, model_name="llama3:instruct"):
        """Initialize all agents with error handling"""
        self.model_name = model_name
        
        try:
            self.query_agent = QueryAgent(model_name)
            print("✓ Query agent initialized")
        except Exception as e:
            print(f"✗ Query agent failed: {e}")
            self.query_agent = None

        try:
            self.youtube_agent = YouTubeAgent(os.getenv("YOUTUBE_API_KEY"))
            print("✓ YouTube agent initialized")
        except Exception as e:
            print(f"✗ YouTube agent failed: {e}")
            self.youtube_agent = None

        try:
            self.pdf_agent = PDFAgent(model_name)
            print("✓ PDF agent initialized")
        except Exception as e:
            print(f"✗ PDF agent failed: {e}")
            self.pdf_agent = None

        try:
            self.embedding_agent = EmbeddingAgent(model_name)
            print("✓ Embedding agent initialized")
        except Exception as e:
            print(f"✗ Embedding agent failed: {e}")
            self.embedding_agent = None

    def run(self, topic: str):
        """Main orchestration method with fallback handling"""
        try:
            # Use the original topic directly without query agent processing
            clean_topic = topic.strip()
            print(f"Searching for: {clean_topic}")

            # Fetch resources using live APIs only
            videos = []
            pdfs = []

            if self.youtube_agent:
                try:
                    videos = self.youtube_agent.fetch(clean_topic, 10)
                    print(f"Found {len(videos)} YouTube videos")
                except Exception as e:
                    print(f"YouTube fetch error: {e}")
                    videos = []
            else:
                videos = []

            if self.pdf_agent:
                try:
                    pdfs = self.pdf_agent.fetch(clean_topic, 10)
                    print(f"Found {len(pdfs)} PDF papers")
                except Exception as e:
                    print(f"PDF fetch error: {e}")
                    pdfs = []
            else:
                pdfs = []

            # Prepare docs for embeddings if embedding agent is available
            if self.embedding_agent and (videos or pdfs):
                try:
                    docs = []
                    for v in videos:
                        docs.append({
                            "id": str(uuid.uuid4()),
                            "text": v["title"] + " " + v["description"],
                            "metadata": {"type": "video", "url": v["url"], "title": v["title"]}
                        })
                    
                    for p in pdfs:
                        # Extract some text from PDF if possible
                        pdf_text = ""
                        if hasattr(self.pdf_agent, 'extract_text'):
                            try:
                                pdf_text = self.pdf_agent.extract_text(p["pdf_url"])
                            except:
                                pdf_text = "[Could not extract text]"
                        
                        docs.append({
                            "id": str(uuid.uuid4()),
                            "text": p["title"] + " " + p["summary"] + " " + pdf_text,
                            "metadata": {"type": "pdf", "url": p["pdf_url"], "title": p["title"]}
                        })

                    # Store embeddings
                    if docs:
                        self.embedding_agent.add(docs)
                        print(f"Added {len(docs)} documents to embedding store")
                        
                except Exception as e:
                    print(f"Embedding storage error: {e}")

            return {"topic": clean_topic, "videos": videos, "pdfs": pdfs}

        except Exception as e:
            print(f"Orchestrator run error: {e}")
            return {
                "topic": topic,
                "videos": [],
                "pdfs": [],
                "error": str(e)
            }

    def semantic_search(self, query: str):
        """Perform semantic search with fallback"""
        if self.embedding_agent:
            try:
                return self.embedding_agent.search(query)
            except Exception as e:
                print(f"Semantic search error: {e}")
                return {"documents": [[]], "metadatas": [[]]}
        else:
            return {"documents": [[]], "metadatas": [[]]}

    def _get_fallback_videos(self, topic: str):
        """Fallback video data when YouTube API is unavailable"""
        return [
            {
                "id": "fallback1",
                "title": f"{topic} - Introduction and Overview",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "description": f"A comprehensive introduction to {topic} covering fundamental concepts and practical applications.",
                "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
                "channel": "Educational Channel",
                "published_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": "fallback2", 
                "title": f"Advanced {topic} Techniques",
                "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
                "description": f"Deep dive into advanced {topic} methodologies and best practices.",
                "thumbnail": "https://img.youtube.com/vi/jNQXAC9IVRw/maxresdefault.jpg",
                "channel": "Tech Academy",
                "published_at": "2024-01-02T00:00:00Z"
            }
        ]

    def _get_fallback_pdfs(self, topic: str):
        """Fallback PDF data when arXiv API is unavailable"""
        return [
            {
                "id": "fallback-pdf-1",
                "title": f"A Comprehensive Survey of {topic}",
                "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
                "summary": f"This paper provides a comprehensive overview of {topic}, covering theoretical foundations and practical implementations.",
                "authors": ["Research Team", "Academic Institution"]
            },
            {
                "id": "fallback-pdf-2",
                "title": f"Recent Advances in {topic}",
                "pdf_url": "https://arxiv.org/pdf/1512.03385.pdf", 
                "summary": f"An analysis of recent developments and breakthrough techniques in {topic} research.",
                "authors": ["Leading Researcher", "University Lab"]
            }
        ]

    def _get_fallback_semantic_results(self, query: str):
        """Fallback semantic search results"""
        return {
            "documents": [[
                f"Semantic search result for '{query}': This is a comprehensive overview of the topic.",
                f"Related concept to '{query}': Key principles and methodologies explained.",
                f"Advanced topics in '{query}': Latest research and developments."
            ]],
            "metadatas": [[
                {"url": "https://example.com/resource1", "title": f"{query} - Overview", "type": "article"},
                {"url": "https://example.com/resource2", "title": f"{query} - Concepts", "type": "tutorial"},
                {"url": "https://example.com/resource3", "title": f"{query} - Advanced", "type": "research"}
            ]]
        }

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize orchestrator
orchestrator = Orchestrator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        result = orchestrator.run(topic)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/semantic_search', methods=['POST'])
def semantic_search():
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        result = orchestrator.semantic_search(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "message": "Smart Learning Agent is running"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
