from datetime import datetime
from typing import Dict, Any
from app.graph.state import ResearchState
from app.agents.planner import planner_agent
from app.agents.researcher import researcher_agent
from app.agents.analyzer import analyzer_agent
from app.agents.verifier import verifier_agent
from app.agents.reporter import reporter_agent
from app.services.pdf_service import pdf_service
from app.storage.json_storage import json_storage
from app.core.config import settings

def _add_log(state: ResearchState, agent: str, action: str, message: str, status: str = "INFO"):
    """Ajoute une entrée d'audit horodatée."""
    log_entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "agent": agent,
        "action": action,
        "message": message,
        "status": status
    }
    state.setdefault("logs", []).append(log_entry)

def plan_node(state: ResearchState) -> Dict[str, Any]:
    """Nœud de planification (initiale ou itérative)."""
    objective = state["objective"]
    depth = state.get("depth", "standard")
    language = state.get("language", "Français")
    iteration = state.get("iteration_count", 0)

    if iteration == 0 or not state.get("plan"):
        _add_log(state, "PLANIFICATEUR", "Planification Initiale", f"Analyse de l'objectif : '{objective[:80]}...'")
        plan = planner_agent.plan_initial_research(objective, depth=depth, language=language)
        _add_log(state, "PLANIFICATEUR", "Plan Généré", f"{len(plan.get('initial_queries', []))} requêtes programmées.")
    else:
        _add_log(state, "PLANIFICATEUR", "Adaptation du Plan", f"Itération {iteration} : ajustement basé sur l'évaluation.")
        plan = planner_agent.adapt_plan(objective, state["plan"], state.get("verification", {}), depth=depth)
        _add_log(state, "PLANIFICATEUR", "Requêtes Correctives", f"{len(plan.get('initial_queries', []))} requêtes complémentaires.")

    state["plan"] = plan
    json_storage.save_research_session(dict(state))
    return state

def research_node(state: ResearchState) -> Dict[str, Any]:
    """Nœud d'exécution des requêtes de recherche."""
    plan = state.get("plan", {})
    queries = plan.get("initial_queries", [])
    depth = state.get("depth", "standard")
    existing_sources = state.get("sources", [])

    _add_log(state, "RECHERCHE", "Investigation Web", f"Exécution de {len(queries)} requêtes sur le Web.")
    sources, executed = researcher_agent.execute_research(
        queries=queries,
        depth=depth,
        existing_sources=existing_sources
    )

    state["sources"] = sources
    state.setdefault("queries_executed", []).extend(executed)
    _add_log(state, "RECHERCHE", "Indexation Terminée", f"Total sources actives : {len(sources)}.")
    
    json_storage.save_research_session(dict(state))
    return state

def analyze_node(state: ResearchState) -> Dict[str, Any]:
    """Nœud d'analyse et d'extraction de tendances."""
    objective = state["objective"]
    sources = state.get("sources", [])
    language = state.get("language", "Français")

    _add_log(state, "ANALYSE", "Examen des Sources", f"Synthèse et confrontation de {len(sources)} sources.")
    analysis = analyzer_agent.analyze_findings(objective, sources, language=language)
    state["analysis"] = analysis
    _add_log(state, "ANALYSE", "Synthèse Établie", "Identification des points de convergence et contradictions.")

    json_storage.save_research_session(dict(state))
    return state

def verify_node(state: ResearchState) -> Dict[str, Any]:
    """Nœud de contrôle qualité et décision autonome."""
    objective = state["objective"]
    plan = state.get("plan", {})
    sources = state.get("sources", [])
    analysis = state.get("analysis", {})
    iteration = state.get("iteration_count", 0)
    max_cycles = settings.MAX_RESEARCH_CYCLES

    _add_log(state, "VERIFICATION", "Contrôle Qualité", f"Évaluation de complétude (Itération {iteration}/{max_cycles}).")
    verification = verifier_agent.verify_research(
        objective=objective,
        plan=plan,
        sources=sources,
        analysis=analysis,
        iteration=iteration,
        max_iterations=max_cycles
    )

    status = verification.get("status", "APPROVED")
    state["verification"] = verification

    if status == "NEEDS_MORE_RESEARCH" and iteration < max_cycles:
        state["iteration_count"] = iteration + 1
        _add_log(state, "VERIFICATION", "Décision : Relance", f"Niveau insuffisant. Déclenchement cycle {state['iteration_count']}.", "WARNING")
    elif status == "INSUFFICIENT_EVIDENCE":
        _add_log(state, "VERIFICATION", "Décision : Limite Atteinte", "Documentation limitée. Poursuite avec avertissement.", "WARNING")
    else:
        _add_log(state, "VERIFICATION", "Décision : Validation", "Qualité certifiée. Autorisation de génération du rapport.", "SUCCESS")

    json_storage.save_research_session(dict(state))
    return state

def report_node(state: ResearchState) -> Dict[str, Any]:
    """Nœud de génération finale du rapport et du PDF."""
    objective = state["objective"]
    plan = state.get("plan", {})
    sources = state.get("sources", [])
    analysis = state.get("analysis", {})
    verification = state.get("verification", {})
    language = state.get("language", "Français")
    depth = state.get("depth", "standard")
    session_id = state.get("id")

    _add_log(state, "REDACTION", "Génération du Rapport", "Rédaction des 10 sections et calcul des citations.")
    final_report = reporter_agent.generate_final_report(
        objective=objective,
        plan=plan,
        sources=sources,
        analysis=analysis,
        verification=verification,
        language=language,
        depth=depth
    )
    state["final_report"] = final_report

    _add_log(state, "REDACTION", "Export PDF", "Mise en page vectorielle via ReportLab.")
    pdf_path = pdf_service.generate_report(final_report, session_id)
    state["pdf_path"] = pdf_path
    _add_log(state, "SYSTEME", "Mission Terminée", f"Rapport PDF disponible : {pdf_path}", "SUCCESS")

    json_storage.save_research_session(dict(state))
    return state
