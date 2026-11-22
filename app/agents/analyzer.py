from typing import Dict, Any, List
from app.services.llm_service import llm_service

class AnalyzerAgent:
    """Agent chargé de disséquer, comparer et structurer les données collectées."""

    SYSTEM_PROMPT = """Tu es un Analyste Technique Senior et Spécialiste de la Synthèse d'Informations.
Ton rôle est d'analyser en profondeur les extraits de sources web collectés, d'extraire les éléments factuels, 
d'identifier les convergences, les divergences ou contradictions entre sources, et de dresser un comparatif objectif.
Tu ne dois inventer aucun fait qui ne soit supporté par les sources.
IMPORTANT : Réponds EXCLUSIVEMENT au format JSON strict."""

    def analyze_findings(
        self,
        objective: str,
        sources: List[Dict[str, Any]],
        language: str = "Français"
    ) -> Dict[str, Any]:
        """Produit une analyse comparative et factuelle complète."""
        if not sources:
            return {
                "summary": "Aucune source disponible pour l'analyse.",
                "key_findings": [],
                "comparative_matrix": {},
                "pros_and_cons": {},
                "contradictions_or_debates": ["Absence de sources exploitables."],
                "coverage_assessment": "Insuffisant"
            }

        # Préparation des sources pour le prompt avec indexation
        sources_context = []
        for idx, s in enumerate(sources[:12], 1):
            sources_context.append(
                f"[Source {idx}] Titre: {s.get('title')}\nURL: {s.get('url')}\nContenu: {s.get('snippet')[:800]}\n"
            )
        formatted_context = "\n---\n".join(sources_context)

        prompt = f"""Objectif : {objective}
Langue d'analyse requise : {language}

Voici les données collectées depuis les sources vérifiées :
{formatted_context}

Analyse ces informations et structure ton diagnostic au format JSON suivant :
{{
  "summary": "Synthèse globale et dense des éléments collectés",
  "key_findings": [
    "Fait majeur 1 étayé par les sources",
    "Fait majeur 2 étayé par les sources"
  ],
  "comparative_matrix": {{
    "points_de_comparaison": "Analyse comparative structurée des différentes solutions/sujets abordés"
  }},
  "pros_and_cons": {{
    "avantages": ["Avantage 1", "Avantage 2"],
    "limitations": ["Limite 1", "Limite 2"]
  }},
  "contradictions_or_debates": [
    "Points de désaccord, divergences de benchmarks ou débats techniques identifiés dans les sources"
  ],
  "coverage_assessment": "Évaluation de la couverture du sujet (Complète / Partielle / Lacunaire)"
}}"""

        return llm_service.generate_structured(
            prompt=prompt,
            system_instruction=self.SYSTEM_PROMPT,
            temperature=0.2
        )

analyzer_agent = AnalyzerAgent()
