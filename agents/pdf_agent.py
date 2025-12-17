import requests
from PyPDF2 import PdfReader
import io
import ollama

class PDFAgent:
    def __init__(self, model_name="llama3:instruct"):
        self.model_name = model_name

    def fetch(self, query: str, max_results: int = 10):
        """Search for research papers using Semantic Scholar Graph API with fallback strategies"""
        papers = []
        
        # Strategy 1: Direct search
        try:
            papers = self._search_semantic_scholar(query, max_results)
            if papers:
                print(f"Found {len(papers)} papers using direct search")
                return papers
        except Exception as e:
            print(f"Direct search failed: {e}")
        
        # Strategy 2: Try with broader search terms
        if not papers:
            try:
                broader_query = f"{query} research OR {query} survey OR {query} review"
                papers = self._search_semantic_scholar(broader_query, max_results)
                if papers:
                    print(f"Found {len(papers)} papers using broader search")
                    return papers
            except Exception as e:
                print(f"Broader search failed: {e}")
        
        # Strategy 3: Try arXiv as fallback
        if not papers:
            try:
                papers = self._search_arxiv(query, max_results)
                if papers:
                    print(f"Found {len(papers)} papers using arXiv fallback")
                    return papers
            except Exception as e:
                print(f"arXiv fallback failed: {e}")
        
        print(f"No papers found for query: {query}")
        return []
    
    def _search_semantic_scholar(self, query: str, max_results: int):
        """Search Semantic Scholar API"""
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": max_results,
            "fields": "title,url,abstract,authors,year,citationCount,openAccessPdf"
        }
        
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json() or {}
        items = data.get("data", []) or data.get("papers", [])

        papers = []
        for item in items:
            open_pdf = None
            oapdf = item.get("openAccessPdf") or {}
            if isinstance(oapdf, dict):
                open_pdf = oapdf.get("url")

            authors = []
            raw_authors = item.get("authors") or []
            for a in raw_authors:
                name = a.get("name") if isinstance(a, dict) else None
                if name:
                    authors.append(name)

            papers.append({
                "title": item.get("title", ""),
                "summary": item.get("abstract", ""),
                "pdf_url": open_pdf or item.get("url", ""),
                "authors": authors,
                "year": item.get("year"),
                "citationCount": item.get("citationCount", 0)
            })

        return papers
    
    def _search_arxiv(self, query: str, max_results: int):
        """Fallback to arXiv API"""
        import urllib.parse
        
        base_url = "http://export.arxiv.org/api/query"
        search_query = urllib.parse.quote(query)
        url = f"{base_url}?search_query=all:{search_query}&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"
        
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        
        # Parse XML response
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.content)
        
        # Define namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        papers = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns)
            summary = entry.find('atom:summary', ns)
            published = entry.find('atom:published', ns)
            
            # Get PDF link
            pdf_url = None
            for link in entry.findall('atom:link', ns):
                if link.get('title') == 'pdf':
                    pdf_url = link.get('href')
                    break
            
            # Get authors
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns)
                if name is not None and name.text:
                    authors.append(name.text)
            
            # Extract year from published date
            year = None
            if published is not None and published.text:
                year = int(published.text[:4])
            
            papers.append({
                "title": title.text.strip() if title is not None else "",
                "summary": summary.text.strip() if summary is not None else "",
                "pdf_url": pdf_url or "",
                "authors": authors,
                "year": year,
                "citationCount": 0  # arXiv doesn't provide citation count
            })
        
        return papers

    def extract_text(self, pdf_url: str, max_pages: int = 3):
        """Extract text from PDF URL"""
        try:
            # Download PDF
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            # Read PDF
            pdf_file = io.BytesIO(response.content)
            reader = PdfReader(pdf_file)
            
            # Extract text from first few pages
            text = ""
            for i, page in enumerate(reader.pages[:max_pages]):
                text += page.extract_text() + "\n"
            
            return text[:2000]  # Limit text length
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""

    def summarize_with_llm(self, text: str):
        """Summarize text using Ollama LLM"""
        try:
            prompt = f"Summarize this academic text in 2-3 sentences:\n\n{text[:1000]}"
            response = ollama.chat(model=self.model_name, messages=[
                {"role": "user", "content": prompt}
            ])
            return response["message"]["content"].strip()
        except Exception as e:
            print(f"Error summarizing with LLM: {e}")
            return text[:200] + "..." if len(text) > 200 else text