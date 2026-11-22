from typing import Dict, Any, List
from app.services.llm_service import llm_service

class VerifierAgent:
    """Agent d'audit qualité chargé de vérifier l'exactitude, la couverture et la solidité des sources."""

    SYSTEM_PROMPT = """Tu es un Auditeur Qualité et Fact-Checker Technique Senior.
Ton rôle est d'évaluer avec rigueur si les informations et sources recueillies répondent pleinement à l'objectif de recherche initial.
Tu dois inspecter :
1. La pertinence et crédibilité apparente des sources.
2. L'alignement avec les critères de succès fixés dans le plan.
3. L'absence d'affirmations gratuites sans source.
4. Si les résultats sont suffisants pour un rapport de haut niveau.

Décisions possibles :
- APPROVED : Informations riches, fiables, suffisantes pour le rapport final.
- NEEDS_MORE_RESEARCH : Il manque des éléments clés ou certains axes sont trop peu documentés.
- INSUFFICIENT_EVIDENCE : Sources trop faibles ou inexistantes après tentative.

IMPORTANT : Réponds EXCLUSIVEMENT au format JSON strict."""

    def verify_research(
        self,
        objective: str,
        plan: Dict[str, Any],
        sources: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        iteration: int = 0,
        max_iterations: int = 2
    ) -> Dict[str, Any]:
        """Audite la qualité de la recherche et statue sur l'opportunité d'une boucle complémentaire."""
        # Sécurité : si aucune source, forcer une recherche complémentaire si compteur < max
        if len(sources) == 0:
            if iteration < max_iterations:
                return {
                    "status": "NEEDS_MORE_RESEARCH",
                    "score": 0.0,
                    "critique": "Aucune source collectée lors du premier passage. Réorientation indispensable.",
                    "missing_points": ["Toutes les informations sur le sujet."],
                    "suggested_queries": [objective]
                }
            else:
                return {
                    "status": "INSUFFICIENT_EVIDENCE",
                    "score": 0.1,
                    "critique": "Aucune source fiable n'a pu être trouvée malgré les recherches.",
                    "missing_points": ["L'ensemble du sujet."],
                    "suggested_queries": []
                }

        criteria = plan.get("success_criteria", [])
        sources_summary = [f"- {s.get('title')} ({s.get('url')})" for s in sources[:10]]

        prompt = f"""Objectif : {objective}
Critères de succès attendus : {criteria}
Nombre total de sources collectées : {len(sources)}
Aperçu des sources :
{chr(10).join(sources_summary)}

Synthèse de l'Analyse :
{analysis.get('summary', '')}

Cycle d'itération actuel : {iteration} (Plafond maximal autorisé : {max_iterations})

Évalue la qualité et décide si le travail est prêt pour le rapport final ou requiert une passe supplémentaire.
Format JSON requis :
{{
  "status": "APPROVED" ou "NEEDS_MORE_RESEARCH" ou "INSUFFICIENT_EVIDENCE",
  "score": 8.5,
  "critique": "Évaluation détaillée des forces et des faiblesses du dossier documentaire",
  "missing_points": ["Point manquant 1 si applicable"],
  "suggested_queries": ["Requête très ciblée pour combler le manque"]
}}"""

        result = llm_service.generate_structured(
            prompt=prompt,
            system_instruction=self.SYSTEM_PROMPT,
            temperature=0.1
        )

        # Règle de garde stricte : si plafond d'itérations atteint, on ne relance plus
        if iteration >= max_iterations and result.get("status") == "NEEDS_MORE_RESEARCH":
            result["status"] = "APPROVED"
            result["critique"] += " (Validation accordée pour finalisation suite au plafond d'itérations atteint)."

        return result

verifier_agent = VerifierAgent()
