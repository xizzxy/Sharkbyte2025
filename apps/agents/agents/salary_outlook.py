"""
SalaryOutlookAgent - Retrieves salary and job outlook data
"""
from typing import Dict, Any
from .base import BaseAgent
from schemas.roadmap_output import SalaryResult
from tools.bls import get_bls_code_for_career, get_bls_occupation_data, get_job_outlook, calculate_roi


class SalaryOutlookAgent(BaseAgent):
    """Analyzes salary and job outlook for a career"""

    def __init__(self):
        super().__init__(
            model_name="gemini-2.0-flash-exp",
            temperature=0.1
        )

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

        # Map career to BLS occupation code
        bls_code = get_bls_code_for_career(career)

        if not bls_code:
            print(f"[SalaryOutlook] No BLS code found for {career}, using defaults")
            return SalaryResult(
                occupation=career,
                bls_code="Unknown",
                median_salary=60000,
                miami_salary=55000,
                growth_rate="Average",
                job_outlook="Data not available",
                roi_years=8.0
            )

        # Get salary data from BLS API
        try:
            salary_data = get_bls_occupation_data(bls_code)
            median_salary = salary_data.get("median_annual_salary") or 60000
        except Exception as e:
            print(f"[SalaryOutlook] BLS API error: {e}")
            median_salary = 60000  # Fallback

        # Get job outlook
        outlook = get_job_outlook(bls_code)

        # Calculate ROI (assuming ~$30k education cost)
        education_cost = 30000  # Will be adjusted based on actual path
        roi_years = calculate_roi(
            median_salary=median_salary,
            education_cost=education_cost,
            years_in_school=4.0
        )

        # Estimate Miami salary (typically 90% of national median for most careers)
        miami_salary = median_salary * 0.90

        return SalaryResult(
            occupation=career,
            bls_code=bls_code,
            median_salary=median_salary,
            miami_salary=miami_salary,
            growth_rate=outlook.get("growth_rate", "Average"),
            job_outlook=outlook.get("outlook", "Data not available"),
            roi_years=roi_years
        )
