"""
IntakeProfilerAgent - Analyzes quiz responses to create structured student profile
"""
import json
from typing import Dict, Any
from pathlib import Path
from .base import BaseAgent
from schemas.quiz_input import QuizInput, ProfileData


class IntakeProfilerAgent(BaseAgent):
    """Analyzes student quiz data and creates structured profile"""

    def __init__(self):
        prompt_file = Path(__file__).parent.parent / "prompts" / "intake_profiler.txt"
        super().__init__(
            model_name="gemini-2.0-flash-exp",
            temperature=0.2,
            system_prompt_file=str(prompt_file)
        )

    def run(self, input_data: Dict[str, Any]) -> ProfileData:
        """
        Analyze quiz data and extract structured profile

        Args:
            input_data: Quiz responses (validated QuizInput)

        Returns:
            ProfileData with career category, constraints, flags, recommendations
        """
        # Validate input
        quiz = QuizInput(**input_data)

        # Build prompt for Gemini
        prompt = f"""
Analyze this student quiz data and create a structured profile.

Quiz Data:
```json
{quiz.model_dump_json(indent=2)}
```

Return ONLY a JSON object (no markdown, no explanation) with the structure:
{{
  "career": "Career Name",
  "category": "STEM-Engineering|STEM-Technology|Healthcare|Business|etc",
  "constraints": {{
    "budget": "low|medium|high",
    "timeline": "X-years",
    "gpa": 0.0,
    "hasAA": true|false,
    "location": "miami|florida|anywhere",
    "work_schedule": "full-time-student|part-time-student"
  }},
  "preferences": ["list", "of", "preferences"],
  "flags": ["community_college_optimal", "bright_futures_eligible", etc],
  "recommendations": ["specific recommendations"]
}}

Be specific about MDC program codes. Consider Florida programs (Bright Futures, etc.).
"""

        # Generate response
        response = self.generate(prompt)

        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()

            profile_dict = json.loads(response)
            return ProfileData(**profile_dict)

        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Response: {response}")

            # Return minimal profile
            return ProfileData(
                career=quiz.career,
                category="Unknown",
                constraints={
                    "budget": quiz.budget,
                    "timeline": quiz.timeline,
                    "gpa": quiz.gpa,
                    "hasAA": quiz.current_education == "aa",
                    "location": quiz.location
                },
                preferences=quiz.goals,
                flags=[],
                recommendations=[]
            )
