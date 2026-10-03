from __future__ import annotations
import os

def web_search(query: str, max_results: int = 5) -> dict:
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        return {"query": query, "results": [], "answer": "TAVILY_API_KEY is not configured; web search was not executed."}
    from tavily import TavilyClient
    response = TavilyClient(api_key=key).search(query=query, max_results=max_results, search_depth="advanced")
    return {"query": query, "results": response.get("results", []), "answer": response.get("answer", "")}
