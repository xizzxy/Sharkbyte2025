"""
OrchestratorAgent - Coordinates all agents to generate complete roadmap
"""
import json
from datetime import datetime
from typing import Dict, Any
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

        # Step 5: Synthesize roadmap
        print("[Orchestrator] Step 5: Synthesizing roadmap...")
        roadmap = self._synthesize_roadmap(
            profile, pathway_result, cost_result, salary_result
        )

        print(f"[Orchestrator] ✓ Roadmap complete: {len(roadmap['nodes'])} nodes, "
              f"{len(roadmap['edges'])} edges")

        return roadmap

    def _synthesize_roadmap(
        self,
        profile,
        pathway_result,
        cost_result,
        salary_result
    ) -> Dict[str, Any]:
        """
        Synthesize all agent outputs into final roadmap structure

        Creates 3 paths (cheapest, fastest, prestige) with:
        - Steps (programs, certifications, licenses)
        - Nodes (for React Flow visualization)
        - Edges (connections/prerequisites)
        - Citations (source URLs)
        """
        # Build paths
        cheapest_path = self._build_path(
            "cheapest",
            "Most Affordable Path",
            cost_result.cheapest_path,
            pathway_result,
            salary_result.roi_years
        )

        fastest_path = self._build_path(
            "fastest",
            "Fastest Path",
            cost_result.fastest_path,
            pathway_result,
            salary_result.roi_years * 0.8  # Faster path = faster ROI
        )

        prestige_path = self._build_path(
            "prestige",
            "Prestige Path",
            cost_result.prestige_path,
            pathway_result,
            salary_result.roi_years * 1.5  # Higher cost = slower ROI
        )

        # Build nodes and edges for React Flow
        nodes, edges = self._build_graph(pathway_result, profile)

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

    def _build_path(self, path_id: str, name: str, cost_data: Dict, pathway_result, roi: float) -> Dict:
        """Build a single path with steps"""
        steps = []
        step_id = 0

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
                "description": f"{mdc_program.name} ({mdc_program.code})"
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
                    "description": transfer.program
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
                    "description": license.name
                })
                step_id += 1

        return {
            "id": path_id,
            "name": name,
            "total_cost": cost_data["total"],
            "duration": "4 years",
            "steps": steps,
            "roi": roi
        }

    def _build_graph(self, pathway_result, profile) -> tuple:
        """Build nodes and edges for React Flow visualization"""
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
                    "url": mdc.url
                },
                "position": {"x": 250, "y": y_pos}
            })
            prev_node = f"node-{node_id}"
            node_id += 1
            y_pos += 150

        # University nodes
        for i, transfer in enumerate(pathway_result.transfer_options[:3]):
            nodes.append({
                "id": f"node-{node_id}",
                "type": "university",
                "data": {
                    "label": f"{transfer.university}: {transfer.program}",
                    "cost": 13000,
                    "duration": "2 years",
                    "url": transfer.url
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
                node_id += 1
                y_pos += 100

        return nodes, edges
