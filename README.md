# AI Research Agent — Autonomous Research & Reporting System

Prototype fonctionnel léger d'un système multi-agents autonome d'investigation, d'analyse et de génération de rapports stratégiques propulsé par **LangGraph**, **Google Gemini** et **Tavily Search API**.

Ce projet a été conçu selon les exigences d'un environnement de production contraint (16 Go de RAM, processeur Intel Core i5-6300U, sans conteneurisation lourde type Docker ni base de données relationnelle).

---

## 1. Architecture Multi-Agents et Workflow

Le système repose sur un graphe cyclique supervisé avec LangGraph comprenant 5 agents spécialisés :

1. **Planner Agent** : Décompose l'objectif en axes stratégiques et génère des requêtes web optimisées. Ajuste dynamiquement le plan en cas de retours du vérificateur.
2. **Researcher Agent** : Interroge Tavily Search API, déduplique les sources, assainit le contenu (protection contre les injections de prompt web) et indexe les métadonnées.
3. **Analyzer Agent** : Synthétise les informations collectées, dresse des matrices comparatives, met en lumière les avantages, limites et contradictions factuelles.
4. **Verification Agent** : Audite l'exhaustivité et la solidité des preuves. Émet une décision stricte (`APPROVED`, `NEEDS_MORE_RESEARCH` dans la limite de 2 boucles, ou `INSUFFICIENT_EVIDENCE`).
5. **Report Agent & PDF Service** : Rédige les 10 sections imposées et génère un rapport vectoriel ReportLab paginé avec citations cliquables.

```
                              [ Objectif Utilisateur ]
                                         │
                                         ▼
                                 ┌───────────────┐
                                 │ PLANNER AGENT │
                                 └───────┬───────┘
                                         │ Plan initial (JSON)
                                         ▼
                            ┌─────────────────────────┐
                            │     RESEARCH AGENT      │
                            │  (Tavily Search API)    │
                            └────────────┬────────────┘
                                         │ Données brutes & URLs
                                         ▼
                                 ┌───────────────┐
                                 │ ANALYSIS AGENT│
                                 └───────┬───────┘
                                         │ Synthèse & Détection contradictions
                                         ▼
                            ┌─────────────────────────┐
                            │   VERIFICATION AGENT    │
                            └────────────┬────────────┘
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   │                                           │
         [ APPROVED ]                                [ NEEDS_MORE_RESEARCH ]
                   │                                           │ (Max 2 cycles)
                   ▼                                           ▼
          ┌────────────────┐                         ┌───────────────────┐
          │  REPORT AGENT  │                         │ MISE À JOUR PLAN  │
          └────────┬───────┘                         └─────────┬─────────┘
                   │ Rapport 10 sections                       │ Nouvelles requêtes
                   ▼                                           └────────┐
          ┌────────────────┐                                            │
          │  PDF SERVICE   │                                            ▼
          │  (ReportLab)   │                                [ RESEARCH AGENT ]
          └────────┬───────┘
                   ▼
       [ Résultat & Export PDF ]
```

---

## 2. Structure du Code

```
ai-research-agent/
│
├── app/
│   ├── agents/
│   │   ├── planner.py         # Planification initiale et adaptation
│   │   ├── researcher.py      # Pilotage Tavily et déduplication
│   │   ├── analyzer.py        # Analyse comparative et synthèse
│   │   ├── verifier.py        # Audit qualité et décisions autonomes
│   │   └── reporter.py        # Rédaction structurée des 10 sections
│   │
│   ├── graph/
│   │   ├── state.py           # Schéma d'état typé ResearchState
│   │   ├── nodes.py           # Nœuds du cycle multi-agents
│   │   └── workflow.py        # Définition du graphe et transitions LangGraph
│   │
│   ├── services/
│   │   ├── llm_service.py     # Service Gemini avec bascule et retries automatiques
│   │   ├── search_service.py  # Wrapper client Tavily Search
│   │   └── pdf_service.py     # Générateur vectoriel PDF ReportLab sobre
│   │
│   ├── core/
│   │   └── config.py          # Paramètres et gestion des variables d'environnement
│   │
│   └── storage/
│       └── json_storage.py    # Persistance JSON locale des sessions
│
├── data/
│   ├── research/              # Traces et états intermédiaires JSON
│   └── reports/               # Rapports PDF finaux générés
│
├── tests/
│   ├── test_api_connections.py # Validation des clés API Gemini et Tavily
│   ├── test_workflow.py        # Tests unitaires du stockage et du générateur PDF
│   └── test_full_execution.py  # Test fonctionnel complet du graphe de bout-en-bout
│
├── .env.example
├── .gitignore
├── requirements.txt
├── streamlit_app.py           # Interface utilisateur Streamlit
└── README.md
```

---

## 3. Prérequis et Installation

- Système d'exploitation : Windows, macOS ou Linux
- Python : Version 3.12 ou supérieure recommandée
- RAM minimale conseillée : 8 Go (optimisé pour 16 Go)

### Étape 1 : Installation des dépendances

```bash
pip install -r requirements.txt
```

### Étape 2 : Configuration des variables d'environnement

Créer un fichier `.env` à la racine (ou copier `.env.example`) :

```env
# Clé API Google Gemini (AI Studio ou Vertex)
GEMINI_API_KEY=votre_cle_gemini_ici
GEMINI_MODEL=gemini-3.5-flash

# Clé API Tavily Search
TAVILY_API_KEY=votre_cle_tavily_ici

# Limites du système
MAX_RESEARCH_CYCLES=2
REQUEST_TIMEOUT_SECONDS=60
DEFAULT_SEARCH_DEPTH=standard
```

---

## 4. Lancement de l'Application Streamlit

Pour démarrer l'interface utilisateur en mode sombre corporate :

```bash
streamlit run streamlit_app.py
```

L'application s'ouvrira automatiquement à l'adresse locale `http://localhost:8501`.

### Fonctionnalités de l'interface :
- **Tableau de bord** : Métriques globales sur les recherches effectuées, les sources indexées et l'historique récent.
- **Nouvelle recherche** : Formulaire de soumission d'objectif avec sélection du niveau de profondeur (*Rapide*, *Standard*, *Approfondie*), de la langue et du quota de sources.
- **Suivi en direct** : Visualisation en temps réel de chaque agent en action (streaming LangGraph), avec affichage dynamique du plan, des requêtes, des extraits de sources et de la décision d'audit.
- **Rapport et Résultats** : Consultation des 10 sections rédigées avec citations vérifiables `[1]`, `[2]`.
- **Export PDF** : Téléchargement direct du rapport PDF prêt à l'emploi.
- **Historique des recherches** : Rechargement en un clic de n'importe quelle session archivée au format JSON.

---

## 5. Exécution des Tests de Validation

Pour tester les composants de manière indépendante :

### 1. Test des liaisons API (Gemini et Tavily)
```bash
python tests/test_api_connections.py
```

### 2. Test du stockage JSON et de la génération PDF
```bash
python tests/test_workflow.py
```

### 3. Test complet du workflow multi-agents de bout-en-bout
```bash
python tests/test_full_execution.py
```

---

## 6. Scénario de Démonstration Recommandé

Pour une démonstration technique de 2 minutes :
1. Lancer l'interface via `streamlit run streamlit_app.py`.
2. Se rendre sur **Nouvelle recherche**.
3. Conserver ou soumettre l'objectif par défaut :
   > *"Research and compare LangGraph, CrewAI, AutoGen and OpenAI Agents SDK. Analyze their architectures, features, advantages, limitations and practical use cases. Produce a technical report with verifiable sources."*
4. Choisir la profondeur **Standard** et cliquer sur **Lancer la recherche autonome**.
5. Observer sur l'écran **Suivi en direct** l'enchaînement autonome des 5 agents et la prise de décision du vérificateur.
6. Télécharger le rapport PDF officiel depuis l'onglet **Rapport et Résultats**.
