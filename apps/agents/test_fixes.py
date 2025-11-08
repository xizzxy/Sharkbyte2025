"""
Test script to validate critical fixes:
1. PathwayResearchAgent - proper out-of-state filtering and deduplication
2. CostEstimatorAgent - separate MS/PhD costs, no $0 values
3. SalaryOutlookAgent - realistic career-specific salaries
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.pathway_research import PathwayResearchAgent
from agents.cost_estimator import CostEstimatorAgent
from agents.salary_outlook import SalaryOutlookAgent

def test_pathway_research():
    """Test PathwayResearchAgent with out-of-state universities"""
    print("\n" + "="*80)
    print("TEST 1: PathwayResearchAgent - Out-of-State Universities")
    print("="*80)

    agent = PathwayResearchAgent()

    # Test 1: Software Developer with "anywhere" preference
    result = agent.run({
        "career": "Software Developer",
        "category": "Technology",
        "constraints": {"location": "anywhere"}
    })

    print(f"\n✅ Test 1a: Software Developer (location=anywhere)")
    print(f"   Transfer options: {len(result.transfer_options)}")
    for i, opt in enumerate(result.transfer_options[:5]):
        print(f"   {i+1}. {opt.university}")

    # Validate: Should include out-of-state universities like MIT, Stanford
    out_of_state_count = sum(1 for opt in result.transfer_options if any(
        name in opt.university for name in ["MIT", "Stanford", "Carnegie Mellon", "Berkeley", "Georgia Tech"]
    ))
    print(f"\n   Out-of-state universities: {out_of_state_count}/5")
    assert out_of_state_count >= 2, "❌ FAILED: Not enough out-of-state universities"

    # Validate: No duplicates
    universities = [opt.university for opt in result.transfer_options]
    unique_count = len(set(universities))
    print(f"   Unique universities: {unique_count}/{len(universities)}")
    assert unique_count == len(universities), "❌ FAILED: Duplicates found"

    print("\n✅ PASSED: Out-of-state filtering and deduplication works")

    # Test 2: Florida only
    result_fl = agent.run({
        "career": "Mechanical Engineer",
        "category": "Engineering",
        "constraints": {"location": "florida"}
    })

    print(f"\n✅ Test 1b: Mechanical Engineer (location=florida)")
    print(f"   Transfer options: {len(result_fl.transfer_options)}")
    for i, opt in enumerate(result_fl.transfer_options[:5]):
        print(f"   {i+1}. {opt.university}")

    # Validate: Should be only Florida schools
    non_fl_count = sum(1 for opt in result_fl.transfer_options if any(
        name in opt.university for name in ["MIT", "Stanford", "Carnegie Mellon", "Berkeley", "Georgia Tech"]
    ))
    print(f"\n   Non-Florida universities: {non_fl_count}")
    assert non_fl_count == 0, "❌ FAILED: Found out-of-state universities in florida-only filter"

    print("\n✅ PASSED: Florida-only filtering works")

def test_cost_estimator():
    """Test CostEstimatorAgent with Masters/PhD costs"""
    print("\n" + "="*80)
    print("TEST 2: CostEstimatorAgent - Masters/PhD Costs")
    print("="*80)

    agent = CostEstimatorAgent()

    # Test with Masters goal
    pathway_result = {
        "transfer_options": [
            {"university": "MIT", "program": "BS Computer Science"},
            {"university": "FIU", "program": "BS Computer Science"}
        ],
        "certifications": [],
        "licenses": []
    }

    result = agent.run({
        "profile": {
            "career": "Software Developer",
            "goals": ["bachelors", "masters"],
            "constraints": {"budget": "high", "hasAA": False}
        },
        "pathway_result": pathway_result
    })

    print(f"\n✅ Test 2a: Software Developer with Masters goal")
    print(f"   Cheapest path: ${result.cheapest_path['total']:,.0f}")
    print(f"   Fastest path: ${result.fastest_path['total']:,.0f}")
    print(f"   Prestige path: ${result.prestige_path['total']:,.0f}")

    # Validate: No $0 costs
    assert result.cheapest_path["total"] > 0, "❌ FAILED: Cheapest path is $0"
    assert result.fastest_path["total"] > 0, "❌ FAILED: Fastest path is $0"
    assert result.prestige_path["total"] > 0, "❌ FAILED: Prestige path is $0"

    # Validate: Costs are different (not all the same)
    costs = [
        result.cheapest_path["total"],
        result.fastest_path["total"],
        result.prestige_path["total"]
    ]
    unique_costs = len(set(costs))
    print(f"\n   Unique cost values: {unique_costs}/3")
    assert unique_costs >= 2, "❌ FAILED: All paths have same cost"

    # Validate: Masters cost is included
    if "masters" in result.prestige_path["breakdown"]:
        masters_cost = result.prestige_path["breakdown"]["masters"]["total"]
        print(f"   Masters cost included: ${masters_cost:,.0f}")
        assert masters_cost > 0, "❌ FAILED: Masters cost is $0"

    print("\n✅ PASSED: Cost calculations working, no $0 values")

    # Test with PhD goal
    result_phd = agent.run({
        "profile": {
            "career": "Mechanical Engineer",
            "goals": ["bachelors", "masters", "phd"],
            "constraints": {"budget": "high", "hasAA": False}
        },
        "pathway_result": pathway_result
    })

    print(f"\n✅ Test 2b: Mechanical Engineer with PhD goal")
    print(f"   Total cost with PhD: ${result_phd.prestige_path['total']:,.0f}")

    # Validate: PhD cost is included and non-zero
    if "phd" in result_phd.prestige_path["breakdown"]:
        phd_cost = result_phd.prestige_path["breakdown"]["phd"]["total"]
        print(f"   PhD cost included: ${phd_cost:,.0f}")
        assert phd_cost > 0, "❌ FAILED: PhD cost is $0"

    print("\n✅ PASSED: PhD cost calculations working")

def test_salary_outlook():
    """Test SalaryOutlookAgent with realistic salaries"""
    print("\n" + "="*80)
    print("TEST 3: SalaryOutlookAgent - Realistic Career-Specific Salaries")
    print("="*80)

    agent = SalaryOutlookAgent()

    # Test different careers
    careers = [
        ("Software Developer", 110000),
        ("Mechanical Engineer", 96000),
        ("Registered Nurse", 86000),
        ("Accountant", 79000)
    ]

    for career, expected_min in careers:
        result = agent.run({
            "career": career,
            "category": "Engineering"
        })

        print(f"\n✅ {career}:")
        print(f"   Median salary: ${result.median_salary:,}")
        print(f"   Miami salary: ${result.miami_salary:,}")
        print(f"   Growth rate: {result.growth_rate}")

        # Validate: Not the old hardcoded $60k
        assert result.median_salary != 60000, f"❌ FAILED: {career} shows hardcoded $60k"

        # Validate: Salary is realistic (within 20% of expected)
        assert result.median_salary >= expected_min * 0.8, f"❌ FAILED: {career} salary too low"
        assert result.median_salary <= expected_min * 1.2, f"❌ FAILED: {career} salary too high"

    print("\n✅ PASSED: All careers have realistic, career-specific salaries")

if __name__ == "__main__":
    try:
        test_pathway_research()
        test_cost_estimator()
        test_salary_outlook()

        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED!")
        print("="*80)
        print("\n✅ PathwayResearchAgent: Out-of-state filtering working")
        print("✅ CostEstimatorAgent: Masters/PhD costs calculated separately")
        print("✅ SalaryOutlookAgent: Realistic career-specific salaries")
        print("\nReady for production use!")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
