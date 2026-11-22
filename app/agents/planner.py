from typing import Dict, Any, List
from app.services.llm_service import llm_service
from app.core.config import settings

class PlannerAgent:
    """Agent responsable de la planification et de l'adaptation dynamique des recherches."""

    SYSTEM_PROMPT = """Tu es un Planificateur de Recherche Stratégique Senior.
Ton rôle est d'analyser l'objectif fourni, de définir les axes d'investigation clés et de générer des requêtes de recherche ciblées pour un moteur comme Tavily.
Tes requêtes doivent être précises, techniques, en anglais ou en français selon la pertinence pour trouver la meilleure documentation.
IMPORTANT : Réponds EXCLUSIVEMENT au format JSON strict."""

    def plan_initial_research(self, objective: str, depth: str = "standard", language: str = "Français") -> Dict[str, Any]:
        """Crée le plan de recherche initial selon la profondeur demandée."""
        depth_conf = settings.DEPTH_CONFIG.get(depth, settings.DEPTH_CONFIG["standard"])
        max_q = depth_conf["max_queries"]

        prompt = f"""Objectif de recherche : {objective}
Profondeur d'investigation : {depth} (Nombre maximal de requêtes : {max_q})
Langue cible du rapport : {language}

Construis un plan de recherche méthodique. Génère exactement entre 2 et {max_q} requêtes de recherche Internet percutantes.
Renvoie un JSON avec la structure exacte suivante :
{{
  "objective_summary": "Résumé concis de l'objectif",
  "focus_areas": ["Axe 1", "Axe 2", ...],
  "initial_queries": ["requete 1", "requete 2", ...],
  "success_criteria": ["Critère 1", "Critère 2", ...],
  "estimated_complexity": "standard"
}}"""

        return llm_service.generate_structured(
            prompt=prompt,
            system_instruction=self.SYSTEM_PROMPT,
            temperature=0.2
        )

    def adapt_plan(self, objective: str, current_plan: Dict[str, Any], verification: Dict[str, Any], depth: str = "standard") -> Dict[str, Any]:
        """Ajuste les requêtes pour combler les manques identifiés par le Vérificateur."""
        missing = verification.get("missing_points", [])
        critique = verification.get("critique", "")
        suggested = verification.get("suggested_queries", [])

        prompt = f"""Objectif initial : {objective}
Critique du Vérificateur de qualité : {critique}
Points manquants ou insuffisants : {missing}
Suggestions de requêtes du vérificateur : {suggested}

Génère 2 à 3 requêtes de recherche Internet complémentaires pour cibler précisément ces lacunes.
Format JSON attendu :
{{
  "objective_summary": "{current_plan.get('objective_summary', objective)}",
  "focus_areas": {current_plan.get('focus_areas', [])},
  "initial_queries": ["nouvelle requete ciblee 1", "nouvelle requete ciblee 2"],
  "success_criteria": {current_plan.get('success_criteria', [])},
  "estimated_complexity": "complementaire"
}}"""

        return llm_service.generate_structured(
            prompt=prompt,
            system_instruction=self.SYSTEM_PROMPT,
            temperature=0.2
        )

planner_agent = PlannerAgent()
