"""
PathwayResearchAgent - Researches MDC programs, transfers, and licensing
"""
import json
from typing import Dict, Any
from pathlib import Path
from .base import BaseAgent
from schemas.roadmap_output import PathwayResult, MDCProgram, TransferOption, Certification, License, Citation
from tools.search import search_mdc_programs, search_transfer_agreements, search_licensing_requirements
from datetime import datetime


class PathwayResearchAgent(BaseAgent):
    """Researches educational pathways and licensing requirements"""

    def __init__(self):
        prompt_file = Path(__file__).parent.parent / "prompts" / "pathway_research.txt"
        super().__init__(
            model_name="gemini-2.0-flash-exp",
            temperature=0.2,
            system_prompt_file=str(prompt_file)
        )

    def run(self, input_data: Dict[str, Any]) -> PathwayResult:
        """
        Research pathways for a career

        Args:
            input_data: Profile data from IntakeProfilerAgent

        Returns:
            PathwayResult with MDC programs, transfers, certs, licenses
        """
        career = input_data.get("career", "")
        category = input_data.get("category", "")
        location = input_data.get("constraints", {}).get("location", "miami")

        print(f"[PathwayResearch] Researching pathways for {career} ({category}), location: {location}")

        # Try seed data first for guaranteed results
        seed_data = self._load_seed_data(career)
        if seed_data:
            print(f"[PathwayResearch] Using seed data for guaranteed pathway")
            return self._get_fallback_pathway(career, category, location)

        # Use search tools (with fallback to seed data if APIs fail)
        try:
            mdc_results = search_mdc_programs(career)
            print(f"[PathwayResearch] Found {len(mdc_results)} MDC results")
            if len(mdc_results) == 0:
                print(f"[PathwayResearch] No search results, using fallback")
                return self._get_fallback_pathway(career, category)
        except Exception as e:
            print(f"[PathwayResearch] Search failed: {e}, using fallback")
            return self._get_fallback_pathway(career, category)

        # Build prompt for Gemini to analyze search results
        prompt = f"""
Analyze search results and create a structured pathway for this career.

Career: {career}
Category: {category}
Location: {location}

Search Results:
```json
{json.dumps(mdc_results[:5], indent=2)}
```

Based on your knowledge and these results, identify:
1. MDC program (AS.EGR, AS.NUR, AS.CS, etc.)
2. Transfer universities (FIU, FAU, etc.) with articulation agreements
3. Certifications (FE Exam, etc.)
4. Licenses (PE, NCLEX-RN, etc.)

Return ONLY a JSON object with the structure defined in your system prompt.
For engineering: Include ABET accreditation, FE exam, PE license.
For nursing: Include NCLEX-RN license.
For software: No required license.
"""

        # Generate response
        response = self.generate(prompt)

        # Parse JSON
        try:
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()

            data = json.loads(response)

            # Convert to Pydantic models
            return PathwayResult(
                mdc_programs=[MDCProgram(**p) for p in data.get("mdc_programs", [])],
                transfer_options=[TransferOption(**t) for t in data.get("transfer_options", [])],
                certifications=[Certification(**c) for c in data.get("certifications", [])],
                licenses=[License(**l) for l in data.get("licenses", [])],
                citations=[
                    Citation(
                        id=str(i),
                        title=c.get("title", ""),
                        url=c.get("url", ""),
                        accessed_at=datetime.now().isoformat()
                    )
                    for i, c in enumerate(data.get("citations", []))
                ]
            )

        except json.JSONDecodeError as e:
            print(f"[PathwayResearch] JSON parse failed: {e}")
            print(f"Response: {response}")

            # Return fallback pathway
            return self._get_fallback_pathway(career, category, "anywhere")

    def _load_seed_data(self, career: str) -> Dict[str, Any]:
        """Load pathway data from seed file"""
        seed_file = Path(__file__).parent.parent.parent.parent / "data" / "seed" / "career_pathways.json"
        try:
            with open(seed_file, 'r') as f:
                all_pathways = json.load(f)
                return all_pathways.get(career, {})
        except Exception as e:
            print(f"[PathwayResearch] Failed to load seed data: {e}")
            return {}

    def _load_ranking_data(self) -> Dict[str, Any]:
        """Load university ranking data"""
        ranking_file = Path(__file__).parent.parent.parent.parent / "data" / "seed" / "university_rankings.json"
        try:
            with open(ranking_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[PathwayResearch] Failed to load ranking data: {e}")
            return {}

    def _get_ranking_score(self, university_name: str, ranking_data: Dict[str, Any]) -> int:
        """Get ranking score for a university (higher is better)"""
        # Try exact match first
        if university_name in ranking_data:
            tier = ranking_data[university_name].get("tier", 3)
            national_rank = ranking_data[university_name].get("national_rank", 200)
            # Score: tier weight (100 points per tier) + inverse of ranking
            return (4 - tier) * 100 + (300 - national_rank)

        # Try fuzzy matching
        uni_upper = university_name.upper()
        for key in ranking_data.keys():
            if key.upper() in uni_upper or uni_upper in key.upper():
                tier = ranking_data[key].get("tier", 3)
                national_rank = ranking_data[key].get("national_rank", 200)
                return (4 - tier) * 100 + (300 - national_rank)

        # Default score for unranked universities
        return 50

    def _get_fallback_pathway(self, career: str, category: str, location: str = "miami") -> PathwayResult:
        """Fallback pathway using seed data or category-based defaults"""
        # Try loading from seed data first
        seed_data = self._load_seed_data(career)

        if seed_data:
            print(f"[PathwayResearch] Using seed data for {career}, location filter: {location}")

            # Load ranking data for sorting
            ranking_data = self._load_ranking_data()

            # Filter and rank transfer partners based on location preference
            all_partners = seed_data.get("transfer_partners", [])

            # Remove duplicates by university name (improved normalization)
            seen_universities = set()
            unique_partners = []
            for t in all_partners:
                uni_name = t.get("name", "").upper()
                # Normalize: remove parentheses, "UNIVERSITY", "THE", extra spaces, commas
                uni_key = (uni_name
                    .replace("(", "").replace(")", "")
                    .replace("UNIVERSITY", "").replace("THE ", "")
                    .replace(",", "").replace("  ", " ")
                    .strip())

                # Skip if already seen
                if uni_key not in seen_universities:
                    seen_universities.add(uni_key)
                    unique_partners.append(t)

            print(f"[PathwayResearch] Deduplicated: {len(all_partners)} → {len(unique_partners)} unique universities")

            # Add ranking score to each partner for sorting
            for partner in unique_partners:
                uni_name = partner.get("name", "")
                partner["_ranking_score"] = self._get_ranking_score(uni_name, ranking_data)

            # Location-based filtering with proper out-of-state support
            if location == "anywhere":
                # Prioritize out-of-state elite schools by ranking
                out_of_state = [t for t in unique_partners if t.get("in_state") == False]
                in_state = [t for t in unique_partners if t.get("in_state") != False]

                # Sort by ranking score (highest first)
                out_of_state.sort(key=lambda x: x.get("_ranking_score", 0), reverse=True)
                in_state.sort(key=lambda x: x.get("_ranking_score", 0), reverse=True)

                # Take top 3 out-of-state + top 2 in-state (5 total)
                transfer_partners = out_of_state[:3] + in_state[:2]
                print(f"[PathwayResearch] Location=anywhere: {len(out_of_state)} out-of-state, {len(in_state)} in-state → {len(transfer_partners)} selected")

            elif location == "florida":
                # Only Florida schools, sorted by ranking
                florida_schools = [t for t in unique_partners if t.get("in_state") != False]
                florida_schools.sort(key=lambda x: x.get("_ranking_score", 0), reverse=True)
                transfer_partners = florida_schools[:5]
                print(f"[PathwayResearch] Location=florida: {len(florida_schools)} FL schools → {len(transfer_partners)} selected")

            else:  # miami or default
                # Prioritize Miami-area schools, then other FL schools
                miami_schools = [t for t in unique_partners if "Miami" in t.get("location", "") or "Coral Gables" in t.get("location", "")]
                other_fl = [t for t in unique_partners if t.get("in_state") != False and "Miami" not in t.get("location", "") and "Coral Gables" not in t.get("location", "")]

                miami_schools.sort(key=lambda x: x.get("_ranking_score", 0), reverse=True)
                other_fl.sort(key=lambda x: x.get("_ranking_score", 0), reverse=True)

                transfer_partners = miami_schools[:3] + other_fl[:2]
                print(f"[PathwayResearch] Location=miami: {len(miami_schools)} Miami schools, {len(other_fl)} other FL → {len(transfer_partners)} selected")

            print(f"[PathwayResearch] Filtered to {len(transfer_partners)} unique transfer partners")

            return PathwayResult(
                mdc_programs=[
                    MDCProgram(
                        code="",
                        name=p["name"],
                        credits=60,
                        url=p["url"]
                    )
                    for p in seed_data.get("mdc_programs", [])
                ],
                transfer_options=[
                    TransferOption(
                        university=t["name"],
                        program=t["program"],
                        articulation="2+2 Transfer Agreement",
                        url=t["url"],
                        abet_accredited=("Engineer" in career)
                    )
                    for t in transfer_partners
                ],
                certifications=[
                    Certification(
                        name=c.get("cert", c.get("exam", "")),
                        required=True,
                        timing="After degree completion",
                        url=c["url"]
                    )
                    for c in seed_data.get("licensing", [])
                    if "cert" in c
                ],
                licenses=[
                    License(
                        name=l.get("exam", ""),
                        required=True,
                        timing="After degree completion",
                        state="Florida",
                        url=l["url"]
                    )
                    for l in seed_data.get("licensing", [])
                    if "exam" in l
                ],
                citations=[
                    Citation(
                        id="1",
                        title=f"MDC Pathways for {career}",
                        url="https://www.mdc.edu/",
                        accessed_at=datetime.now().isoformat()
                    )
                ]
            )

        # Fallback to category-based defaults
        if "engineer" in career.lower():
            return PathwayResult(
                mdc_programs=[
                    MDCProgram(
                        code="AS.EGR",
                        name="Engineering Associate in Science",
                        credits=60,
                        url="https://www.mdc.edu/engineering/"
                    )
                ],
                transfer_options=[
                    TransferOption(
                        university="FIU",
                        program=f"BS {career}",
                        articulation="2+2 Transfer Agreement",
                        url="https://cec.fiu.edu/",
                        abet_accredited=True
                    ),
                    TransferOption(
                        university="FAU",
                        program=f"BS {career}",
                        articulation="2+2 Transfer Agreement",
                        url="https://www.fau.edu/engineering/",
                        abet_accredited=True
                    )
                ],
                certifications=[
                    Certification(
                        name="FE Exam (Fundamentals of Engineering)",
                        required=True,
                        timing="During senior year or after graduation",
                        url="https://ncees.org/engineering/fe/"
                    )
                ],
                licenses=[
                    License(
                        name="PE License (Professional Engineer)",
                        required=True,
                        timing="After 4 years of work experience + PE exam",
                        state="Florida",
                        url="https://fbpe.org/"
                    )
                ],
                citations=[
                    Citation(
                        id="1",
                        title="MDC Engineering Programs",
                        url="https://www.mdc.edu/engineering/",
                        accessed_at=datetime.now().isoformat()
                    )
                ]
            )

        elif "software" in career.lower() or "developer" in career.lower():
            return PathwayResult(
                mdc_programs=[
                    MDCProgram(
                        code="AS.CS",
                        name="Computer Science Associate in Science",
                        credits=60,
                        url="https://www.mdc.edu/stem/"
                    )
                ],
                transfer_options=[
                    TransferOption(
                        university="FIU",
                        program="BS Computer Science",
                        articulation="2+2 Transfer Agreement",
                        url="https://www.cis.fiu.edu/",
                        abet_accredited=True
                    )
                ],
                certifications=[],
                licenses=[],
                citations=[]
            )

        elif "nurse" in career.lower():
            return PathwayResult(
                mdc_programs=[
                    MDCProgram(
                        code="AS.NUR",
                        name="Nursing Associate in Science (ADN)",
                        credits=72,
                        url="https://www.mdc.edu/nursing/"
                    )
                ],
                transfer_options=[
                    TransferOption(
                        university="FIU",
                        program="RN-to-BSN",
                        articulation="Seamless transfer",
                        url="https://cnhs.fiu.edu/",
                        abet_accredited=None
                    )
                ],
                certifications=[],
                licenses=[
                    License(
                        name="NCLEX-RN",
                        required=True,
                        timing="After ADN graduation",
                        state="Florida",
                        url="https://floridasnursing.gov/"
                    )
                ],
                citations=[]
            )

        else:
            # Generic fallback
            return PathwayResult(
                mdc_programs=[],
                transfer_options=[],
                certifications=[],
                licenses=[],
                citations=[]
            )
