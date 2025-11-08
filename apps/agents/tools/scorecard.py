"""
College Scorecard API wrapper
Retrieves tuition, completion rates, and other institutional data
"""
import os
import requests
from typing import Dict, Optional, List
from pathlib import Path
from dotenv import load_dotenv

# Load .env from careerpilot/.env (3 levels up from tools/scorecard.py)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def get_college_data(institution_name: str) -> Optional[Dict]:
    """
    Retrieve college data from the College Scorecard API.

    Args:
        institution_name: Name of the institution (e.g., "Florida International University")

    Returns:
        Dictionary with tuition, completion rate, admission rate, etc.

    Example:
        >>> data = get_college_data("Florida International University")
        >>> print(data["latest.cost.tuition.in_state"])
        6565
    """
    api_key = os.getenv("SCORECARD_API_KEY")

    if not api_key:
        print("WARNING: Missing SCORECARD_API_KEY in environment. Using fallback data.")
        return _get_fallback_college_data(institution_name)

    url = "https://api.data.gov/ed/collegescorecard/v1/schools"
    params = {
        "api_key": api_key,
        "school.name": institution_name,
        "fields": ",".join([
            "id",
            "school.name",
            "school.city",
            "school.state",
            "latest.cost.tuition.in_state",
            "latest.cost.tuition.out_of_state",
            "latest.cost.attendance.academic_year",
            "latest.admissions.admission_rate.overall",
            "latest.completion.completion_rate_4yr_150nt",
            "latest.student.size",
            "latest.cost.avg_net_price.overall"
        ])
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            print(f"No results found for institution: {institution_name}")
            return None

        # Return first result (most relevant)
        return data["results"][0]

    except requests.exceptions.RequestException as e:
        print(f"College Scorecard API error: {e}")
        return None


def get_college_costs(institution_name: str) -> Dict[str, float]:
    """
    Get simplified cost breakdown for an institution.

    Args:
        institution_name: Name of institution

    Returns:
        Dictionary with tuition, fees, and net price

    Example:
        >>> costs = get_college_costs("FIU")
        >>> print(costs["in_state_tuition"])
        6565
    """
    data = get_college_data(institution_name)

    if not data:
        return {
            "in_state_tuition": 0.0,
            "out_of_state_tuition": 0.0,
            "net_price": 0.0,
            "total_cost_of_attendance": 0.0
        }

    latest = data.get("latest", {})
    cost = latest.get("cost", {})
    tuition = cost.get("tuition", {})
    attendance = cost.get("attendance", {})

    return {
        "in_state_tuition": float(tuition.get("in_state") or 0),
        "out_of_state_tuition": float(tuition.get("out_of_state") or 0),
        "net_price": float(cost.get("avg_net_price", {}).get("overall") or 0),
        "total_cost_of_attendance": float(attendance.get("academic_year") or 0)
    }


def get_multiple_college_costs(institution_names: List[str]) -> Dict[str, Dict]:
    """
    Get costs for multiple institutions.

    Args:
        institution_names: List of institution names

    Returns:
        Dictionary mapping institution name to cost data
    """
    results = {}

    for name in institution_names:
        results[name] = get_college_costs(name)

    return results


def estimate_total_education_cost(
    mdc_years: float = 2.0,
    university_name: str = "Florida International University",
    university_years: float = 2.0,
    is_florida_resident: bool = True
) -> Dict[str, float]:
    """
    Estimate total cost for MDC → University pathway.

    Args:
        mdc_years: Years at MDC (typically 2)
        university_name: Transfer university
        university_years: Years at university (typically 2 for transfer students)
        is_florida_resident: Whether student is FL resident

    Returns:
        Cost breakdown with total
    """
    # MDC tuition is very low (~$100/credit hour for FL residents)
    mdc_cost_per_year = 3400 if is_florida_resident else 12000
    mdc_total = mdc_cost_per_year * mdc_years

    # Get university costs
    university_costs = get_college_costs(university_name)
    tuition_key = "in_state_tuition" if is_florida_resident else "out_of_state_tuition"
    university_cost_per_year = university_costs.get(tuition_key, 10000)
    university_total = university_cost_per_year * university_years

    # Estimate fees (typically 10-15% of tuition)
    fees = (mdc_total + university_total) * 0.12

    # Estimate books (~$1200/year)
    books = 1200 * (mdc_years + university_years)

    total = mdc_total + university_total + fees + books

    return {
        "mdc": mdc_total,
        "university": university_total,
        "fees": fees,
        "books": books,
        "total": total,
        "breakdown": {
            "institution": university_name,
            "years_mdc": mdc_years,
            "years_university": university_years,
            "resident_status": "in-state" if is_florida_resident else "out-of-state"
        }
    }


# Common Florida institutions mapping (for fuzzy matching)
INSTITUTION_ALIASES = {
    "mdc": "Miami Dade College",
    "fiu": "Florida International University",
    "fau": "Florida Atlantic University",
    "ucf": "University of Central Florida",
    "uf": "University of Florida",
    "fsu": "Florida State University",
    "usf": "University of South Florida",
    "mit": "Massachusetts Institute of Technology",
    "georgia tech": "Georgia Institute of Technology",
}


def normalize_institution_name(name: str) -> str:
    """Normalize institution name for API query"""
    name_lower = name.lower().strip()

    # Check aliases first
    if name_lower in INSTITUTION_ALIASES:
        return INSTITUTION_ALIASES[name_lower]

    return name


def _get_fallback_college_data(institution_name: str) -> Optional[Dict]:
    """
    Fallback college data when API key is not available.
    Returns realistic seed data for common Florida institutions.
    """
    fallback_data = {
        "Florida International University": {
            "id": 133951,
            "school.name": "Florida International University",
            "school.city": "Miami",
            "school.state": "FL",
            "latest.cost.tuition.in_state": 6565,
            "latest.cost.tuition.out_of_state": 18566,
            "latest.cost.attendance.academic_year": 21000,
            "latest.admissions.admission_rate.overall": 0.64,
            "latest.completion.completion_rate_4yr_150nt": 0.52,
            "latest.student.size": 56851,
            "latest.cost.avg_net_price.overall": 8500
        },
        "Miami Dade College": {
            "id": 135726,
            "school.name": "Miami Dade College",
            "school.city": "Miami",
            "school.state": "FL",
            "latest.cost.tuition.in_state": 3400,
            "latest.cost.tuition.out_of_state": 12000,
            "latest.cost.attendance.academic_year": 10000,
            "latest.admissions.admission_rate.overall": 1.0,
            "latest.completion.completion_rate_4yr_150nt": 0.23,
            "latest.student.size": 50000,
            "latest.cost.avg_net_price.overall": 4200
        },
        "University of Florida": {
            "id": 134130,
            "school.name": "University of Florida",
            "school.city": "Gainesville",
            "school.state": "FL",
            "latest.cost.tuition.in_state": 6380,
            "latest.cost.tuition.out_of_state": 28658,
            "latest.cost.attendance.academic_year": 23000,
            "latest.admissions.admission_rate.overall": 0.23,
            "latest.completion.completion_rate_4yr_150nt": 0.88,
            "latest.student.size": 56567,
            "latest.cost.avg_net_price.overall": 9200
        }
    }

    # Check for exact match
    if institution_name in fallback_data:
        return fallback_data[institution_name]

    # Check normalized name
    normalized = normalize_institution_name(institution_name)
    if normalized in fallback_data:
        return fallback_data[normalized]

    # Return generic fallback
    print(f"No fallback data for: {institution_name}. Using generic estimates.")
    return {
        "id": 0,
        "school.name": institution_name,
        "school.city": "Unknown",
        "school.state": "FL",
        "latest.cost.tuition.in_state": 8000,
        "latest.cost.tuition.out_of_state": 20000,
        "latest.cost.attendance.academic_year": 18000,
        "latest.admissions.admission_rate.overall": 0.5,
        "latest.completion.completion_rate_4yr_150nt": 0.4,
        "latest.student.size": 10000,
        "latest.cost.avg_net_price.overall": 10000
    }
