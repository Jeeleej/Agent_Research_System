import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_core.tools import tool
from tavily import TavilyClient

load_dotenv()

tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None

@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information. Returns Titles, URLs, and snippets."""
    if not tavily:
        return "Error: TAVILY_API_KEY is not configured."
    try:
        results = tavily.search(query=query, max_results=5)
        out = []
        for r in results.get("results", []):
            url = r.get("url", "").strip()
            title = r.get("title", "").strip()
            snippet = r.get("content", "").strip()[:300]
            out.append(f"Source URL: {url}\nTitle: {title}\nSummary: {snippet}")
        return "\n\n---\n\n".join(out)
    except Exception as e:
        return f"Error executing search: {str(e)}"


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(
            url, timeout=8, headers={"User-Agent": "Mozilla/5.0"}
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:5000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"