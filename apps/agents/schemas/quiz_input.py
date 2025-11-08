"""
Pydantic schemas for quiz input validation
"""
from typing import List, Literal
from pydantic import BaseModel, Field, field_validator


class QuizInput(BaseModel):
    """User quiz input data"""
    career: str = Field(..., description="Target career (e.g., 'Mechanical Engineer')")
    current_education: Literal["hs", "some_college", "aa", "ba"] = Field(
        ..., description="Current education level"
    )
    gpa: float = Field(..., ge=0.0, le=4.0, description="Current GPA")
    budget: Literal["low", "medium", "high"] = Field(
        ..., description="Total education budget (<30k, 30-80k, >80k)"
    )
    timeline: Literal["fast", "normal", "flexible"] = Field(
        ..., description="Timeline preference (2yr, 4yr, 6yr+)"
    )
    location: Literal["miami", "florida", "anywhere"] = Field(
        ..., description="Location preference"
    )
    goals: List[str] = Field(
        default_factory=list,
        description="Career goals (internship, research, masters, phd, etc.)"
    )
    has_transfer_credits: bool = Field(
        default=False, description="Has existing college credits"
    )
    veteran_status: bool = Field(default=False, description="Veteran or active military")
    work_schedule: Literal["full-time-student", "part-time-student"] = Field(
        default="full-time-student", description="Work schedule"
    )

    @field_validator("career")
    @classmethod
    def validate_career(cls, v: str) -> str:
        """Ensure career is not empty"""
        if not v.strip():
            raise ValueError("Career cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "career": "Mechanical Engineer",
                "current_education": "hs",
                "gpa": 3.5,
                "budget": "medium",
                "timeline": "normal",
                "location": "miami",
                "goals": ["internship", "PE_license"],
                "has_transfer_credits": False,
                "veteran_status": False,
                "work_schedule": "full-time-student"
            }
        }


class ProfileData(BaseModel):
    """Structured profile extracted from quiz"""
    career: str
    category: str = Field(..., description="Career category (e.g., STEM-Engineering)")
    constraints: dict = Field(..., description="Budget, timeline, GPA constraints")
    preferences: List[str] = Field(default_factory=list)
    flags: List[str] = Field(
        default_factory=list,
        description="Special flags (e.g., community_college_optimal)"
    )
    recommendations: List[str] = Field(default_factory=list)
