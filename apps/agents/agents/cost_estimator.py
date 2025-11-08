"""
CostEstimatorAgent - Calculates education costs for different paths
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
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

        # Load seed data for housing costs and university rankings
        self._load_seed_data()

    def _load_seed_data(self):
        """Load housing costs and university rankings from seed data"""
        seed_dir = Path(__file__).parent.parent.parent.parent / "data" / "seed"

        try:
            with open(seed_dir / "housing_costs.json", 'r') as f:
                self.housing_data = json.load(f)
            print(f"[CostEstimator] Loaded housing data for {len(self.housing_data)} cities")
        except Exception as e:
            print(f"[CostEstimator] Failed to load housing_costs.json: {e}")
            self.housing_data = {}

        try:
            with open(seed_dir / "university_rankings.json", 'r') as f:
                self.rankings_data = json.load(f)
            print(f"[CostEstimator] Loaded ranking data for {len(self.rankings_data)} universities")
        except Exception as e:
            print(f"[CostEstimator] Failed to load university_rankings.json: {e}")
            self.rankings_data = {}

    def _get_housing_cost(self, city: str) -> Dict[str, float]:
        """Get housing cost data for a city"""
        if city in self.housing_data:
            housing = self.housing_data[city]
            monthly = housing.get("avg_rent_shared", 1100) + housing.get("avg_food", 350) + housing.get("avg_transport", 110)
            print(f"[Housing] city={city} monthly=${monthly:,.0f}")
            return housing

        # Try fuzzy matching
        for city_key in self.housing_data.keys():
            if city.lower() in city_key.lower() or city_key.lower() in city.lower():
                housing = self.housing_data[city_key]
                monthly = housing.get("avg_rent_shared", 1100) + housing.get("avg_food", 350) + housing.get("avg_transport", 110)
                print(f"[Housing] city={city} (matched={city_key}) monthly=${monthly:,.0f}")
                return housing

        # Default to Miami costs
        print(f"[Housing] city={city} monthly=$1560 (WARNING: No data found, using Miami defaults)")
        return {
            "avg_rent_shared": 1100,
            "avg_rent_studio": 1600,
            "avg_food": 350,
            "avg_transport": 110
        }

    def _get_tuition(self, university_name: str, in_state: bool) -> float:
        """Get tuition from rankings data or College Scorecard"""
        # Try rankings data first
        for uni_key, uni_data in self.rankings_data.items():
            if uni_key.lower() in university_name.lower() or university_name.lower() in uni_key.lower():
                if in_state and "tuition_in_state" in uni_data:
                    tuition = uni_data["tuition_in_state"]
                    if tuition > 0:
                        print(f"[Tuition] source=seed in_state={in_state} {university_name}=${tuition:,.0f}/yr")
                        return tuition
                elif not in_state and "tuition_out_of_state" in uni_data:
                    tuition = uni_data["tuition_out_of_state"]
                    if tuition > 0:
                        print(f"[Tuition] source=seed in_state={in_state} {university_name}=${tuition:,.0f}/yr")
                        return tuition

        # Fallback to College Scorecard
        costs = get_college_costs(university_name)
        tuition_key = "in_state_tuition" if in_state else "out_of_state_tuition"
        scorecard_tuition = costs.get(tuition_key, 0)

        # If scorecard returns 0 or null, use a reasonable default based on school type
        if scorecard_tuition > 0:
            print(f"[Tuition] source=scorecard in_state={in_state} {university_name}=${scorecard_tuition:,.0f}/yr")
            return scorecard_tuition

        # Last resort fallback - try rankings data one more time with any value
        for uni_key, uni_data in self.rankings_data.items():
            if uni_key.lower() in university_name.lower() or university_name.lower() in uni_key.lower():
                fallback = uni_data.get("tuition_out_of_state", uni_data.get("tuition_in_state", 15000))
                print(f"[Tuition] source=seed_fallback in_state={in_state} {university_name}=${fallback:,.0f}/yr")
                return max(fallback, 10000)  # Enforce minimum $10k

        # Generic fallback - use realistic minimums
        if in_state:
            fallback = 6000  # Typical FL public in-state
        else:
            fallback = 20000  # Typical FL public out-of-state
        print(f"[Tuition] source=generic_fallback in_state={in_state} {university_name}=${fallback:,.0f}/yr (WARNING: No data found)")
        return fallback

    def _get_university_location(self, university_name: str) -> str:
        """Get university location from rankings data"""
        for uni_key, uni_data in self.rankings_data.items():
            if uni_key.lower() in university_name.lower() or university_name.lower() in uni_key.lower():
                return uni_data.get("location", "Miami, FL")

        # Default to Miami
        return "Miami, FL"

    def _calculate_realistic_cost(
        self,
        university_name: str,
        in_state: bool,
        mdc_years: float = 2.0,
        university_years: float = 2.0
    ) -> Dict[str, float]:
        """
        Calculate realistic total cost including tuition, housing, food, transport

        Args:
            university_name: Name of university
            in_state: Whether student is in-state
            mdc_years: Years at MDC
            university_years: Years at university

        Returns:
            Complete cost breakdown
        """
        # MDC costs (very low tuition, stay at home assumed)
        mdc_tuition_per_year = 3400 if in_state else 12000
        mdc_total = mdc_tuition_per_year * mdc_years
        print(f"[CostEstimator] node=AA school=MDC tuition_y=${mdc_tuition_per_year:,.0f} years={mdc_years} housing_m=$0 total=${mdc_total:,.0f}")

        # University location and housing
        location = self._get_university_location(university_name)
        housing_data = self._get_housing_cost(location)

        # University tuition
        tuition_per_year = self._get_tuition(university_name, in_state)

        # Living expenses per year
        yearly_rent = housing_data.get("avg_rent_shared", 1100) * 12
        yearly_food = housing_data.get("avg_food", 350) * 12
        yearly_transport = housing_data.get("avg_transport", 110) * 12
        yearly_living = yearly_rent + yearly_food + yearly_transport

        # University total cost (tuition + living expenses)
        university_total = (tuition_per_year + yearly_living) * university_years

        # Books and fees
        books = 1200 * (mdc_years + university_years)
        fees = (mdc_total + (tuition_per_year * university_years)) * 0.12

        total = mdc_total + university_total + books + fees

        print(f"[CostEstimator] node=BS school={university_name} tuition_y=${tuition_per_year:,.0f} years={university_years} housing_m=${yearly_living/12:,.0f} total=${total:,.0f}")

        return {
            "mdc": mdc_total,
            "university_tuition": tuition_per_year * university_years,
            "university_housing": yearly_rent * university_years,
            "university_food": yearly_food * university_years,
            "university_transport": yearly_transport * university_years,
            "books": books,
            "fees": fees,
            "total": total,
            "breakdown": {
                "institution": university_name,
                "location": location,
                "years_mdc": mdc_years,
                "years_university": university_years,
                "resident_status": "in-state" if in_state else "out-of-state"
            }
        }

    def _calculate_masters_cost(
        self,
        university_name: str,
        in_state: bool,
        years: float = 2.0
    ) -> Dict[str, float]:
        """
        Calculate realistic Masters degree cost

        Args:
            university_name: Name of university
            in_state: Whether student is in-state
            years: Years for Masters (typically 1-2)

        Returns:
            Complete cost breakdown for Masters
        """
        # Graduate tuition (typically 20% higher than undergrad)
        undergrad_tuition = self._get_tuition(university_name, in_state)
        masters_tuition_per_year = undergrad_tuition * 1.2

        # Location and housing
        location = self._get_university_location(university_name)
        housing_data = self._get_housing_cost(location)

        # Living expenses per year
        yearly_rent = housing_data.get("avg_rent_shared", 1100) * 12
        yearly_food = housing_data.get("avg_food", 350) * 12
        yearly_transport = housing_data.get("avg_transport", 110) * 12
        yearly_living = yearly_rent + yearly_food + yearly_transport

        # Total cost
        total_tuition = masters_tuition_per_year * years
        total_living = yearly_living * years
        books = 1000 * years
        fees = total_tuition * 0.1

        total = total_tuition + total_living + books + fees

        print(f"[CostEstimator] node=MS school={university_name} tuition_y=${masters_tuition_per_year:,.0f} years={years} housing_m=${yearly_living/12:,.0f} total=${total:,.0f}")

        return {
            "tuition": total_tuition,
            "housing": yearly_rent * years,
            "food": yearly_food * years,
            "transport": yearly_transport * years,
            "books": books,
            "fees": fees,
            "total": total,
            "breakdown": {
                "institution": university_name,
                "location": location,
                "years": years,
                "resident_status": "in-state" if in_state else "out-of-state",
                "degree_type": "Masters"
            }
        }

    def _calculate_phd_cost(
        self,
        university_name: str,
        years: float = 5.0
    ) -> Dict[str, float]:
        """
        Calculate realistic PhD cost (typically funded, student pays living expenses only)

        Args:
            university_name: Name of university
            years: Years for PhD (typically 4-6)

        Returns:
            Complete cost breakdown for PhD
        """
        # PhDs are usually funded (tuition waived + stipend), but student still needs housing
        location = self._get_university_location(university_name)
        housing_data = self._get_housing_cost(location)

        # Living expenses per year (PhD stipend typically covers ~70% of living costs)
        yearly_rent = housing_data.get("avg_rent_shared", 1100) * 12
        yearly_food = housing_data.get("avg_food", 350) * 12
        yearly_transport = housing_data.get("avg_transport", 110) * 12
        yearly_living = yearly_rent + yearly_food + yearly_transport

        # Student pays ~30% out of pocket (stipend covers rest)
        out_of_pocket_yearly = yearly_living * 0.3

        # Total cost
        total_living = out_of_pocket_yearly * years
        books = 800 * years  # Research materials
        fees = 500 * years  # Conference travel, etc.

        total = total_living + books + fees

        print(f"[CostEstimator] node=PhD school={university_name} tuition_y=$0 years={years} housing_m=${out_of_pocket_yearly/12:,.0f} total=${total:,.0f} (tuition_waived+stipend)")

        return {
            "tuition": 0,  # Waived for funded PhD
            "living_expenses": total_living,
            "books": books,
            "fees": fees,
            "total": total,
            "breakdown": {
                "institution": university_name,
                "location": location,
                "years": years,
                "degree_type": "PhD",
                "note": "PhD typically funded - tuition waived, stipend covers ~70% of living costs"
            }
        }

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
        university_years = 2 if not has_aa else 2

        # Cheapest path: MDC → FIU/FAU (in-state)
        cheapest_university = "Florida International University"
        if transfer_options:
            # Pick most affordable Florida option
            for option in transfer_options:
                uni = option.get("university", "")
                if "FIU" in uni.upper() or "FAU" in uni.upper() or "UCF" in uni.upper():
                    cheapest_university = uni
                    break

        cheapest_cost = self._calculate_realistic_cost(
            university_name=cheapest_university,
            in_state=True,
            mdc_years=mdc_years,
            university_years=university_years
        )

        # Fastest path: Same as cheapest but accelerated (15% premium for summer classes)
        fastest_cost = cheapest_cost.copy()
        fastest_cost["total"] = cheapest_cost["total"] * 1.15

        # Prestige path: Top-ranked university (may be out-of-state)
        prestige_university = "University of Florida"  # Default
        prestige_in_state = True

        if transfer_options:
            # Find highest-tier university from transfer options
            best_tier = 999
            for option in transfer_options:
                uni_name = option.get("university", "")
                # Check rankings
                for uni_key, uni_data in self.rankings_data.items():
                    if uni_key.lower() in uni_name.lower() or uni_name.lower() in uni_key.lower():
                        tier = uni_data.get("tier", 3)
                        if tier < best_tier:
                            best_tier = tier
                            prestige_university = uni_name
                            # Check if out-of-state
                            location = uni_data.get("location", "FL")
                            prestige_in_state = "FL" in location

        prestige_cost = self._calculate_realistic_cost(
            university_name=prestige_university,
            in_state=prestige_in_state,
            mdc_years=mdc_years,
            university_years=university_years
        )

        # Add certification/license costs
        cert_cost = 0
        for cert in pathway_result.get("certifications", []):
            if cert.get("required"):
                cert_cost += 200

        for license in pathway_result.get("licenses", []):
            if license.get("required"):
                cert_cost += 300

        cheapest_cost["total"] += cert_cost
        fastest_cost["total"] += cert_cost
        prestige_cost["total"] += cert_cost

        # Check if Masters or PhD is part of the goals
        goals = profile.get("goals", [])
        has_masters = "masters" in [g.lower() for g in goals]
        has_phd = "phd" in [g.lower() for g in goals]

        # Add Masters cost if needed
        masters_cost_data = None
        if has_masters:
            # Use prestige university for Masters (typically best option)
            masters_cost_data = self._calculate_masters_cost(
                university_name=prestige_university,
                in_state=prestige_in_state,
                years=2.0
            )
            # Add Masters to totals
            cheapest_cost["total"] += masters_cost_data["total"]
            fastest_cost["total"] += masters_cost_data["total"] * 0.85  # Can accelerate to 1.5yr
            prestige_cost["total"] += masters_cost_data["total"]
            prestige_cost["masters"] = masters_cost_data

        # Add PhD cost if needed
        phd_cost_data = None
        if has_phd:
            # PhDs typically at top-tier research universities
            phd_university = prestige_university
            phd_cost_data = self._calculate_phd_cost(
                university_name=phd_university,
                years=5.0
            )
            # Add PhD to totals
            cheapest_cost["total"] += phd_cost_data["total"]
            fastest_cost["total"] += phd_cost_data["total"] * 0.9  # Can accelerate to 4yr
            prestige_cost["total"] += phd_cost_data["total"]
            prestige_cost["phd"] = phd_cost_data

        print(f"[CostEstimator] Final totals - Cheapest: ${cheapest_cost['total']:.0f}, Fastest: ${fastest_cost['total']:.0f}, Prestige: ${prestige_cost['total']:.0f}")

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
