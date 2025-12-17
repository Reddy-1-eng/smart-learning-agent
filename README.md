# Smart Learning Agent

An AI-powered educational platform that finds and curates learning resources from YouTube videos and research papers, enhanced with semantic search capabilities.

## Features

- **YouTube Integration**: Search and fetch educational videos
- **Research Papers**: Find relevant academic papers from arXiv
- **AI-Powered Search**: Semantic search using embeddings
- **Fallback System**: Works even when external APIs are unavailable
- **Modern UI**: Beautiful, responsive web interface

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root with:

```env
# YouTube API Configuration
YOUTUBE_API_KEY=your_youtube_api_key_here

# Ollama Configuration (optional)
OLLAMA_MODEL=llama3:instruct

# ChromaDB Configuration (optional)
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

### 3. Get YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Add the API key to your `.env` file

### 4. Install Ollama (Optional)

For full AI functionality:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the model
ollama pull llama3:instruct
```

### 5. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## How It Works

1. **Query Processing**: User enters a topic, which is processed and refined by the Query Agent
2. **Resource Fetching**: 
   - YouTube Agent searches for relevant videos
   - PDF Agent searches arXiv for research papers
3. **Content Processing**: PDFs are processed to extract text content
4. **Embedding Storage**: All content is stored with embeddings for semantic search
5. **Results Display**: Resources are displayed in a beautiful, organized interface
6. **Semantic Search**: Users can ask questions about the content using AI-powered search

## Fallback System

The application includes a robust fallback system:
- If YouTube API is unavailable, sample videos are shown
- If arXiv API fails, sample research papers are displayed
- If Ollama is not available, basic functionality still works
- If ChromaDB fails, semantic search uses fallback results

## API Endpoints

- `GET /` - Main application interface
- `POST /api/search` - Search for learning resources
- `POST /api/semantic_search` - Perform semantic search
- `GET /api/health` - Health check endpoint

## Project Structure

```
smart-learning-agent/
├── agents/
│   ├── query_agent.py      # Topic processing and refinement
│   ├── youtube_agent.py    # YouTube video search
│   ├── pdf_agent.py        # Research paper search and processing
│   └── embedding_agent.py  # Semantic search and embeddings
├── templates/
│   └── index.html          # Web interface
├── static/
│   └── style.css           # Styling
├── app.py                  # Main Flask application
├── orchestrator.py         # Agent coordination (legacy)
└── requirements.txt        # Python dependencies
```

## Troubleshooting

### Common Issues

1. **YouTube API Error**: Make sure your API key is valid and YouTube Data API v3 is enabled
2. **Ollama Connection Error**: Install Ollama and pull the required model
3. **ChromaDB Error**: The app will work with fallback data if ChromaDB fails
4. **PDF Processing Error**: Some PDFs may not be processable, but the app will continue

### Logs

Check the console output for detailed error messages and status updates. The application provides clear feedback about which components are working.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
