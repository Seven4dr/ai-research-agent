import os
from typing import List, Dict, Any
from tavily import TavilyClient
from app.core.config import settings

class SearchService:
    """Service d'interrogation de l'API Tavily Search."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.TAVILY_API_KEY
        self.client = TavilyClient(api_key=self.api_key) if self.api_key else None

    def search(
        self,
        query: str,
        search_depth: str = "basic",
        max_results: int = 5,
        include_answer: bool = False
    ) -> List[Dict[str, Any]]:
        """Exécute une requête unique via Tavily et retourne les résultats filtrés."""
        if not self.client:
            raise ValueError("Clé API Tavily absente. Veuillez configurer TAVILY_API_KEY.")
            
        try:
            response = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_answer=include_answer
            )
            
            results = []
            for item in response.get("results", []):
                results.append({
                    "title": item.get("title", "Sans titre"),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", ""),
                    "score": item.get("score", 0.0),
                    "query": query
                })
            return results
        except Exception as e:
            # Enregistrement de l'erreur pour traitement par l'Agent
            raise RuntimeError(f"Erreur Tavily Search ({query}): {str(e)}")

    def batch_search_and_deduplicate(
        self,
        queries: List[str],
        depth: str = "standard",
        existing_urls: set = None
    ) -> List[Dict[str, Any]]:
        """Exécute un ensemble de requêtes et déduplique strictement par URL."""
        if existing_urls is None:
            existing_urls = set()
            
        config = settings.DEPTH_CONFIG.get(depth, settings.DEPTH_CONFIG["standard"])
        tavily_depth = config["tavily_depth"]
        per_query_limit = max(2, config["max_sources"] // max(1, len(queries)))
        
        all_results = []
        for q in queries:
            try:
                res = self.search(
                    query=q,
                    search_depth=tavily_depth,
                    max_results=per_query_limit
                )
                for item in res:
                    url = item.get("url", "").strip()
                    if url and url not in existing_urls:
                        existing_urls.add(url)
                        all_results.append(item)
            except Exception as e:
                # Tolérance aux pannes par requête
                continue
                
        return all_results

search_service = SearchService()
