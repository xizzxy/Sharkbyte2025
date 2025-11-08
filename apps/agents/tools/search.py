"""
Google Programmable Custom Search wrapper
Searches only trusted education domains
"""
import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


def search_education_sites(
    query: str,
    num_results: int = 10,
    site_restrictions: Optional[List[str]] = None
) -> List[Dict]:
    """
    Search only trusted educational institution domains.

    Args:
        query: Search query
        num_results: Number of results to return (max 10 per request)
        site_restrictions: List of domains to restrict to

    Returns:
        List of search results with title, link, snippet

    Example:
        >>> results = search_education_sites("mechanical engineering program")
        >>> print(results[0]["title"])
    """
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

    if not api_key or not engine_id:
        raise ValueError(
            "Missing GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_ENGINE_ID in environment"
        )

    # Default trusted domains
    if site_restrictions is None:
        site_restrictions = [
            "mdc.edu",
            "fiu.edu",
            "fau.edu",
            "ucf.edu",
            "uf.edu",
            "floridashines.org",
            "ed.gov"
        ]

    # Build site restriction query
    site_query = " OR ".join([f"site:{domain}" for domain in site_restrictions])
    full_query = f"{query} {site_query}"

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": engine_id,
        "q": full_query,
        "num": min(num_results, 10)  # API limit is 10 per request
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "items" not in data:
            return []

        return [
            {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "domain": extract_domain(item.get("link", ""))
            }
            for item in data["items"]
        ]

    except requests.exceptions.RequestException as e:
        print(f"Search API error: {e}")
        return []


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return ""


def extract_program_details(html_content: str, program_type: str = "engineering") -> Dict:
    """
    Extract structured program details from HTML/text content.
    This would be called by Gemini with the HTML content from search results.

    Args:
        html_content: HTML or text content to analyze
        program_type: Type of program to extract details for

    Returns:
        Structured program information

    Note:
        In production, this would use Gemini to analyze the content.
        For now, this is a placeholder that demonstrates the structure.
    """
    # This would be implemented as a Gemini function call
    # where Gemini analyzes the HTML and extracts structured data

    return {
        "program_name": "",
        "program_code": "",
        "credits": 0,
        "prerequisites": [],
        "description": "",
        "url": ""
    }


def search_mdc_programs(career: str) -> List[Dict]:
    """
    Search for MDC programs related to a career.

    Args:
        career: Career name (e.g., "Mechanical Engineer")

    Returns:
        List of relevant MDC programs
    """
    query = f"{career} program degree site:mdc.edu"
    return search_education_sites(query, num_results=5, site_restrictions=["mdc.edu"])


def search_transfer_agreements(university: str, mdc_program: str) -> List[Dict]:
    """
    Search for articulation/transfer agreements.

    Args:
        university: University name (e.g., "FIU")
        mdc_program: MDC program code or name

    Returns:
        List of transfer agreement documents
    """
    query = f"MDC {mdc_program} transfer agreement articulation {university}"
    return search_education_sites(
        query,
        num_results=5,
        site_restrictions=["mdc.edu", "fiu.edu", "fau.edu", "floridashines.org"]
    )


def search_licensing_requirements(profession: str, state: str = "Florida") -> List[Dict]:
    """
    Search for professional licensing requirements.

    Args:
        profession: Profession name (e.g., "Professional Engineer")
        state: State for licensing requirements

    Returns:
        List of licensing requirement documents
    """
    query = f"{profession} license requirements {state} examination"
    return search_education_sites(
        query,
        num_results=5,
        site_restrictions=["ed.gov", "floridashines.org"]
    )
