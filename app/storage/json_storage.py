import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.core.config import settings

class JSONStorage:
    """Gestionnaire de persistance locale au format JSON."""
    
    def __init__(self):
        settings.ensure_directories()
        self.research_dir = settings.RESEARCH_DIR
        self.reports_dir = settings.REPORTS_DIR

    def save_research_session(self, session_data: Dict[str, Any]) -> str:
        """Sauvegarde une session de recherche complète."""
        session_id = session_data.get("id") or str(uuid.uuid4())
        session_data["id"] = session_id
        session_data["updated_at"] = datetime.now().isoformat()
        if "created_at" not in session_data:
            session_data["created_at"] = session_data["updated_at"]
            
        file_path = self.research_dir / f"research_{session_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
            
        return session_id

    def get_research_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une session de recherche par son identifiant."""
        file_path = self.research_dir / f"research_{session_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_research_sessions(self) -> List[Dict[str, Any]]:
        """Liste l'ensemble des sessions enregistrées, triées par date décroissante."""
        sessions = []
        for file_path in self.research_dir.glob("research_*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    sessions.append({
                        "id": data.get("id"),
                        "objective": data.get("objective", "Sans titre"),
                        "created_at": data.get("created_at"),
                        "status": data.get("verification", {}).get("status", "INCONNU"),
                        "sources_count": len(data.get("sources", [])),
                        "pdf_path": data.get("pdf_path"),
                        "file_path": str(file_path)
                    })
            except Exception:
                continue
                
        sessions.sort(key=lambda s: s.get("created_at", ""), reverse=True)
        return sessions

    def get_stats(self) -> Dict[str, int]:
        """Calcule les métriques globales pour le tableau de bord."""
        sessions = self.list_research_sessions()
        total = len(sessions)
        completed = sum(1 for s in sessions if s.get("status") in ["APPROVED", "VALIDE", "TERMINE"])
        sources_count = sum(s.get("sources_count", 0) for s in sessions)
        return {
            "total_researches": total,
            "completed_researches": completed,
            "in_progress_researches": max(0, total - completed),
            "total_sources_collected": sources_count
        }

json_storage = JSONStorage()
