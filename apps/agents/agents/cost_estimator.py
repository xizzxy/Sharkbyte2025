"""
CostEstimatorAgent - Calculates education costs for different paths
"""
from typing import Dict, Any
from .base import BaseAgent
from schemas.roadmap_output import CostResult
from tools.scorecard import get_college_costs, estimate_total_education_cost, normalize_institution_name


class CostEstimatorAgent(BaseAgent):
    """Calculates total costs for cheapest, fastest, and prestige paths"""

    def __init__(self):
        super().__init__(
            model_name="gemini-2.0-flash-exp",
            temperature=0.1  # Lower temp for consistent calculations
        )

    def run(self, input_data: Dict[str, Any]) -> CostResult:
        """
        Calculate costs for 3 paths

        Args:
            input_data: Profile and pathway data

        Returns:
            CostResult with cheapest, fastest, prestige breakdowns
        """
        profile = input_data.get("profile", {})
        pathway_result = input_data.get("pathway_result", {})

        budget = profile.get("constraints", {}).get("budget", "medium")
        has_aa = profile.get("constraints", {}).get("hasAA", False)

        transfer_options = pathway_result.get("transfer_options", [])

        print(f"[CostEstimator] Calculating costs (budget={budget}, hasAA={has_aa})")

        # Determine MDC years (0 if has AA, 2 otherwise)
        mdc_years = 0 if has_aa else 2
        university_years = 2 if not has_aa else 2  # Adjust if needed

        # Cheapest path: MDC → FIU/FAU
        cheapest_university = "Florida International University"
        if transfer_options:
            # Pick most affordable option (FIU, FAU, UCF)
            for option in transfer_options:
                uni = option.get("university", "")
                if uni.upper() in ["FIU", "FAU", "UCF"]:
                    cheapest_university = normalize_institution_name(uni)
                    break

        cheapest_cost = estimate_total_education_cost(
            mdc_years=mdc_years,
            university_name=cheapest_university,
            university_years=university_years,
            is_florida_resident=True
        )

        # Fastest path: Same as cheapest but accelerated (summer classes)
        fastest_cost = cheapest_cost.copy()
        fastest_cost["total"] = cheapest_cost["total"] * 1.15  # 15% more for summer

        # Prestige path: Out-of-state or private
        prestige_university = "Georgia Institute of Technology"  # For engineering
        prestige_cost = estimate_total_education_cost(
            mdc_years=mdc_years,
            university_name=prestige_university,
            university_years=university_years,
            is_florida_resident=False  # Out-of-state tuition
        )

        # Add certification/license costs
        cert_cost = 0
        for cert in pathway_result.get("certifications", []):
            if cert.get("required"):
                cert_cost += 200  # Typical exam fee

        for license in pathway_result.get("licenses", []):
            if license.get("required"):
                cert_cost += 300  # License fee

        cheapest_cost["total"] += cert_cost
        fastest_cost["total"] += cert_cost
        prestige_cost["total"] += cert_cost

        return CostResult(
            cheapest_path={
                "total": cheapest_cost["total"],
                "breakdown": cheapest_cost
            },
            fastest_path={
                "total": fastest_cost["total"],
                "breakdown": fastest_cost
            },
            prestige_path={
                "total": prestige_cost["total"],
                "breakdown": prestige_cost
            }
        )
