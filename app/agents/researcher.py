from typing import List, Dict, Any, Tuple
from app.services.search_service import search_service

class ResearcherAgent:
    """Agent autonome chargé de l'exécution des recherches via Tavily et de la gestion des sources."""

    def execute_research(
        self,
        queries: List[str],
        depth: str = "standard",
        existing_sources: List[Dict[str, Any]] = None
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Exécute les requêtes de recherche, déduplique les URLs et enrichit la base documentaire."""
        if existing_sources is None:
            existing_sources = []

        existing_urls = {s.get("url") for s in existing_sources if s.get("url")}
        executed_queries = []
        new_sources = []

        for query in queries:
            query_str = query.strip()
            if not query_str:
                continue
            executed_queries.append(query_str)

        # Recherche par lot avec déduplication stricte
        collected = search_service.batch_search_and_deduplicate(
            queries=executed_queries,
            depth=depth,
            existing_urls=existing_urls
        )

        # Nettoyage et assainissement des sources (protection anti-prompt injection)
        for item in collected:
            clean_snippet = self._sanitize_text(item.get("snippet", ""))
            clean_title = self._sanitize_text(item.get("title", "Sans titre"))
            new_sources.append({
                "title": clean_title,
                "url": item.get("url", ""),
                "snippet": clean_snippet,
                "score": item.get("score", 0.0),
                "query": item.get("query", "")
            })

        all_sources = existing_sources + new_sources
        return all_sources, executed_queries

    def _sanitize_text(self, text: str) -> str:
        """Nettoie le texte web des tentatives potentielles d'injection."""
        if not text:
            return ""
        # Remplacer les délimiteurs sensibles ou balises suspectes
        cleaned = text.replace("<script", "&lt;script").replace("</script>", "&lt;/script&gt;")
        return cleaned[:2500]  # Limite de taille par extrait

researcher_agent = ResearcherAgent()
