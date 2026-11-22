from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

class LogEntry(BaseModel):
    timestamp: str
    agent: str
    action: str
    message: str
    status: str = "INFO"

class ResearchPlan(BaseModel):
    objective_summary: str
    focus_areas: List[str] = Field(default_factory=list)
    initial_queries: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    estimated_complexity: str = "standard"

class SourceItem(BaseModel):
    title: str
    url: str
    snippet: str
    score: Optional[float] = None
    query: Optional[str] = None

class VerificationResult(BaseModel):
    status: str  # "APPROVED", "NEEDS_MORE_RESEARCH", "INSUFFICIENT_EVIDENCE"
    score: float = 0.0
    critique: str = ""
    missing_points: List[str] = Field(default_factory=list)
    suggested_queries: List[str] = Field(default_factory=list)

class FinalReport(BaseModel):
    title: str
    executive_summary: str
    introduction: str
    research_methodology: str
    detailed_findings: str
    comparative_analysis: str
    advantages_and_limitations: str
    recommendations: str
    conclusion: str
    references: List[Dict[str, str]] = Field(default_factory=list)

class ResearchState(TypedDict):
    id: str
    objective: str
    language: str
    depth: str
    max_sources: int
    plan: Dict[str, Any]
    queries_executed: List[str]
    sources: List[Dict[str, Any]]
    analysis: Dict[str, Any]
    verification: Dict[str, Any]
    iteration_count: int
    final_report: Dict[str, Any]
    pdf_path: Optional[str]
    logs: List[Dict[str, Any]]
    error: Optional[str]
