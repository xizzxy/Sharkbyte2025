"""
Pydantic schemas for roadmap output
"""
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field


class Step(BaseModel):
    """A single step in an educational/career path"""
    id: str
    type: Literal["program", "course", "certification", "license", "job"]
    institution: str
    duration: str = Field(..., description="Duration (e.g., '2 years', '6 months')")
    cost: float = Field(..., description="Cost in USD")
    prerequisites: List[str] = Field(default_factory=list)
    description: str


class Path(BaseModel):
    """Complete educational path (cheapest, fastest, or prestige)"""
    id: str
    name: str = Field(..., description="Path name (e.g., 'Cheapest Path')")
    total_cost: float
    duration: str = Field(..., description="Total duration")
    steps: List[Step]
    roi: float = Field(..., description="Years to break even")


class Node(BaseModel):
    """React Flow node"""
    id: str
    type: Literal["mdc", "university", "cert", "license", "outcome", "masters", "phd", "internship", "research"]
    data: Dict = Field(
        ...,
        description="Node data (label, cost, duration, url)"
    )
    position: Dict[str, float] = Field(..., description="x, y coordinates")


class Edge(BaseModel):
    """React Flow edge"""
    id: str
    source: str
    target: str
    label: Optional[str] = Field(None, description="Edge label (e.g., 'Transfer Agreement')")


class Citation(BaseModel):
    """Source citation"""
    id: str
    title: str
    url: str
    accessed_at: str


class MDCProgram(BaseModel):
    """MDC academic program"""
    code: str = Field(..., description="Program code (e.g., AS.EGR)")
    name: str
    credits: int
    url: str


class TransferOption(BaseModel):
    """University transfer option"""
    university: str
    program: str
    articulation: str = Field(..., description="Agreement type (e.g., '2+2')")
    url: str
    abet_accredited: Optional[bool] = None


class Certification(BaseModel):
    """Professional certification"""
    name: str
    required: bool
    timing: str = Field(..., description="When to obtain (e.g., 'Before graduation')")
    url: Optional[str] = None


class License(BaseModel):
    """Professional license"""
    name: str
    required: bool
    timing: str
    state: str = Field(..., description="State where license is valid")
    url: Optional[str] = None


class PathwayResult(BaseModel):
    """Result from PathwayResearchAgent"""
    mdc_programs: List[MDCProgram]
    transfer_options: List[TransferOption]
    certifications: List[Certification]
    licenses: List[License]
    citations: List[Citation]


class CostBreakdown(BaseModel):
    """Cost breakdown for a path"""
    mdc: float = 0.0
    university: float = 0.0
    fees: float = 0.0
    books: float = 0.0
    certifications: float = 0.0
    total: float


class CostResult(BaseModel):
    """Result from CostEstimatorAgent"""
    cheapest_path: Dict = Field(..., description="Cheapest path cost breakdown")
    fastest_path: Dict = Field(..., description="Fastest path cost breakdown")
    prestige_path: Dict = Field(..., description="Prestige path cost breakdown")


class SalaryResult(BaseModel):
    """Result from SalaryOutlookAgent"""
    occupation: str
    bls_code: str
    median_salary: float
    miami_salary: Optional[float] = None
    growth_rate: str
    job_outlook: str
    roi_years: float


class Roadmap(BaseModel):
    """Complete roadmap output"""
    paths: Dict[str, Path] = Field(
        ...,
        description="Cheapest, fastest, and prestige paths"
    )
    nodes: List[Node]
    edges: List[Edge]
    citations: List[Citation]
    metadata: Dict = Field(
        ...,
        description="Generated timestamp, confidence, etc."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "paths": {
                    "cheapest": {
                        "id": "cheapest",
                        "name": "Most Affordable Path",
                        "total_cost": 28000,
                        "duration": "4 years",
                        "steps": [],
                        "roi": 6.2
                    }
                },
                "nodes": [],
                "edges": [],
                "citations": [],
                "metadata": {
                    "generated_at": "2025-11-07T12:00:00Z",
                    "confidence": 0.85
                }
            }
        }
