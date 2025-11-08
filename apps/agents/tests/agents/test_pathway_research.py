"""
Engineering-focused tests for PathwayResearchAgent
Tests mechanical, electrical, software engineer pathways
"""
import pytest
from agents.pathway_research import PathwayResearchAgent


class TestEngineeringPathways:
    """Test engineering career pathways"""

    def setup_method(self):
        """Initialize agent before each test"""
        self.agent = PathwayResearchAgent()

    def test_mechanical_engineer_pathway(self):
        """
        Verify ME pathway includes:
        - MDC AS.EGR program
        - ABET-accredited transfer options (FIU/FAU)
        - FE Exam requirement
        - PE License requirement
        """
        profile = {
            "career": "Mechanical Engineer",
            "category": "STEM-Engineering",
            "constraints": {"location": "miami"}
        }

        result = self.agent.run(profile)

        # Check MDC program
        assert len(result.mdc_programs) > 0, "Should have at least one MDC program"
        mdc_codes = [p.code for p in result.mdc_programs]
        assert any("EGR" in code for code in mdc_codes), "Should include Engineering AS (AS.EGR)"

        # Check transfer options
        assert len(result.transfer_options) > 0, "Should have transfer universities"
        universities = [t.university for t in result.transfer_options]
        assert any(u.upper() in ["FIU", "FAU", "UCF"] for u in universities), \
            "Should include Florida public universities"

        # Check ABET accreditation
        abet_programs = [t for t in result.transfer_options if t.abet_accredited]
        assert len(abet_programs) > 0, "Engineering programs must be ABET-accredited"

        # Check FE exam requirement
        fe_exams = [c for c in result.certifications if "FE" in c.name and c.required]
        assert len(fe_exams) > 0, "Mechanical Engineer requires FE Exam"

        # Check PE license requirement
        pe_licenses = [l for l in result.licenses if "PE" in l.name and l.required]
        assert len(pe_licenses) > 0, "Mechanical Engineer requires PE License"
        assert pe_licenses[0].state == "Florida"

    def test_electrical_engineer_pathway(self):
        """
        Verify EE pathway includes:
        - Same MDC engineering program (AS.EGR)
        - ABET-accredited EE programs
        - FE Exam and PE License
        """
        profile = {
            "career": "Electrical Engineer",
            "category": "STEM-Engineering",
            "constraints": {"location": "florida"}
        }

        result = self.agent.run(profile)

        # EE uses same MDC engineering AS
        assert len(result.mdc_programs) > 0
        mdc_codes = [p.code for p in result.mdc_programs]
        assert any("EGR" in code for code in mdc_codes)

        # Check for EE programs at universities
        programs = [t.program for t in result.transfer_options]
        assert any("Electrical" in p for p in programs), \
            "Should include Electrical Engineering programs"

        # ABET accreditation
        assert any(t.abet_accredited for t in result.transfer_options), \
            "EE programs must be ABET-accredited"

        # FE and PE requirements (same as ME)
        assert any("FE" in c.name for c in result.certifications), "EE requires FE Exam"
        assert any("PE" in l.name for l in result.licenses), "EE requires PE License"

    def test_civil_engineer_pathway(self):
        """Verify Civil Engineer has same requirements as ME/EE"""
        profile = {
            "career": "Civil Engineer",
            "category": "STEM-Engineering"
        }

        result = self.agent.run(profile)

        # Same pattern as ME/EE
        assert len(result.mdc_programs) > 0
        assert len(result.transfer_options) > 0
        assert any(t.abet_accredited for t in result.transfer_options)
        assert any(c.required for c in result.certifications)  # FE Exam
        assert any(l.required for l in result.licenses)  # PE License


class TestSoftwarePathways:
    """Test software/technology career pathways"""

    def setup_method(self):
        self.agent = PathwayResearchAgent()

    def test_software_developer_pathway(self):
        """
        Verify Software Developer pathway:
        - MDC Computer Science AS
        - Transfer to FIU/FAU CS programs
        - NO required professional license
        - Optional certifications (AWS, Azure, etc.)
        """
        profile = {
            "career": "Software Developer",
            "category": "STEM-Technology",
            "constraints": {"location": "miami"}
        }

        result = self.agent.run(profile)

        # Check MDC CS program
        assert len(result.mdc_programs) > 0
        mdc_codes = [p.code for p in result.mdc_programs]
        assert any("CS" in code or "Computer Science" in p.name
                   for code, p in zip(mdc_codes, result.mdc_programs)), \
            "Should include Computer Science AS"

        # Check transfer options
        assert len(result.transfer_options) > 0
        programs = [t.program for t in result.transfer_options]
        assert any("Computer Science" in p or "CS" in p for p in programs)

        # CRITICAL: Software development does NOT require professional license
        required_licenses = [l for l in result.licenses if l.required]
        assert len(required_licenses) == 0, \
            "Software Developer should NOT have required licenses (PE, RN, etc.)"

        # May have optional certifications
        # (This is OK to be empty or have optional certs)
        optional_certs = [c for c in result.certifications if not c.required]
        # No assertion - optional is fine

    def test_software_engineer_same_as_developer(self):
        """Verify 'Software Engineer' treated same as 'Software Developer'"""
        profile = {
            "career": "Software Engineer",
            "category": "STEM-Technology"
        }

        result = self.agent.run(profile)

        # Should have CS program
        assert len(result.mdc_programs) > 0

        # No required license
        assert all(not l.required for l in result.licenses)


class TestHealthcarePathways:
    """Test healthcare career pathways"""

    def setup_method(self):
        self.agent = PathwayResearchAgent()

    def test_registered_nurse_pathway(self):
        """
        Verify RN pathway:
        - MDC Nursing ADN (AS.NUR)
        - RN-to-BSN transfer option
        - NCLEX-RN license requirement
        """
        profile = {
            "career": "Registered Nurse",
            "category": "Healthcare",
            "constraints": {"location": "miami"}
        }

        result = self.agent.run(profile)

        # Check MDC nursing program
        assert len(result.mdc_programs) > 0
        nursing_programs = [p for p in result.mdc_programs if "NUR" in p.code or "Nursing" in p.name]
        assert len(nursing_programs) > 0, "Should have MDC Nursing ADN"

        # Check RN-to-BSN transfer
        assert len(result.transfer_options) > 0
        programs = [t.program for t in result.transfer_options]
        assert any("RN" in p or "BSN" in p or "Nursing" in p for p in programs)

        # Check NCLEX-RN license
        nclex = [l for l in result.licenses if "NCLEX" in l.name and l.required]
        assert len(nclex) > 0, "RN requires NCLEX-RN licensure exam"
        assert nclex[0].state == "Florida"


class TestArchitecturePathways:
    """Test architecture career pathways"""

    def setup_method(self):
        self.agent = PathwayResearchAgent()

    def test_architect_pathway(self):
        """
        Verify Architect pathway:
        - NAAB-accredited programs
        - NCARB certification
        - ARE exams
        """
        profile = {
            "career": "Architect",
            "category": "STEM-Architecture"
        }

        result = self.agent.run(profile)

        # Architecture requires specific licensing
        assert len(result.licenses) > 0, "Architect requires professional license"

        # Should mention ARE exams or Architect license
        license_names = [l.name for l in result.licenses]
        assert any("ARE" in name or "Architect" in name for name in license_names), \
            "Should include Architectural Registration Exam (ARE)"


# Performance test
@pytest.mark.slow
def test_pathway_research_completes_quickly():
    """Verify pathway research completes in reasonable time"""
    import time

    agent = PathwayResearchAgent()
    profile = {
        "career": "Mechanical Engineer",
        "category": "STEM-Engineering"
    }

    start = time.time()
    result = agent.run(profile)
    duration = time.time() - start

    assert duration < 15.0, f"Pathway research took too long: {duration:.2f}s"
    assert len(result.mdc_programs) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
