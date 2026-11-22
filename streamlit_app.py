import os
import sys
import time
import json
import uuid
from datetime import datetime
from pathlib import Path
import streamlit as st

# Configuration du chemin
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from app.core.config import settings
from app.graph.workflow import research_graph
from app.graph.state import ResearchState
from app.storage.json_storage import json_storage
from app.services.pdf_service import pdf_service

# Configuration de la page
st.set_page_config(
    page_title="Système Autonome de Veille et d'Analyse",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles CSS personnalisés : Noir et Blanc Pur, Style Réel Corporate & Minimaliste
st.markdown("""
<style>
    /* Palette Noir et Blanc stricte */
    :root {
        --bg-black: #000000;
        --card-bg: #0d0d0d;
        --card-surface: #141414;
        --border-color: #262626;
        --border-subtle: #1f1f1f;
        --text-white: #ffffff;
        --text-muted: #888888;
        --text-dim: #555555;
    }

    /* Arrière-plan global */
    .stApp {
        background-color: var(--bg-black);
        color: var(--text-white);
        font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Cartes et conteneurs */
    .custom-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 20px;
        margin-bottom: 16px;
    }

    .custom-header {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--text-muted);
        margin-bottom: 8px;
        font-weight: 600;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-white);
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        letter-spacing: -0.02em;
    }

    /* Badges monochromes */
    .badge {
        display: inline-block;
        padding: 3px 8px;
        font-size: 0.72rem;
        font-weight: 600;
        border-radius: 2px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .badge-white {
        background: #ffffff;
        color: #000000;
        border: 1px solid #ffffff;
    }
    .badge-outline {
        background: transparent;
        color: #ffffff;
        border: 1px solid #444444;
    }
    .badge-muted {
        background: #171717;
        color: #888888;
        border: 1px solid #262626;
    }

    /* Lignes d'événements et logs */
    .log-row {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.82rem;
        padding: 10px 14px;
        border-left: 1px solid var(--text-white);
        margin-bottom: 8px;
        background: var(--card-surface);
        border-top: 1px solid var(--border-subtle);
        border-right: 1px solid var(--border-subtle);
        border-bottom: 1px solid var(--border-subtle);
    }
    .log-time { color: var(--text-dim); margin-right: 12px; font-weight: 500; }
    .log-agent { color: var(--text-white); font-weight: 700; margin-right: 12px; text-transform: uppercase; }

    /* Boutons Streamlit en style Noir & Blanc */
    div.stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #ffffff !important;
        border-radius: 2px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        padding: 10px 24px !important;
        transition: all 0.2s ease-in-out !important;
    }
    div.stButton > button:hover {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
    }

    div.stDownloadButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #ffffff !important;
        border-radius: 2px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        padding: 10px 24px !important;
    }
    div.stDownloadButton > button:hover {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
    }

    /* Champs de saisie */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div {
        background-color: #0d0d0d !important;
        color: #ffffff !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 2px !important;
    }

    /* Liens hypertexte sobres */
    a {
        color: #ffffff !important;
        text-decoration: underline !important;
        text-underline-offset: 3px;
    }
    a:hover {
        color: #cccccc !important;
    }

    /* Barre latérale */
    section[data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 1px solid var(--border-color) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de l'état de session Streamlit
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "live_state" not in st.session_state:
    st.session_state.live_state = None
if "is_running" not in st.session_state:
    st.session_state.is_running = False

# Barre latérale de navigation
with st.sidebar:
    st.markdown("### CENTRE DE RECHERCHE")
    st.caption("Système Autonome d'Investigation et de Décision")
    st.markdown("---")
    
    page = st.radio(
        "Menu Principal",
        [
            "Tableau de bord",
            "Nouvelle recherche",
            "Suivi en direct",
            "Rapport et Resultats",
            "Historique des rapports"
        ],
        index=1 if st.session_state.is_running else 0
    )
    st.markdown("---")
    
    st.markdown("### DISPONIBILITE SYSTEME")
    st.markdown("<span class='badge badge-white'>SYSTEME EN LIGNE</span>", unsafe_allow_html=True)
    st.caption("Tous les modules d'investigation et d'audit sont opérationnels.")


# -------------------------------------------------------------------------------------
# 1. TABLEAU DE BORD
# -------------------------------------------------------------------------------------
if page == "Tableau de bord":
    st.markdown("## VUE D'ENSEMBLE DES OPERATIONS")
    st.caption("Indicateurs consolidés sur l'activité d'investigation et l'archivage documentaire.")
    
    stats = json_storage.get_stats()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="custom-card">
            <div class="custom-header">Missions Totales</div>
            <div class="metric-value">{stats['total_researches']}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="custom-card">
            <div class="custom-header">Missions Conclues</div>
            <div class="metric-value">{stats['completed_researches']}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="custom-card">
            <div class="custom-header">Sources Archivees</div>
            <div class="metric-value">{stats['total_sources_collected']}</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="custom-card">
            <div class="custom-header">Cycles d'Audit Max</div>
            <div class="metric-value">{settings.MAX_RESEARCH_CYCLES}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("### DOSSIERS RECENTS")
    sessions = json_storage.list_research_sessions()
    if sessions:
        for s in sessions[:5]:
            with st.container():
                st.markdown(f"""
                <div class="custom-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 600; font-size: 1rem; color: #ffffff;">{s.get('objective', 'Sans titre')}</span>
                        <span class="badge badge-outline">{s.get('status')}</span>
                    </div>
                    <div style="margin-top: 8px; color: #888888; font-size: 0.85rem;">
                        Date : {s.get('created_at', '')[:16].replace('T', ' ')} | Sources vérifiées : {s.get('sources_count', 0)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Aucun dossier enregistré. Initialisez une première recherche.")


# -------------------------------------------------------------------------------------
# 2. NOUVELLE RECHERCHE
# -------------------------------------------------------------------------------------
elif page == "Nouvelle recherche":
    st.markdown("## LANCER UNE INVESTIGATION")
    st.caption("Définissez votre objectif d'analyse. Le système planifie, consulte les sources, synthétise et contrôle la rigueur des conclusions de façon autonome.")
    
    with st.form("new_research_form"):
        objective = st.text_area(
            "Objectif d'investigation",
            value="Research and compare LangGraph, CrewAI, AutoGen and OpenAI Agents SDK. Analyze their architectures, features, advantages, limitations and practical use cases. Produce a technical report with verifiable sources.",
            height=110,
            help="Précisez votre sujet d'étude ou votre problématique technique."
        )
        
        col_depth, col_lang, col_sources = st.columns(3)
        with col_depth:
            depth = st.selectbox(
                "Niveau de profondeur",
                ["standard", "rapide", "approfondie"],
                index=0,
                format_func=lambda x: {
                    "rapide": "Synthétique (Investigation ciblée)",
                    "standard": "Standard (Investigation équilibrée)",
                    "approfondie": "Approfondie (Investigation exhaustive)"
                }.get(x, x)
            )
        with col_lang:
            language = st.selectbox("Langue de restitution", ["Français", "Anglais"], index=0)
        with col_sources:
            max_sources = st.slider("Volume indicatif de sources", min_value=3, max_value=20, value=10)
            
        submitted = st.form_submit_button("DEMARRER L'ANALYSE AUTONOME")
        
    if submitted:
        if not objective.strip():
            st.error("Veuillez renseigner un objectif d'investigation.")
        else:
            session_id = str(uuid.uuid4())
            initial_state: ResearchState = {
                "id": session_id,
                "objective": objective.strip(),
                "language": language,
                "depth": depth,
                "max_sources": max_sources,
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
            
            st.session_state.current_session_id = session_id
            st.session_state.live_state = initial_state
            st.session_state.is_running = True
            
            json_storage.save_research_session(dict(initial_state))
            st.rerun()


# -------------------------------------------------------------------------------------
# 3. SUIVI EN DIRECT
# -------------------------------------------------------------------------------------
elif page == "Suivi en direct":
    st.markdown("## SURVEILLANCE DES PROCESSUS EN TEMPS REEL")
    st.caption("Flux d'exécution transparent : décisions méthodologiques, requêtes web, analyse critique et contrôle qualité.")
    
    if not st.session_state.live_state:
        st.info("Aucune exécution active. Veuillez lancer une recherche depuis l'onglet 'Nouvelle recherche'.")
    else:
        state = st.session_state.live_state
        
        # En-tête de session
        st.markdown(f"""
        <div class="custom-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="custom-header">Dossier en cours : {state.get('id', '')[:8]}</span>
                <span class="badge badge-white">EXECUTION ACTIVE</span>
            </div>
            <div style="font-size: 1.05rem; font-weight: 600; margin-top: 8px; color: #ffffff;">
                {state.get('objective')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Indicateurs d'état en 4 colonnes monochromes
        agent_col, iter_col, sources_col, status_col = st.columns(4)
        active_agent_placeholder = agent_col.empty()
        iter_placeholder = iter_col.empty()
        sources_placeholder = sources_col.empty()
        verdict_placeholder = status_col.empty()
        
        # Onglets de surveillance
        st.markdown("### ELEMENTS DE DECISION ET SOURCES EXTRAITES")
        tabs = st.tabs(["Plan strategique", "Sources identifiees", "Synthese preliminaire", "Journal d'audit"])
        
        tab_plan = tabs[0].empty()
        tab_sources = tabs[1].empty()
        tab_analysis = tabs[2].empty()
        tab_logs = tabs[3].empty()
        
        # Si la recherche est en cours, exécution réelle
        if st.session_state.is_running:
            try:
                progress_bar = st.progress(0, text="Initialisation de la séquence autonome...")
                
                step_idx = 0
                max_estimated_steps = 7
                
                current_state_payload = dict(state)
                
                for event in research_graph.stream(current_state_payload):
                    node_name = list(event.keys())[0]
                    updated_data = event[node_name]
                    current_state_payload.update(updated_data)
                    st.session_state.live_state = current_state_payload
                    
                    step_idx += 1
                    pct = min(100, int((step_idx / max_estimated_steps) * 100))
                    
                    # Libellés professionnels sans termes techniques bruts
                    agent_label = {
                        "planner": "STRATEGIE & PLANIFICATION",
                        "researcher": "INVESTIGATION WEB",
                        "analyzer": "ANALYSE TECHNIQUE",
                        "verifier": "AUDIT & CONFORMITE",
                        "reporter": "REDACTION & EXPORT"
                    }.get(node_name, node_name.upper())
                    
                    progress_bar.progress(pct, text=f"Étape active : {agent_label}")
                    
                    active_agent_placeholder.markdown(f"""
                    <div class="custom-card">
                        <div class="custom-header">Phase Actuelle</div>
                        <div style="font-weight: 700; color: #ffffff; font-size: 0.95rem;">{agent_label}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    iter_placeholder.markdown(f"""
                    <div class="custom-card">
                        <div class="custom-header">Cycle d'Audit</div>
                        <div class="metric-value">{current_state_payload.get('iteration_count', 0)} / {settings.MAX_RESEARCH_CYCLES}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    sources_placeholder.markdown(f"""
                    <div class="custom-card">
                        <div class="custom-header">Sources Retenues</div>
                        <div class="metric-value">{len(current_state_payload.get('sources', []))}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    v_status = current_state_payload.get('verification', {}).get('status', 'EN COURS')
                    verdict_placeholder.markdown(f"""
                    <div class="custom-card">
                        <div class="custom-header">Statut Conformite</div>
                        <div style="font-weight: 700; color: #ffffff;">{v_status}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Rendu du Plan
                    plan = current_state_payload.get("plan", {})
                    if plan:
                        with tab_plan.container():
                            st.markdown(f"**Cadrage du sujet :** {plan.get('objective_summary', '')}")
                            st.markdown("**Axes d'investigation :**")
                            for a in plan.get("focus_areas", []):
                                st.markdown(f"- {a}")
                            st.markdown("**Requêtes programmées :**")
                            for q in plan.get("initial_queries", []):
                                st.code(q, language="text")
                                
                    # Rendu des Sources
                    sources = current_state_payload.get("sources", [])
                    if sources:
                        with tab_sources.container():
                            st.markdown(f"**{len(sources)} sources documentaires vérifiées :**")
                            for s in sources:
                                st.markdown(f"""
                                <div class="log-row">
                                    <a href="{s.get('url')}" target="_blank"><b>{s.get('title')}</b></a><br/>
                                    <span style="color: #666666; font-size: 0.75rem;">{s.get('url')}</span>
                                    <div style="margin-top: 6px; color: #cccccc;">{s.get('snippet')[:250]}...</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                    # Rendu de l'Analyse
                    analysis = current_state_payload.get("analysis", {})
                    if analysis:
                        with tab_analysis.container():
                            st.markdown(f"**Synthèse globale :** {analysis.get('summary', '')}")
                            st.markdown("**Constats majeurs :**")
                            for kf in analysis.get("key_findings", []):
                                st.markdown(f"- {kf}")
                            debates = analysis.get("contradictions_or_debates", [])
                            if debates:
                                st.markdown("**Divergences ou Débats Notés :**")
                                for d in debates:
                                    st.markdown(f"- {d}")
                                    
                    # Rendu des Logs
                    logs = current_state_payload.get("logs", [])
                    if logs:
                        with tab_logs.container():
                            for l in reversed(logs):
                                st.markdown(f"""
                                <div class="log-row">
                                    <span class="log-time">[{l.get('timestamp')}]</span>
                                    <span class="log-agent">{l.get('agent')}</span>
                                    <span>{l.get('action')} — {l.get('message')}</span>
                                </div>
                                """, unsafe_allow_html=True)
                
                progress_bar.progress(100, text="Mission finalisée avec succès.")
                st.session_state.is_running = False
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.session_state.is_running = False
                st.error(f"Interruption de la procédure : {str(e)}")


# -------------------------------------------------------------------------------------
# 4. RAPPORT ET RESULTATS
# -------------------------------------------------------------------------------------
elif page == "Rapport et Resultats":
    st.markdown("## RAPPORT DE SYNTHESE TECHNIQUE")
    st.caption("Document final articulé en 10 sections avec appareil de citations vérifiables.")
    
    state = st.session_state.live_state
    if not state or not state.get("final_report"):
        st.info("Aucun rapport disponible pour la session courante. Veuillez lancer une recherche ou consulter l'Historique.")
    else:
        rep = state.get("final_report", {})
        
        # En-tête du rapport
        st.markdown(f"""
        <div class="custom-card">
            <div class="custom-header">Document d'analyse stratégique</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #ffffff; margin-bottom: 8px;">
                {rep.get('title', 'Sans Titre')}
            </div>
            <div style="color: #888888; font-size: 0.85rem;">
                Langue : {rep.get('language', 'Français')} | Niveau : {rep.get('depth', 'Standard').upper()} | Sources citées : {len(rep.get('references', []))}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Téléchargement PDF
        pdf_path = state.get("pdf_path")
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="TELECHARGER LE RAPPORT PDF OFFICIEL",
                data=pdf_bytes,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf"
            )
            
        st.markdown("---")
        
        # 10 Sections
        st.markdown("### 1. SYNTHESE EXECUTIVE")
        st.write(rep.get("executive_summary", ""))
        
        st.markdown("### 2. INTRODUCTION ET CONTEXTE")
        st.write(rep.get("introduction", ""))
        
        st.markdown("### 3. METHODOLOGIE DE RECHERCHE")
        st.write(rep.get("research_methodology", ""))
        
        st.markdown("### 4. RESULTATS DETAILLES")
        st.write(rep.get("detailed_findings", ""))
        
        st.markdown("### 5. ANALYSE COMPARATIVE")
        st.write(rep.get("comparative_analysis", ""))
        
        st.markdown("### 6. AVANTAGES ET LIMITES")
        st.write(rep.get("advantages_and_limitations", ""))
        
        st.markdown("### 7. RECOMMANDATIONS STRATEGIQUES")
        st.write(rep.get("recommendations", ""))
        
        st.markdown("### 8. CONCLUSION")
        st.write(rep.get("conclusion", ""))
        
        st.markdown("### 9. SOURCES DOCUMENTAIRES ET CITATIONS")
        refs = rep.get("references", [])
        if refs:
            for r in refs:
                st.markdown(f"**[{r.get('index')}] {r.get('title')}** — [{r.get('url')}]({r.get('url')})")
        else:
            st.write("Aucune source externe.")


# -------------------------------------------------------------------------------------
# 5. HISTORIQUE DES RAPPORTS
# -------------------------------------------------------------------------------------
elif page == "Historique des rapports":
    st.markdown("## ARCHIVES DES DOSSIERS")
    st.caption("Consultez et rechargez les sessions d'investigation enregistrées.")
    
    sessions = json_storage.list_research_sessions()
    if not sessions:
        st.info("Aucun dossier archivé.")
    else:
        for s in sessions:
            with st.container():
                st.markdown(f"""
                <div class="custom-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; font-size: 1.05rem; color: #ffffff;">{s.get('objective')}</span>
                        <span class="badge badge-outline">{s.get('status')}</span>
                    </div>
                    <div style="margin-top: 6px; color: #888888; font-size: 0.82rem;">
                        Identifiant : {s.get('id')} | Enregistré le : {s.get('created_at', '')[:19].replace('T', ' ')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col_load, col_pdf = st.columns([1, 1])
                with col_load:
                    if st.button("Consulter ce dossier", key=f"load_{s.get('id')}"):
                        loaded_data = json_storage.get_research_session(s.get('id'))
                        if loaded_data:
                            st.session_state.current_session_id = s.get('id')
                            st.session_state.live_state = loaded_data
                            st.session_state.is_running = False
                            st.rerun()
                with col_pdf:
                    pdf_p = s.get("pdf_path")
                    if pdf_p and os.path.exists(pdf_p):
                        with open(pdf_p, "rb") as pf:
                            st.download_button(
                                label="Télécharger PDF",
                                data=pf.read(),
                                file_name=os.path.basename(pdf_p),
                                mime="application/pdf",
                                key=f"dl_{s.get('id')}"
                            )
