import os
import sys
import unittest
from pathlib import Path

# Ajout du chemin racine
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.storage.json_storage import json_storage
from app.services.pdf_service import pdf_service
from app.graph.state import ResearchState
from app.graph.workflow import research_graph

class TestWorkflow(unittest.TestCase):
    """Suite de tests d'intégration pour le système de recherche autonome."""

    def test_json_storage(self):
        """Vérifie la persistance et la récupération locale en JSON."""
        test_session = {
            "id": "test_session_123",
            "objective": "Test de persistance",
            "status": "APPROVED",
            "sources": [{"title": "Doc Test", "url": "https://example.com"}]
        }
        sid = json_storage.save_research_session(test_session)
        self.assertEqual(sid, "test_session_123")
        
        loaded = json_storage.get_research_session(sid)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["objective"], "Test de persistance")
        print("[SUCCES] Test sauvegarde et lecture JSON OK.")

    def test_pdf_generation(self):
        """Vérifie la génération d'un rapport PDF vectoriel avec ReportLab."""
        mock_report = {
            "title": "Rapport de Test Automatisé",
            "executive_summary": "Ceci est un résumé exécutif de test.",
            "introduction": "Contexte du test unitaire.",
            "research_methodology": "Méthodologie standard.",
            "detailed_findings": "Constats factuels de test.",
            "comparative_analysis": "Analyse comparative A vs B.",
            "advantages_and_limitations": "Avantages et limites constatés.",
            "recommendations": "Recommandations opérationnelles.",
            "conclusion": "Conclusion du test.",
            "references": [
                {"title": "Documentation Officielle Python", "url": "https://docs.python.org/3/"}
            ],
            "depth": "Standard",
            "language": "Français"
        }
        pdf_path = pdf_service.generate_report(mock_report, "test_pdf_session")
        self.assertTrue(os.path.exists(pdf_path))
        self.assertTrue(os.path.getsize(pdf_path) > 1000)
        print(f"[SUCCES] Test génération PDF OK : {pdf_path}")

if __name__ == "__main__":
    unittest.main()
