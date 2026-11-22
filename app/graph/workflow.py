from langgraph.graph import StateGraph, END
from app.graph.state import ResearchState
from app.graph.nodes import (
    plan_node,
    research_node,
    analyze_node,
    verify_node,
    report_node
)
from app.core.config import settings

def decide_next_step(state: ResearchState) -> str:
    """Condition de transition après l'évaluation du vérificateur."""
    verification = state.get("verification", {})
    status = verification.get("status", "APPROVED")
    iteration = state.get("iteration_count", 0)

    # Si relance requise et limite de boucles non atteinte
    if status == "NEEDS_MORE_RESEARCH" and iteration <= settings.MAX_RESEARCH_CYCLES:
        return "planner"

    # Sinon on passe directement à la rédaction finale
    return "reporter"

def build_research_graph():
    """Assemble le graphe multi-agents LangGraph."""
    workflow = StateGraph(ResearchState)

    # Déclaration des nœuds
    workflow.add_node("planner", plan_node)
    workflow.add_node("researcher", research_node)
    workflow.add_node("analyzer", analyze_node)
    workflow.add_node("verifier", verify_node)
    workflow.add_node("reporter", report_node)

    # Définition des flux séquentiels
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "analyze_node" if False else "analyzer")
    workflow.add_edge("analyzer", "verifier")

    # Branchement conditionnel autonome
    workflow.add_conditional_edges(
        "verifier",
        decide_next_step,
        {
            "planner": "planner",
            "reporter": "reporter"
        }
    )

    workflow.add_edge("reporter", END)

    return workflow.compile()

research_graph = build_research_graph()
