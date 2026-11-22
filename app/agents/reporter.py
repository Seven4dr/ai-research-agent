from typing import Dict, Any, List
from app.services.llm_service import llm_service

class ReporterAgent:
    """Agent chargé de rédiger le rapport final complet respectant les 10 sections obligatoires."""

    SYSTEM_PROMPT = """Tu es un Rédacteur Scientifique et Technique Senior de renom.
Ton rôle est de rédiger un rapport d'analyse de très haut niveau, rigoureux, neutre, articulé et professionnel.
Le rapport doit être rédigé dans un français impeccable et soigné.
Aucun émoji ne doit figurer dans le texte.
Toutes les affirmations importantes doivent citer les sources collectées en utilisant la notation [1], [2], etc.
Tu dois STRICTEMENT respecter les 10 sections obligatoires imposées sans en omettre aucune.
IMPORTANT : Réponds EXCLUSIVEMENT au format JSON strict."""

    def generate_final_report(
        self,
        objective: str,
        plan: Dict[str, Any],
        sources: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        verification: Dict[str, Any],
        language: str = "Français",
        depth: str = "standard"
    ) -> Dict[str, Any]:
        """Rédige les 10 sections du rapport final exhaustif."""
        # Construction de l'index de références numérotées
        ref_list = []
        ref_context = []
        for idx, s in enumerate(sources, 1):
            ref_list.append({
                "index": idx,
                "title": s.get("title", f"Source {idx}"),
                "url": s.get("url", "")
            })
            ref_context.append(f"[{idx}] {s.get('title')} ({s.get('url')}):\n{s.get('snippet')[:600]}")

        formatted_refs = "\n---\n".join(ref_context[:14])

        prompt = f"""Objectif : {objective}
Profondeur de recherche : {depth}
Langue requise : {language}

Dossier de sources documentaires vérifiées :
{formatted_refs}

Données de l'analyse préalable :
- Synthèse : {analysis.get('summary', '')}
- Découvertes : {analysis.get('key_findings', [])}
- Comparatif : {analysis.get('comparative_matrix', {})}
- Débats/Contradictions : {analysis.get('contradictions_or_debates', [])}

Rédige un rapport complet de qualité professionnelle. Utilise les balises de citation [1], [2], etc.
Réponds STRICTEMENT sous la forme d'un objet JSON avec ces clés exactes :
{{
  "title": "Titre clair, percutant et professionnel",
  "executive_summary": "Synthèse exécutive détaillée destinée aux décideurs",
  "introduction": "Contexte, enjeux technologiques et périmètre d'analyse",
  "research_methodology": "Démarche d'investigation multi-agents, requêtes exécutées et critères de sélection",
  "detailed_findings": "Constats techniques détaillés avec citations des sources [X]",
  "comparative_analysis": "Comparaison approfondie des solutions/concepts étudiés",
  "advantages_and_limitations": "Avantages opérationnels et limites techniques identifiés",
  "recommendations": "Recommandations concrètes et cas d'usage conseillés",
  "conclusion": "Bilan de clôture et perspectives futures"
}}"""

        report_json = llm_service.generate_structured(
            prompt=prompt,
            system_instruction=self.SYSTEM_PROMPT,
            temperature=0.2
        )

        # Injecter la liste officielle des références
        report_json["references"] = ref_list
        report_json["depth"] = depth
        report_json["language"] = language
        return report_json

reporter_agent = ReporterAgent()
