"""
BLS (Bureau of Labor Statistics) Public Data API wrapper
Retrieves salary and job outlook data
"""
import os
import json
import requests
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load .env from careerpilot/.env (3 levels up from tools/bls.py)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def get_salary_data(
    occupation_code: str,
    start_year: int = 2019,
    end_year: int = 2024,
    use_api_v2: bool = True
) -> Dict:
    """
    Retrieve salary trends for a BLS occupation code.
    Refactored from BLS sample code.

    Args:
        occupation_code: BLS occupation code (e.g., "17-2141" for Mechanical Engineers)
        start_year: Start year for data
        end_year: End year for data
        use_api_v2: Use v2 API (requires registration key, higher limits)

    Returns:
        BLS API response with salary time series data

    Example:
        >>> data = get_salary_data("17-2141", 2022, 2024)
        >>> series = data["Results"]["series"][0]["data"]
        >>> print(series[0]["value"])  # Latest salary data
    """
    bls_api_key = os.getenv("BLS_API_KEY")

    # API endpoint
    if use_api_v2 and bls_api_key:
        url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    else:
        url = "https://api.bls.gov/publicAPI/v1/timeseries/data/"

    headers = {"Content-Type": "application/json"}

    # For OEWS (Occupational Employment and Wage Statistics)
    # Series ID format: OEUM{occupation_code}{area_code}{data_type}
    # Area code: 0000000 = National
    # Data type: 02 = Median hourly wage, 04 = Mean annual wage

    # Get both median hourly and mean annual
    series_ids = [
        f"OEUM{occupation_code.replace('-', '')}0000000002",  # Median hourly
        f"OEUM{occupation_code.replace('-', '')}0000000004",  # Mean annual
    ]

    payload = {
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year)
    }

    # Add registration key if available (increases rate limits)
    if bls_api_key:
        payload["registrationkey"] = bls_api_key

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"BLS API error: {e}")
        return {"status": "REQUEST_FAILED", "message": str(e)}


def get_bls_occupation_data(occupation_code: str) -> Dict[str, any]:
    """
    Get formatted occupation data (salary, growth, etc.)

    Args:
        occupation_code: BLS occupation code

    Returns:
        Formatted salary and job outlook data
    """
    data = get_salary_data(occupation_code, start_year=2022, end_year=2024)

    if data.get("status") != "REQUEST_SUCCEEDED":
        print(f"WARNING: BLS API failed for {occupation_code}. Using fallback data.")
        return _get_fallback_salary_data(occupation_code)

    results = data.get("Results", {})
    series_list = results.get("series", [])

    median_hourly = None
    mean_annual = None

    for series in series_list:
        series_id = series.get("seriesID", "")
        series_data = series.get("data", [])

        if not series_data:
            continue

        # Get most recent data point
        latest = series_data[0]
        value = float(latest.get("value", 0))

        if series_id.endswith("02"):  # Median hourly
            median_hourly = value
        elif series_id.endswith("04"):  # Mean annual
            mean_annual = value

    # Calculate annual from hourly if needed
    if median_hourly and not mean_annual:
        mean_annual = median_hourly * 2080  # 40 hours/week * 52 weeks

    return {
        "occupation_code": occupation_code,
        "median_hourly_wage": median_hourly,
        "mean_annual_wage": mean_annual,
        "median_annual_salary": median_hourly * 2080 if median_hourly else mean_annual,
        "data_year": series_data[0].get("year") if series_data else None
    }


def calculate_roi(
    median_salary: float,
    education_cost: float,
    years_in_school: float = 4.0,
    tax_rate: float = 0.25
) -> float:
    """
    Calculate years to break even on education investment.

    Args:
        median_salary: Expected annual salary after graduation
        education_cost: Total cost of education
        years_in_school: Years spent in school (opportunity cost)
        tax_rate: Effective tax rate

    Returns:
        Years to break even

    Example:
        >>> roi = calculate_roi(95000, 30000, 4.0)
        >>> print(f"{roi:.1f} years")
    """
    # After-tax salary
    net_salary = median_salary * (1 - tax_rate)

    # Opportunity cost: could have earned minimum wage during school
    # Florida minimum wage ~$12/hour = ~$25k/year
    opportunity_cost = 25000 * years_in_school

    # Total investment = education cost + opportunity cost
    total_investment = education_cost + opportunity_cost

    # Years to break even
    if net_salary <= 0:
        return float('inf')

    roi_years = total_investment / net_salary

    return roi_years


# Mapping of common careers to BLS occupation codes
# Source: https://www.bls.gov/soc/2018/major_groups.htm
CAREER_TO_BLS_CODE = {
    "mechanical engineer": "17-2141",
    "electrical engineer": "17-2071",
    "civil engineer": "17-2051",
    "software developer": "15-1252",
    "software engineer": "15-1252",
    "computer programmer": "15-1251",
    "registered nurse": "29-1141",
    "nurse": "29-1141",
    "architect": "17-1011",
    "accountant": "13-2011",
    "financial analyst": "13-2051",
    "data scientist": "15-2051",
    "physician": "29-1216",
    "dentist": "29-1021",
    "pharmacist": "29-1051",
    "physical therapist": "29-1123",
    "teacher": "25-2021",
    "lawyer": "23-1011",
    "paralegal": "23-2011",
}


def get_bls_code_for_career(career: str) -> Optional[str]:
    """
    Map career name to BLS occupation code.

    Args:
        career: Career name (e.g., "Mechanical Engineer")

    Returns:
        BLS occupation code or None
    """
    career_lower = career.lower().strip()

    # Direct match
    if career_lower in CAREER_TO_BLS_CODE:
        return CAREER_TO_BLS_CODE[career_lower]

    # Fuzzy match (contains)
    for key, code in CAREER_TO_BLS_CODE.items():
        if key in career_lower or career_lower in key:
            return code

    return None


def get_salary_for_career(career: str) -> Optional[Dict]:
    """
    Get salary data for a career by name.

    Args:
        career: Career name

    Returns:
        Salary data or None
    """
    bls_code = get_bls_code_for_career(career)

    if not bls_code:
        print(f"No BLS code found for career: {career}")
        return None

    return get_bls_occupation_data(bls_code)


# Job growth projections (2023-2033) - would be fetched from BLS in production
# Source: https://www.bls.gov/emp/tables/occupational-projections-and-characteristics.htm
JOB_GROWTH_DATA = {
    "17-2141": {"growth_rate": "4%", "outlook": "Average"},  # Mechanical Engineers
    "17-2071": {"growth_rate": "5%", "outlook": "Average"},  # Electrical Engineers
    "17-2051": {"growth_rate": "6%", "outlook": "Faster than average"},  # Civil Engineers
    "15-1252": {"growth_rate": "21%", "outlook": "Much faster than average"},  # Software Developers
    "29-1141": {"growth_rate": "6%", "outlook": "Faster than average"},  # Registered Nurses
    "17-1011": {"growth_rate": "5%", "outlook": "Average"},  # Architects
}


def get_job_outlook(occupation_code: str) -> Dict[str, str]:
    """Get job growth projection for an occupation"""
    return JOB_GROWTH_DATA.get(
        occupation_code,
        {"growth_rate": "Unknown", "outlook": "Data not available"}
    )


def _get_fallback_salary_data(occupation_code: str) -> Dict[str, any]:
    """
    Fallback salary data when BLS API is unavailable.
    Returns realistic estimates for common occupations.
    """
    fallback_salaries = {
        "17-2141": {  # Mechanical Engineers
            "occupation_code": "17-2141",
            "median_hourly_wage": 45.50,
            "mean_annual_wage": 95300,
            "median_annual_salary": 94640,
            "data_year": "2024"
        },
        "17-2071": {  # Electrical Engineers
            "occupation_code": "17-2071",
            "median_hourly_wage": 50.25,
            "mean_annual_wage": 107540,
            "median_annual_salary": 104520,
            "data_year": "2024"
        },
        "15-1252": {  # Software Developers
            "occupation_code": "15-1252",
            "median_hourly_wage": 55.00,
            "mean_annual_wage": 120730,
            "median_annual_salary": 114400,
            "data_year": "2024"
        },
        "29-1141": {  # Registered Nurses
            "occupation_code": "29-1141",
            "median_hourly_wage": 38.50,
            "mean_annual_wage": 81220,
            "median_annual_salary": 80080,
            "data_year": "2024"
        },
        "17-2051": {  # Civil Engineers
            "occupation_code": "17-2051",
            "median_hourly_wage": 42.50,
            "mean_annual_wage": 89940,
            "median_annual_salary": 88400,
            "data_year": "2024"
        }
    }

    if occupation_code in fallback_salaries:
        return fallback_salaries[occupation_code]

    # Generic fallback
    print(f"No fallback data for occupation code: {occupation_code}")
    return {
        "occupation_code": occupation_code,
        "median_hourly_wage": 30.00,
        "mean_annual_wage": 65000,
        "median_annual_salary": 62400,
        "data_year": "2024",
        "note": "Estimated fallback data"
    }
