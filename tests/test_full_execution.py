import sys
import uuid
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.graph.workflow import research_graph
from app.graph.state import ResearchState
from app.storage.json_storage import json_storage

def run_test():
    session_id = str(uuid.uuid4())
    print(f"Lancement du test bout-en-bout (ID: {session_id})...")
    
    initial_state: ResearchState = {
        "id": session_id,
        "objective": "Compare LangGraph and CrewAI for multi-agent workflows in 2026",
        "language": "Français",
        "depth": "rapide",
        "max_sources": 4,
        "plan": {},
        "queries_executed": [],
        "sources": [],
        "analysis": {},
        "verification": {},
        "iteration_count": 0,
        "final_report": {},
        "pdf_path": None,
        "logs": [],
        "error": None
    }
    
    print("\n[STREAMING DES EVENEMENTS DU GRAPHE LANGGRAPH]")
    final_state = dict(initial_state)
    for event in research_graph.stream(final_state):
        node_name = list(event.keys())[0]
        updated = event[node_name]
        final_state.update(updated)
        print(f" -> Nœud complété : [{node_name.upper()}]")
        if node_name == "planner":
            print(f"    Requêtes : {final_state.get('plan', {}).get('initial_queries')}")
        elif node_name == "researcher":
            print(f"    Sources trouvées : {len(final_state.get('sources', []))}")
        elif node_name == "verifier":
            print(f"    Décision : {final_state.get('verification', {}).get('status')}")
        elif node_name == "reporter":
            print(f"    Rapport généré : '{final_state.get('final_report', {}).get('title')}'")
            print(f"    Fichier PDF : {final_state.get('pdf_path')}")

    print("\n[VERIFICATION DES FICHIERS PRODUITS]")
    saved = json_storage.get_research_session(session_id)
    assert saved is not None, "La session JSON doit être enregistrée"
    print(" -> Session JSON enregistrée et relue avec succès.")
    
    pdf_p = final_state.get("pdf_path")
    assert pdf_p and Path(pdf_p).exists(), "Le fichier PDF doit exister sur le disque"
    print(f" -> Fichier PDF vérifié sur le disque ({Path(pdf_p).stat().st_size} octets).")
    print("\nTest bout-en-bout réussi avec 100% de succès.")

if __name__ == "__main__":
    run_test()
