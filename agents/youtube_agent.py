from googleapiclient.discovery import build
import os

class YouTubeAgent:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("Missing YouTube API key. Provide via parameter or YOUTUBE_API_KEY env var.")
        self.service = build("youtube", "v3", developerKey=self.api_key)

    def fetch(self, query: str, max_results: int = 10):
        """Fetch best educational videos sorted by view count and relevance"""
        # Add educational keywords to get tutorial/teaching videos
        educational_query = f"{query} tutorial OR {query} explained OR {query} course OR {query} lecture"
        
        # Search for videos with relevance and view count ordering
        req = self.service.search().list(
            q=educational_query,
            part="snippet",
            type="video",
            maxResults=max_results * 2,  # Get more to filter
            order="viewCount",  # Sort by most viewed
            videoDuration="medium",  # Prefer medium/long videos (better content)
            relevanceLanguage="en"
        )
        resp = req.execute()
        
        video_ids = [item["id"]["videoId"] for item in resp.get("items", [])]
        
        if not video_ids:
            return []
        
        # Get detailed video statistics
        stats_req = self.service.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(video_ids)
        )
        stats_resp = stats_req.execute()
        
        videos = []
        for item in stats_resp.get("items", []):
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})
            
            videos.append({
                "id": item["id"],
                "title": snippet.get("title", ""),
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "description": snippet.get("description", ""),
                "channel": snippet.get("channelTitle", ""),
                "viewCount": int(stats.get("viewCount", 0)),
                "likeCount": int(stats.get("likeCount", 0)),
                "duration": item.get("contentDetails", {}).get("duration", "")
            })
        
        # Sort by view count (already sorted, but ensure it)
        videos.sort(key=lambda x: x["viewCount"], reverse=True)
        
        # Return top max_results
        return videos[:max_results]