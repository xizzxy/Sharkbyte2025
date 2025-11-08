"""
FastAPI server for CareerPilot AI agents
"""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from orchestrator import OrchestratorAgent
from schemas.quiz_input import QuizInput

# Load .env from careerpilot/.env
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(
    title="CareerPilot AI Agents",
    description="Multi-agent system for educational roadmap generation",
    version="1.0.0"
)

# CORS middleware (allow Cloudflare Worker to call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your worker domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = OrchestratorAgent()


class PlanRequest(BaseModel):
    """Request body for /api/plan endpoint"""
    quiz_data: dict


class PlanResponse(BaseModel):
    """Response from /api/plan endpoint"""
    success: bool
    roadmap: dict = None
    error: str = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "CareerPilot AI Agents",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agents": {
            "intake_profiler": "ready",
            "pathway_research": "ready",
            "cost_estimator": "ready",
            "salary_outlook": "ready"
        },
        "environment": {
            "gcp_project": os.getenv("GCP_PROJECT_ID") is not None,
            "search_api": os.getenv("GOOGLE_SEARCH_API_KEY") is not None,
            "scorecard_api": os.getenv("SCORECARD_API_KEY") is not None,
            "bls_api": os.getenv("BLS_API_KEY") is not None
        }
    }


@app.post("/api/plan", response_model=PlanResponse)
async def generate_plan(request: PlanRequest):
    """
    Generate educational roadmap from quiz data

    Args:
        request: Quiz data from user

    Returns:
        Complete roadmap with paths, nodes, edges, citations
    """
    try:
        # Validate quiz data
        quiz = QuizInput(**request.quiz_data)

        # Generate roadmap
        roadmap = orchestrator.generate_roadmap(quiz.model_dump())

        return PlanResponse(
            success=True,
            roadmap=roadmap
        )

    except ValueError as e:
        # Validation error
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Internal error
        print(f"[ERROR] Roadmap generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/careers")
async def list_careers():
    """Get list of supported careers"""
    return {
        "careers": [
            {"name": "Mechanical Engineer", "category": "STEM-Engineering"},
            {"name": "Electrical Engineer", "category": "STEM-Engineering"},
            {"name": "Civil Engineer", "category": "STEM-Engineering"},
            {"name": "Software Developer", "category": "STEM-Technology"},
            {"name": "Registered Nurse", "category": "Healthcare"},
            {"name": "Architect", "category": "STEM-Architecture"},
            {"name": "Accountant", "category": "Business"},
            {"name": "Data Scientist", "category": "STEM-Technology"},
        ]
    }


class ChatRequest(BaseModel):
    """Request body for /api/chat endpoint"""
    message: str
    system_prompt: str


class ChatResponse(BaseModel):
    """Response from /api/chat endpoint"""
    response: str


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for roadmap Q&A using Google AI

    Args:
        request: User message and system prompt

    Returns:
        AI-generated response
    """
    try:
        import google.generativeai as genai

        # Configure Google AI with API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        genai.configure(api_key=api_key)

        # Create model
        model = genai.GenerativeModel(
            "gemini-2.0-flash-exp",
            system_instruction=request.system_prompt
        )

        # Generate response
        response = model.generate_content(
            request.message,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=500,
            )
        )

        return ChatResponse(response=response.text)

    except Exception as e:
        print(f"[ERROR] Chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("AGENT_SERVER_PORT", 8000))

    print(f"""
    ========================================================
         CareerPilot AI - Agent Server

      Server: http://localhost:{port}
      Docs:   http://localhost:{port}/docs
      Health: http://localhost:{port}/health
    ========================================================
    """)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
