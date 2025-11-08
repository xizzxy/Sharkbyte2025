#!/usr/bin/env python3
"""
Test script to verify environment variable loading.
Run this to ensure .env is properly configured.

Usage:
    python test_env.py
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from careerpilot/.env
# Navigate from apps/agents/ to careerpilot/.env
env_path = Path(__file__).parent.parent.parent / ".env"
print(f"Loading .env from: {env_path}")
print(f".env exists: {env_path.exists()}")
load_dotenv(dotenv_path=env_path)

def test_env_loading():
    """Test environment variable loading and fallback handling"""

    print("=" * 60)
    print("CareerPilot AI - Environment Configuration Test")
    print("=" * 60)
    print()

    # Required variables
    print("✓ REQUIRED VARIABLES:")
    print("-" * 60)

    gcp_project = os.getenv("GCP_PROJECT_ID")
    gcp_location = os.getenv("GCP_LOCATION")
    gcp_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if gcp_project and gcp_project != "your-gcp-project-id":
        print(f"✅ GCP_PROJECT_ID: {gcp_project}")
    else:
        print("❌ GCP_PROJECT_ID: NOT SET (required for Vertex AI)")

    if gcp_location:
        print(f"✅ GCP_LOCATION: {gcp_location}")
    else:
        print("❌ GCP_LOCATION: NOT SET (required for Vertex AI)")

    if gcp_credentials:
        credentials_path = Path(gcp_credentials)
        if credentials_path.is_absolute():
            exists = credentials_path.exists()
        else:
            # Relative to apps/agents/
            abs_path = Path(__file__).parent / gcp_credentials
            exists = abs_path.exists()

        if exists:
            print(f"✅ GOOGLE_APPLICATION_CREDENTIALS: {gcp_credentials} (file exists)")
        else:
            print(f"⚠️  GOOGLE_APPLICATION_CREDENTIALS: {gcp_credentials} (file NOT FOUND)")
    else:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS: NOT SET")

    print()

    # Optional variables with fallback
    print("✓ OPTIONAL VARIABLES (fallback data available):")
    print("-" * 60)

    scorecard_key = os.getenv("SCORECARD_API_KEY")
    if scorecard_key and scorecard_key != "your-scorecard-api-key":
        print(f"✅ SCORECARD_API_KEY: {'*' * 10}{scorecard_key[-4:]} (API enabled)")
    else:
        print("⚠️  SCORECARD_API_KEY: NOT SET (will use fallback data)")

    bls_key = os.getenv("BLS_API_KEY")
    if bls_key and bls_key != "your-bls-registration-key":
        print(f"✅ BLS_API_KEY: {'*' * 10}{bls_key[-4:]} (API enabled)")
    else:
        print("⚠️  BLS_API_KEY: NOT SET (will use fallback data)")

    search_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    search_engine = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    if search_key and search_key != "your-google-search-api-key":
        print(f"✅ GOOGLE_SEARCH_API_KEY: {'*' * 10}{search_key[-4:]} (API enabled)")
    else:
        print("⚠️  GOOGLE_SEARCH_API_KEY: NOT SET (will use seed data)")

    if search_engine and search_engine != "your-custom-search-engine-id":
        print(f"✅ GOOGLE_SEARCH_ENGINE_ID: {search_engine}")
    else:
        print("⚠️  GOOGLE_SEARCH_ENGINE_ID: NOT SET")

    print()
    print("=" * 60)
    print()

    # Test API fallback functions
    print("✓ TESTING API FALLBACK FUNCTIONS:")
    print("-" * 60)

    try:
        from tools.scorecard import get_college_costs
        fiu_costs = get_college_costs("Florida International University")
        if fiu_costs.get("in_state_tuition", 0) > 0:
            print(f"✅ College Scorecard API/Fallback: Working")
            print(f"   → FIU In-State Tuition: ${fiu_costs['in_state_tuition']:,.0f}")
        else:
            print("❌ College Scorecard: Failed to retrieve data")
    except Exception as e:
        print(f"❌ College Scorecard: Error - {e}")

    try:
        from tools.bls import get_salary_for_career
        salary_data = get_salary_for_career("Software Developer")
        if salary_data and salary_data.get("mean_annual_wage"):
            print(f"✅ BLS API/Fallback: Working")
            print(f"   → Software Developer Median Salary: ${salary_data['mean_annual_wage']:,.0f}")
        else:
            print("❌ BLS API: Failed to retrieve data")
    except Exception as e:
        print(f"❌ BLS API: Error - {e}")

    print()
    print("=" * 60)
    print()

    # Summary
    has_gcp = gcp_project and gcp_project != "your-gcp-project-id"

    if has_gcp:
        print("✅ CONFIGURATION STATUS: Ready to run")
        print("   Run: python main.py")
    else:
        print("❌ CONFIGURATION STATUS: Missing required GCP credentials")
        print("   Please configure GCP_PROJECT_ID and GOOGLE_APPLICATION_CREDENTIALS")
        print("   See README.md for setup instructions")

    print()
    print("=" * 60)

if __name__ == "__main__":
    test_env_loading()
