import sys
from pathlib import Path
from dotenv import load_dotenv

# Ajout du chemin racine
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.config import settings

def test_tavily_connection():
    """Vérifie la validité de la clé Tavily."""
    print("Test de connexion Tavily Search API...")
    try:
        from app.services.search_service import search_service
        results = search_service.search("LangGraph Python multi-agent", max_results=2)
        print(f"[SUCCES] Tavily a renvoyé {len(results)} résultats.")
        for r in results:
            print(f"  - {r.get('title')} ({r.get('url')})")
        return True
    except Exception as e:
        print(f"[ERREUR] Échec Tavily : {e}")
        return False

def test_gemini_connection():
    """Vérifie la validité de l'accès Gemini / Vertex AI."""
    print("\nTest de connexion Google Gemini API...")
    try:
        from app.services.llm_service import llm_service
        reply = llm_service.generate_text("Réponds brièvement en 1 mot : OK")
        print(f"[SUCCES] Gemini a répondu : {reply.strip()}")
        return True
    except Exception as e:
        print(f"[ERREUR] Échec Gemini : {e}")
        return False

if __name__ == "__main__":
    tavily_ok = test_tavily_connection()
    gemini_ok = test_gemini_connection()
    if tavily_ok and gemini_ok:
        print("\nToutes les connexions API sont valides et opérationnelles.")
    else:
        print("\nCertaines connexions ont échoué. Vérifiez les clés dans .env.")
