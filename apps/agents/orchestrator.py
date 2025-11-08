"""
OrchestratorAgent - Coordinates all agents to generate complete roadmap
"""
import json
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path as FilePath
from agents.intake_profiler import IntakeProfilerAgent
from agents.pathway_research import PathwayResearchAgent
from agents.cost_estimator import CostEstimatorAgent
from agents.salary_outlook import SalaryOutlookAgent
from schemas.quiz_input import QuizInput
from schemas.roadmap_output import Roadmap, Path, Node, Edge, Citation, Step


class OrchestratorAgent:
    """Coordinates all agents to produce complete roadmap"""

    def __init__(self):
        self.intake_profiler = IntakeProfilerAgent()
        self.pathway_researcher = PathwayResearchAgent()
        self.cost_estimator = CostEstimatorAgent()
        self.salary_outlooker = SalaryOutlookAgent()

        # Load seed data for enhancements
        self._load_seed_data()

    def _load_seed_data(self):
        """Load enhancement seed data files"""
        seed_dir = FilePath(__file__).parent.parent.parent.parent / "data" / "seed"

        # Load housing costs
        try:
            with open(seed_dir / "housing_costs.json", 'r') as f:
                self.housing_data = json.load(f)
        except:
            self.housing_data = {}

        # Load internships and research opportunities
        try:
            with open(seed_dir / "internships_research.json", 'r') as f:
                self.internship_data = json.load(f)
        except:
            self.internship_data = {}

        # Load university rankings
        try:
            with open(seed_dir / "university_rankings.json", 'r') as f:
                self.ranking_data = json.load(f)
        except:
            self.ranking_data = {}

    def generate_roadmap(self, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete roadmap from quiz data

        Args:
            quiz_data: User quiz responses

        Returns:
            Complete Roadmap with paths, nodes, edges, citations

        Flow:
            1. IntakeProfilerAgent → Profile
            2. PathwayResearchAgent → MDC programs, transfers, licenses
            3. CostEstimatorAgent → Cost breakdowns for 3 paths
            4. SalaryOutlookAgent → Salary, ROI
            5. Synthesize → Complete roadmap
        """
        print(f"[Orchestrator] Starting roadmap generation for: {quiz_data.get('career')}")

        # Step 1: Profile analysis
        print("[Orchestrator] Step 1: Profiling student...")
        profile = self.intake_profiler.run(quiz_data)
        print(f"[Orchestrator] Profile: {profile.category} | Flags: {profile.flags}")

        # Step 2: Pathway research
        print("[Orchestrator] Step 2: Researching pathways...")
        pathway_result = self.pathway_researcher.run(profile.model_dump())
        print(f"[Orchestrator] Found {len(pathway_result.mdc_programs)} MDC programs, "
              f"{len(pathway_result.transfer_options)} transfer options")

        # Step 3: Cost estimation
        print("[Orchestrator] Step 3: Estimating costs...")
        cost_result = self.cost_estimator.run({
            "profile": profile.model_dump(),
            "pathway_result": pathway_result.model_dump()
        })
        print(f"[Orchestrator] Cheapest: ${cost_result.cheapest_path['total']:,.0f}, "
              f"Prestige: ${cost_result.prestige_path['total']:,.0f}")

        # Step 4: Salary outlook
        print("[Orchestrator] Step 4: Analyzing salary outlook...")
        salary_result = self.salary_outlooker.run({
            "career": profile.career,
            "category": profile.category
        })
        print(f"[Orchestrator] Median salary: ${salary_result.median_salary:,.0f}, "
              f"ROI: {salary_result.roi_years:.1f} years")

        # Step 5: AI-Driven Path Selection via Gemini
        print("[Orchestrator] Step 5: Asking Gemini to recommend optimal paths...")
        optimal_paths = self._get_gemini_path_recommendations(
            profile, pathway_result, cost_result, salary_result, quiz_data
        )
        print(f"[Orchestrator] Gemini recommended: Cheapest={optimal_paths['cheapest']['university']}, "
              f"Fastest={optimal_paths['fastest']['university']}, Prestige={optimal_paths['prestige']['university']}")

        # Step 6: Synthesize roadmap with AI recommendations
        print("[Orchestrator] Step 6: Synthesizing roadmap with AI choices...")
        roadmap = self._synthesize_roadmap(
            profile, pathway_result, cost_result, salary_result, quiz_data, optimal_paths
        )

        print(f"[Orchestrator] ✓ Roadmap complete: {len(roadmap['nodes'])} nodes, "
              f"{len(roadmap['edges'])} edges")

        return roadmap

    def _get_gemini_path_recommendations(
        self,
        profile,
        pathway_result,
        cost_result,
        salary_result,
        quiz_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use Gemini to intelligently choose optimal paths based on all collected data"""
        import google.generativeai as genai
        import os

        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")

        # Prepare comprehensive data for Gemini
        location_pref = quiz_data.get("location", "miami")
        goals = quiz_data.get("goals", [])
        budget = quiz_data.get("budget", "medium")

        # Build meta-prompt
        meta_prompt = f"""Given the student inputs below and the research results from all agents, recommend the optimal academic roadmap for:
- Cheapest path
- Fastest path
- Most Prestigious path

STUDENT PROFILE:
- Career Goal: {profile.career}
- Category: {profile.category}
- Location Preference: {location_pref}
- Budget Priority: {budget}
- Goals: {', '.join(goals)}
- GPA: {quiz_data.get('gpa', 3.0)}

AVAILABLE UNIVERSITIES:
{self._format_universities_for_gemini(pathway_result, location_pref)}

COST DATA (for reference):
- Cheapest Path Total: ${cost_result.cheapest_path['total']:,.0f}
- Prestige Path Total: ${cost_result.prestige_path['total']:,.0f}

SALARY DATA:
- Expected Median Salary: ${salary_result.median_salary:,.0f}
- ROI Years: {salary_result.roi_years}

RULES:
1. Consider tuition + housing + fees per city
2. A Master's costs 1–2 years separately (calculated independently)
3. A PhD costs 4–6 years separately (calculated independently)
4. If location is "anywhere" or out-of-state, prefer out-of-state elite universities (MIT, Stanford, CMU, Berkeley, Georgia Tech)
5. If location is "florida" or "miami", prefer Florida universities (UF, FIU, FSU, UCF, FAU)
6. Use ranking_score and tier to rank university prestige (Tier 1 > Tier 2 > Tier 3)
7. Cheapest path: Minimize total cost (tuition + housing), prefer in-state, budget-friendly options
8. Fastest path: Minimize total years, may have higher cost if accelerated programs available
9. Prestige path: Maximize tier and ranking_score, accept higher cost for better outcomes
10. If Masters or PhD in goals, include them as SEPARATE steps with their own costs
11. CRITICAL: The three paths MUST recommend different universities. Do NOT recommend the same school for all 3 paths.

OUTPUT FORMAT (strict JSON):
{{
  "cheapest": {{
    "university": "Full University Name",
    "program": "Degree Name",
    "tier": 1-3,
    "ranking_score": 100-400,
    "estimated_bs_cost": total for 2 years BS including tuition + housing,
    "estimated_ms_cost": total for MS if in goals (0 if not),
    "estimated_phd_cost": total for PhD if in goals (0 if not),
    "total_years": 4-10,
    "reasoning": "Why this is the cheapest option"
  }},
  "fastest": {{
    "university": "Different University Name",
    "program": "Degree Name",
    "tier": 1-3,
    "ranking_score": 100-400,
    "estimated_bs_cost": total,
    "estimated_ms_cost": total if in goals,
    "estimated_phd_cost": total if in goals,
    "total_years": 3-8,
    "reasoning": "Why this is the fastest option"
  }},
  "prestige": {{
    "university": "Elite University Name (MIT/Stanford/CMU/Berkeley if out-of-state)",
    "program": "Degree Name",
    "tier": 1,
    "ranking_score": 350-400,
    "estimated_bs_cost": total,
    "estimated_ms_cost": total if in goals,
    "estimated_phd_cost": total if in goals,
    "total_years": 4-10,
    "reasoning": "Why this is the most prestigious option"
  }}
}}

Return ONLY the JSON, no additional text."""

        # Call Gemini
        try:
            print(f"[Orchestrator] Calling Gemini with {len(meta_prompt)} chars...")
            response = model.generate_content(meta_prompt)
            response_text = response.text.strip()

            # Log the full response for debugging
            print(f"[Orchestrator] Gemini response length: {len(response_text)} chars")

            # Parse JSON response
            import json
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()

            recommendations = json.loads(response_text)

            # Validate recommendations
            if not self._validate_gemini_recommendations(recommendations):
                print("[Orchestrator] ⚠️ Gemini recommendations failed validation, using fallback")
                return self._get_fallback_recommendations(pathway_result, location_pref)

            print(f"[Orchestrator] ✓ Gemini recommendations validated successfully")
            return recommendations

        except Exception as e:
            print(f"[Orchestrator] ❌ Gemini call failed: {e}")
            print(f"[Orchestrator] Using fallback recommendations")
            return self._get_fallback_recommendations(pathway_result, location_pref)

    def _format_universities_for_gemini(self, pathway_result, location_pref: str) -> str:
        """Format university options with all relevant data for Gemini"""
        universities = []

        for i, transfer in enumerate(pathway_result.transfer_options[:8]):  # Top 8 options
            ranking = self._get_university_ranking(transfer.university)
            location = ranking.get("location", "Unknown")

            # Get cost data
            tuition_in = ranking.get("tuition_in_state", 10000)
            tuition_out = ranking.get("tuition_out_of_state", 25000)

            # Get housing data
            housing = self.housing_data.get(location, {})
            yearly_housing = (housing.get("avg_rent_shared", 1000) * 12 +
                            housing.get("avg_food", 350) * 12 +
                            housing.get("avg_transport", 100) * 12)

            is_in_state = "FL" in location
            tuition = tuition_in if is_in_state else tuition_out

            uni_data = f"""
{i+1}. {transfer.university}
   - Program: {transfer.program}
   - Location: {location}
   - In-State: {"Yes" if is_in_state else "No"}
   - Tier: {ranking.get('tier', 3)}
   - Ranking Score: {self._calculate_ranking_score(ranking)}
   - Tuition (2 years): ${tuition * 2:,.0f}
   - Housing/Living (2 years): ${yearly_housing * 2:,.0f}
   - Total BS Cost: ${(tuition + yearly_housing) * 2:,.0f}
   - URL: {transfer.url}"""
            universities.append(uni_data)

        return "\n".join(universities)

    def _calculate_ranking_score(self, ranking: Dict[str, Any]) -> int:
        """Calculate ranking score (same formula as PathwayResearchAgent)"""
        tier = ranking.get("tier", 3)
        national_rank = ranking.get("national_rank", 200)
        return (4 - tier) * 100 + (300 - national_rank)

    def _validate_gemini_recommendations(self, recommendations: Dict[str, Any]) -> bool:
        """Validate Gemini recommendations meet quality standards"""
        try:
            # Check all three paths exist
            if not all(key in recommendations for key in ["cheapest", "fastest", "prestige"]):
                print("[Orchestrator] ❌ Validation failed: Missing path recommendations")
                return False

            # Check universities are different
            universities = [
                recommendations["cheapest"].get("university", ""),
                recommendations["fastest"].get("university", ""),
                recommendations["prestige"].get("university", "")
            ]

            if len(set(universities)) < 3:
                print(f"[Orchestrator] ❌ Validation failed: Duplicate universities: {universities}")
                return False

            # Check all paths have required fields
            for path_name, path in recommendations.items():
                required_fields = ["university", "program", "tier", "estimated_bs_cost"]
                if not all(field in path for field in required_fields):
                    print(f"[Orchestrator] ❌ Validation failed: {path_name} missing required fields")
                    return False

                # Check reasonable cost values
                if path["estimated_bs_cost"] <= 0 or path["estimated_bs_cost"] > 500000:
                    print(f"[Orchestrator] ❌ Validation failed: {path_name} has unrealistic BS cost")
                    return False

            return True

        except Exception as e:
            print(f"[Orchestrator] ❌ Validation error: {e}")
            return False

    def _get_fallback_recommendations(self, pathway_result, location_pref: str) -> Dict[str, Any]:
        """Fallback recommendations if Gemini fails - MUST use 3 different universities"""
        transfer_options = pathway_result.transfer_options

        # Sort by ranking
        ranked = []
        for transfer in transfer_options:
            ranking = self._get_university_ranking(transfer.university)
            score = self._calculate_ranking_score(ranking)
            location = ranking.get("location", "")
            is_fl = "FL" in location
            tuition_in = ranking.get("tuition_in_state", 10000)
            tuition_out = ranking.get("tuition_out_of_state", 25000)
            tuition = tuition_in if is_fl else tuition_out

            ranked.append({
                "transfer": transfer,
                "ranking": ranking,
                "score": score,
                "is_fl": is_fl,
                "tuition": tuition,
                "location": location
            })

        ranked.sort(key=lambda x: x["score"], reverse=True)

        # CRITICAL: Ensure 3 DIFFERENT universities

        # Cheapest: Lowest cost Florida in-state school
        fl_schools = [r for r in ranked if r["is_fl"]]
        fl_schools.sort(key=lambda x: x["tuition"])
        cheapest = fl_schools[0] if fl_schools else ranked[-1]

        # Prestige: Highest ranked school (prefer out-of-state elite)
        prestige = ranked[0]

        # Fastest: Mid-tier option that's DIFFERENT from cheapest and prestige
        # Try to find a different FL school for fastest, or second-best prestige
        fastest = None
        for r in ranked:
            uni_name = r["transfer"].university
            if uni_name != cheapest["transfer"].university and uni_name != prestige["transfer"].university:
                fastest = r
                break

        # If we still don't have a third unique school, force it
        if not fastest or len(set([cheapest["transfer"].university, fastest["transfer"].university, prestige["transfer"].university])) < 3:
            # Pick second FL school if cheapest is FL
            if cheapest["is_fl"] and len(fl_schools) >= 2:
                fastest = fl_schools[1]
            # Or pick second prestige if prestige is top
            elif len(ranked) >= 2:
                fastest = ranked[1]
            else:
                fastest = cheapest  # Last resort

        # Calculate realistic costs
        def calc_cost(r):
            housing_data = self.housing_data.get(r["location"], {})
            yearly_housing = (housing_data.get("avg_rent_shared", 1100) * 12 +
                            housing_data.get("avg_food", 350) * 12 +
                            housing_data.get("avg_transport", 100) * 12)
            return (r["tuition"] + yearly_housing) * 2  # 2 years BS

        return {
            "cheapest": {
                "university": cheapest["transfer"].university,
                "program": cheapest["transfer"].program,
                "tier": cheapest["ranking"].get("tier", 2),
                "ranking_score": cheapest["score"],
                "estimated_bs_cost": calc_cost(cheapest),
                "estimated_ms_cost": 0,
                "estimated_phd_cost": 0,
                "total_years": 4
            },
            "fastest": {
                "university": fastest["transfer"].university,
                "program": fastest["transfer"].program,
                "tier": fastest["ranking"].get("tier", 2),
                "ranking_score": fastest["score"],
                "estimated_bs_cost": calc_cost(fastest),
                "estimated_ms_cost": 0,
                "estimated_phd_cost": 0,
                "total_years": 3.5
            },
            "prestige": {
                "university": prestige["transfer"].university,
                "program": prestige["transfer"].program,
                "tier": prestige["ranking"].get("tier", 1),
                "ranking_score": prestige["score"],
                "estimated_bs_cost": calc_cost(prestige),
                "estimated_ms_cost": 0,
                "estimated_phd_cost": 0,
                "total_years": 4
            }
        }

    def _synthesize_roadmap(
        self,
        profile,
        pathway_result,
        cost_result,
        salary_result,
        quiz_data: Dict[str, Any],
        optimal_paths: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Synthesize all agent outputs into final roadmap structure

        Creates 3 paths (cheapest, fastest, prestige) with:
        - Steps (programs, certifications, licenses)
        - Nodes (for React Flow visualization)
        - Edges (connections/prerequisites)
        - Citations (source URLs)
        """
        # Extract user goals
        goals = quiz_data.get('goals', [])

        # Build paths
        cheapest_path = self._build_path(
            "cheapest",
            "Most Affordable Path",
            cost_result.cheapest_path,
            pathway_result,
            salary_result.roi_years,
            goals
        )

        fastest_path = self._build_path(
            "fastest",
            "Fastest Path",
            cost_result.fastest_path,
            pathway_result,
            salary_result.roi_years * 0.8,  # Faster path = faster ROI
            goals
        )

        prestige_path = self._build_path(
            "prestige",
            "Prestige Path",
            cost_result.prestige_path,
            pathway_result,
            salary_result.roi_years * 1.5,  # Higher cost = slower ROI
            goals
        )

        # Build nodes and edges for React Flow
        nodes, edges = self._build_graph(pathway_result, profile, goals)

        # Collect citations
        citations = pathway_result.citations

        return {
            "paths": {
                "cheapest": cheapest_path,
                "fastest": fastest_path,
                "prestige": prestige_path
            },
            "nodes": nodes,
            "edges": edges,
            "citations": [c.model_dump() for c in citations],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "confidence": 0.85,
                "career": profile.career,
                "category": profile.category,
                "salary_outlook": {
                    "median_salary": salary_result.median_salary,
                    "growth_rate": salary_result.growth_rate,
                    "job_outlook": salary_result.job_outlook
                }
            }
        }

    def _build_path(self, path_id: str, name: str, cost_data: Dict, pathway_result, roi: float, goals: List[str]) -> Dict:
        """Build a single path with steps including internships/research and grad school"""
        steps = []
        step_id = 0
        career = pathway_result.mdc_programs[0].name if pathway_result.mdc_programs else "General"

        # Add MDC program (if applicable)
        if pathway_result.mdc_programs and cost_data.get("breakdown", {}).get("mdc", 0) > 0:
            mdc_program = pathway_result.mdc_programs[0]
            steps.append({
                "id": f"step-{step_id}",
                "type": "program",
                "institution": "Miami Dade College",
                "duration": "2 years",
                "cost": cost_data["breakdown"].get("mdc", 0),
                "prerequisites": [],
                "description": f"{mdc_program.name} ({mdc_program.code})",
                "url": mdc_program.url
            })
            step_id += 1

        # Add internship/research if user selected those goals
        if "internship" in goals or "research" in goals:
            career_key = self._match_career_key(career)
            internship_info = self.internship_data.get(career_key, {})

            if "internship" in goals and internship_info.get("internships"):
                intern = internship_info["internships"][0]
                steps.append({
                    "id": f"step-{step_id}",
                    "type": "internship",
                    "institution": intern.get("name", "Industry Partner"),
                    "duration": "Summer (10-12 weeks)",
                    "cost": 0,  # Internships are paid
                    "prerequisites": [f"step-{step_id-1}"] if step_id > 0 else [],
                    "description": f"Internship: {intern.get('name', 'Industry Partner')}",
                    "url": intern.get("url", ""),
                    "location": intern.get("location", "")
                })
                step_id += 1

            if "research" in goals and internship_info.get("research"):
                research = internship_info["research"][0]
                steps.append({
                    "id": f"step-{step_id}",
                    "type": "research",
                    "institution": "Research University",
                    "duration": "10 weeks (Summer REU)",
                    "cost": 0,  # REUs provide stipends
                    "prerequisites": [f"step-{step_id-1}"] if step_id > 0 else [],
                    "description": f"Research: {research.get('name', 'Undergraduate Research')}",
                    "url": research.get("url", "")
                })
                step_id += 1

        # Add university program
        if pathway_result.transfer_options:
            university_cost = cost_data["breakdown"].get("university", 0)
            for transfer in pathway_result.transfer_options[:1]:  # Take first option
                steps.append({
                    "id": f"step-{step_id}",
                    "type": "program",
                    "institution": transfer.university,
                    "duration": "2 years",
                    "cost": university_cost,
                    "prerequisites": [f"step-{step_id-1}"] if step_id > 0 else [],
                    "description": transfer.program,
                    "url": transfer.url
                })
                step_id += 1
                break

        # Add certifications
        for cert in pathway_result.certifications:
            if cert.required:
                steps.append({
                    "id": f"step-{step_id}",
                    "type": "certification",
                    "institution": "Professional Board",
                    "duration": cert.timing,
                    "cost": 200,  # Typical exam fee
                    "prerequisites": [f"step-{step_id-1}"],
                    "description": cert.name
                })
                step_id += 1

        # Add licenses
        for license in pathway_result.licenses:
            if license.required:
                steps.append({
                    "id": f"step-{step_id}",
                    "type": "license",
                    "institution": f"{license.state} Board",
                    "duration": license.timing,
                    "cost": 300,  # Typical license fee
                    "prerequisites": [f"step-{step_id-1}"],
                    "description": license.name,
                    "url": license.url or ""
                })
                step_id += 1

        # Add Masters program if user selected it
        if "masters" in goals and pathway_result.transfer_options:
            university = pathway_result.transfer_options[0].university
            degree_name = self._get_degree_name(career)
            ms_cost = self._calculate_graduate_cost(university, "masters", 2)
            steps.append({
                "id": f"step-{step_id}",
                "type": "masters",
                "institution": university,
                "duration": "2 years",
                "cost": ms_cost,
                "prerequisites": [f"step-{step_id-1}"] if step_id > 0 else [],
                "description": f"MS in {degree_name}",
                "url": ""
            })
            step_id += 1

        # Add PhD program if user selected it
        if "phd" in goals and pathway_result.transfer_options:
            university = pathway_result.transfer_options[0].university
            degree_name = self._get_degree_name(career)
            phd_cost = self._calculate_graduate_cost(university, "phd", 5)  # Average 5 years
            steps.append({
                "id": f"step-{step_id}",
                "type": "phd",
                "institution": university,
                "duration": "4-6 years",
                "cost": phd_cost,
                "prerequisites": [f"step-{step_id-1}"] if step_id > 0 else [],
                "description": f"PhD in {degree_name} - Research & Dissertation",
                "url": ""
            })
            step_id += 1

        # Calculate accurate total from all steps
        calculated_total = sum(step.get("cost", 0) for step in steps)

        # Use calculated total if it's significantly different from CostEstimator total
        # (This handles cases where orchestrator adds MS/PhD that CostEstimator didn't include)
        final_total = calculated_total if calculated_total > cost_data["total"] * 1.1 else cost_data["total"]

        # Calculate total duration
        total_years = 0
        for step in steps:
            duration_str = step.get("duration", "0 years")
            if "year" in duration_str:
                try:
                    years = float(duration_str.split()[0].split("-")[0])
                    total_years += years
                except:
                    pass

        return {
            "id": path_id,
            "name": name,
            "total_cost": final_total,
            "duration": f"{total_years:.1f} years" if total_years > 0 else "4 years",
            "steps": steps,
            "roi": roi
        }

    def _build_graph(self, pathway_result, profile, goals: List[str]) -> tuple:
        """Build nodes and edges for React Flow visualization with rankings and enhanced types"""
        nodes = []
        edges = []
        node_id = 0
        y_pos = 0

        # MDC node
        if pathway_result.mdc_programs:
            mdc = pathway_result.mdc_programs[0]
            nodes.append({
                "id": f"node-{node_id}",
                "type": "mdc",
                "data": {
                    "label": f"MDC: {mdc.name}",
                    "cost": 6800,
                    "duration": "2 years",
                    "url": mdc.url,
                    "tier": "AA"
                },
                "position": {"x": 250, "y": y_pos}
            })
            prev_node = f"node-{node_id}"
            node_id += 1
            y_pos += 150

        # University nodes with ranking data
        last_university_node = None
        for i, transfer in enumerate(pathway_result.transfer_options[:3]):
            ranking = self._get_university_ranking(transfer.university)
            nodes.append({
                "id": f"node-{node_id}",
                "type": "university",
                "data": {
                    "label": f"{transfer.university}: {transfer.program}",
                    "cost": 13000,
                    "duration": "2 years",
                    "url": transfer.url,
                    "tier": f"Tier {ranking.get('tier', 3)}",
                    "ranking_label": ranking.get('ranking_label', ''),
                    "degree": "BS"
                },
                "position": {"x": 250 + i * 300, "y": y_pos}
            })

            # Edge from MDC to university
            if pathway_result.mdc_programs and i == 0:
                edges.append({
                    "id": f"edge-{len(edges)}",
                    "source": prev_node,
                    "target": f"node-{node_id}",
                    "label": transfer.articulation
                })
                last_university_node = f"node-{node_id}"

            node_id += 1

        y_pos += 150

        # Certification/License nodes
        for cert in pathway_result.certifications:
            if cert.required:
                nodes.append({
                    "id": f"node-{node_id}",
                    "type": "cert",
                    "data": {
                        "label": cert.name,
                        "cost": 200,
                        "duration": cert.timing,
                        "url": cert.url or ""
                    },
                    "position": {"x": 250, "y": y_pos}
                })
                node_id += 1
                y_pos += 100

        for license in pathway_result.licenses:
            if license.required:
                nodes.append({
                    "id": f"node-{node_id}",
                    "type": "license",
                    "data": {
                        "label": f"{license.name} ({license.state})",
                        "cost": 300,
                        "duration": license.timing,
                        "url": license.url or ""
                    },
                    "position": {"x": 250, "y": y_pos}
                })
                license_node = f"node-{node_id}"
                node_id += 1
                y_pos += 100

        # Add Masters node if in goals
        masters_node = None
        if "masters" in goals and pathway_result.transfer_options:
            university = pathway_result.transfer_options[0].university
            career = profile.career if hasattr(profile, 'career') else "Engineering"
            degree_name = self._get_degree_name(career)
            ms_cost = self._calculate_graduate_cost(university, "masters", 2)

            nodes.append({
                "id": f"node-{node_id}",
                "type": "masters",
                "data": {
                    "label": f"MS {degree_name}",
                    "institution": university,
                    "cost": ms_cost,
                    "duration": "2 years",
                    "url": "",
                    "degree": "MS"
                },
                "position": {"x": 250, "y": y_pos}
            })

            # Edge from BS to MS (use last_university_node or fallback)
            if last_university_node:
                edges.append({
                    "id": f"edge-{len(edges)}",
                    "source": last_university_node,
                    "target": f"node-{node_id}",
                    "label": "Graduate School"
                })

            masters_node = f"node-{node_id}"
            node_id += 1
            y_pos += 150

        # Add PhD node if in goals
        if "phd" in goals and pathway_result.transfer_options:
            university = pathway_result.transfer_options[0].university
            career = profile.career if hasattr(profile, 'career') else "Engineering"
            degree_name = self._get_degree_name(career)
            phd_cost = self._calculate_graduate_cost(university, "phd", 5)

            nodes.append({
                "id": f"node-{node_id}",
                "type": "phd",
                "data": {
                    "label": f"PhD in {degree_name}",
                    "institution": university,
                    "cost": phd_cost,
                    "duration": "4-6 years",
                    "url": "",
                    "degree": "PhD"
                },
                "position": {"x": 250, "y": y_pos}
            })

            # Edge from MS to PhD (or BS if no MS)
            source_node = masters_node if masters_node else last_university_node
            if source_node:
                edges.append({
                    "id": f"edge-{len(edges)}",
                    "source": source_node,
                    "target": f"node-{node_id}",
                    "label": "Doctoral Research"
                })

            node_id += 1
            y_pos += 150

        return nodes, edges

    def _get_degree_name(self, career: str) -> str:
        """Convert career name to proper degree name"""
        career_lower = career.lower()
        if "software" in career_lower or "developer" in career_lower or "computer" in career_lower or "programmer" in career_lower:
            return "Computer Science"
        elif "mechanical" in career_lower:
            return "Mechanical Engineering"
        elif "electrical" in career_lower or "electronics" in career_lower:
            return "Electrical Engineering"
        elif "civil" in career_lower:
            return "Civil Engineering"
        elif "business" in career_lower or "finance" in career_lower or "account" in career_lower:
            return "Business Administration"
        elif "nurs" in career_lower:
            return "Nursing"
        elif "data" in career_lower and "scien" in career_lower:
            return "Data Science"
        else:
            return career  # Default to career name

    def _match_career_key(self, career: str) -> str:
        """Match career name to seed data key"""
        career_lower = career.lower()
        if "mechanical" in career_lower or "mae" in career_lower:
            return "Mechanical Engineer"
        elif "electrical" in career_lower or "eee" in career_lower:
            return "Electrical Engineer"
        elif "civil" in career_lower:
            return "Civil Engineer"
        elif "software" in career_lower or "computer science" in career_lower:
            return "Software Developer"
        elif "nurs" in career_lower:
            return "Registered Nurse"
        elif "architect" in career_lower:
            return "Architect"
        elif "account" in career_lower:
            return "Accountant"
        elif "data" in career_lower:
            return "Data Scientist"
        else:
            return career

    def _get_university_ranking(self, university: str) -> Dict[str, Any]:
        """Get ranking data for a university"""
        # Try exact match first
        if university in self.ranking_data:
            return self.ranking_data[university]

        # Try abbreviated match
        for abbrev in ["UF", "UM", "FSU", "UCF", "FAU", "FIU", "USF"]:
            if abbrev in university:
                return self.ranking_data.get(abbrev, {"tier": 3, "ranking_label": "Regional University"})

        return {"tier": 3, "ranking_label": "Regional University"}

    def _calculate_graduate_cost(self, university: str, degree_type: str, years: float) -> float:
        """Calculate cost for Masters or PhD including tuition, housing, food, transport"""
        # Get university ranking data for tuition
        ranking = self._get_university_ranking(university)
        location = ranking.get("location", "Miami, FL")

        # Determine if in-state or out-of-state
        is_in_state = "FL" in location
        undergrad_tuition = ranking.get("tuition_in_state" if is_in_state else "tuition_out_of_state", 10000)

        # Graduate tuition (typically 20% higher than undergrad)
        grad_tuition_per_year = undergrad_tuition * 1.2

        # Get housing costs
        housing = self.housing_data.get(location, {})
        yearly_rent = housing.get("avg_rent_shared", 1100) * 12
        yearly_food = housing.get("avg_food", 350) * 12
        yearly_transport = housing.get("avg_transport", 110) * 12
        yearly_living = yearly_rent + yearly_food + yearly_transport

        # PhD is typically funded - tuition waived, stipend covers ~70% of living
        # Student pays only ~30% of living expenses out of pocket
        if degree_type == "phd":
            out_of_pocket_yearly = yearly_living * 0.3
            books_fees = 800 + 500  # Research materials + conferences
            total_cost = (out_of_pocket_yearly + books_fees) * years
        else:  # Masters
            books_fees = 1000  # Textbooks and fees
            total_cost = (grad_tuition_per_year + yearly_living + books_fees) * years

        print(f"[Orchestrator] {degree_type.upper()} cost for {university}: ${total_cost:,.0f} ({years} years)")
        return round(total_cost, 2)
