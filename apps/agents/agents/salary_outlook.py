"""
SalaryOutlookAgent - Retrieves salary and job outlook data
"""
from typing import Dict, Any
from .base import BaseAgent
from schemas.roadmap_output import SalaryResult
from tools.bls import get_bls_code_for_career, get_bls_occupation_data, get_job_outlook, calculate_roi


class SalaryOutlookAgent(BaseAgent):
    """Analyzes salary and job outlook for a career"""

    # Realistic career-specific salary data (Bureau of Labor Statistics 2024)
    CAREER_SALARIES = {
        "software developer": {"median": 110000, "miami": 102000, "growth": "Much faster than average"},
        "software engineer": {"median": 110000, "miami": 102000, "growth": "Much faster than average"},
        "mechanical engineer": {"median": 96000, "miami": 88000, "growth": "Average"},
        "electrical engineer": {"median": 103000, "miami": 95000, "growth": "Average"},
        "civil engineer": {"median": 89000, "miami": 84000, "growth": "Average"},
        "registered nurse": {"median": 86000, "miami": 82000, "growth": "Much faster than average"},
        "nurse": {"median": 86000, "miami": 82000, "growth": "Much faster than average"},
        "accountant": {"median": 79000, "miami": 74000, "growth": "Average"},
        "data scientist": {"median": 103500, "miami": 96000, "growth": "Much faster than average"},
        "cybersecurity": {"median": 112000, "miami": 105000, "growth": "Much faster than average"},
        "architect": {"median": 82000, "miami": 78000, "growth": "Average"},
        "business analyst": {"median": 76000, "miami": 71000, "growth": "Average"},
        "finance": {"median": 76000, "miami": 71000, "growth": "Average"},
    }

    def __init__(self):
        super().__init__(
            model_name="gemini-2.0-flash-exp",
            temperature=0.1
        )

    def _get_career_salary_fallback(self, career: str) -> Dict[str, Any]:
        """Get realistic salary fallback based on career field"""
        career_lower = career.lower()

        # Try exact match first
        if career_lower in self.CAREER_SALARIES:
            return self.CAREER_SALARIES[career_lower]

        # Try fuzzy matching
        for key, data in self.CAREER_SALARIES.items():
            if key in career_lower or career_lower in key:
                return data

        # Generic default based on category patterns
        if any(word in career_lower for word in ["engineer", "tech", "software", "developer"]):
            return {"median": 95000, "miami": 88000, "growth": "Average"}
        elif any(word in career_lower for word in ["nurse", "medical", "health"]):
            return {"median": 82000, "miami": 78000, "growth": "Faster than average"}
        elif any(word in career_lower for word in ["business", "finance", "accounting"]):
            return {"median": 76000, "miami": 71000, "growth": "Average"}
        else:
            return {"median": 65000, "miami": 60000, "growth": "Average"}

    def run(self, input_data: Dict[str, Any]) -> SalaryResult:
        """
        Get salary outlook for a career

        Args:
            input_data: Career name and category

        Returns:
            SalaryResult with median salary, growth rate, ROI
        """
        career = input_data.get("career", "")
        category = input_data.get("category", "")

        print(f"[SalaryOutlook] Analyzing salary for {career}")

        # Get realistic career-specific fallback data
        fallback_data = self._get_career_salary_fallback(career)

        # Map career to BLS occupation code
        bls_code = get_bls_code_for_career(career)

        if not bls_code:
            print(f"[SalaryOutlook] No BLS code found for {career}, using career-specific fallback: ${fallback_data['median']}")
            return SalaryResult(
                occupation=career,
                bls_code="Unknown",
                median_salary=fallback_data["median"],
                miami_salary=fallback_data["miami"],
                growth_rate=fallback_data["growth"],
                job_outlook="Data not available - using industry averages",
                roi_years=8.0
            )

        # Get salary data from BLS API
        median_salary = None
        outlook = {}
        try:
            salary_data = get_bls_occupation_data(bls_code)
            median_salary = salary_data.get("median_annual_salary")

            # Get job outlook
            outlook = get_job_outlook(bls_code)
        except Exception as e:
            print(f"[SalaryOutlook] BLS API error: {e}, using career-specific fallback")

        # Use fallback if BLS API failed or returned no data
        if not median_salary or median_salary == 0:
            median_salary = fallback_data["median"]
            miami_salary = fallback_data["miami"]
            growth_rate = fallback_data["growth"]
            print(f"[SalaryOutlook] Using realistic fallback for {career}: ${median_salary} national, ${miami_salary} Miami")
        else:
            # BLS API succeeded - estimate Miami salary
            miami_salary = median_salary * 0.90
            growth_rate = outlook.get("growth_rate", fallback_data["growth"])

        # Calculate ROI (assuming ~$30k education cost)
        education_cost = 30000  # Will be adjusted based on actual path
        roi_years = calculate_roi(
            median_salary=median_salary,
            education_cost=education_cost,
            years_in_school=4.0
        )

        return SalaryResult(
            occupation=career,
            bls_code=bls_code or "Unknown",
            median_salary=median_salary,
            miami_salary=miami_salary,
            growth_rate=growth_rate,
            job_outlook=outlook.get("outlook", f"{growth_rate} job growth expected"),
            roi_years=roi_years
        )
