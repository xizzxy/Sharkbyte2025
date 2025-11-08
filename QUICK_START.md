# 🚀 CareerPilot AI - Quick Start Guide

**Get your multi-agent system running in 10 minutes!**

---

## ⚡ The Fastest Path to Testing

### Step 1: Install Python Dependencies (2 minutes)

```bash
cd C:\Users\xizzy\Sharkbyte2025\careerpilot\apps\agents

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 2: Set Up Environment Variables (3 minutes)

```bash
# Copy template
copy ..\..\. env.example .env

# Edit .env with your favorite editor
notepad .env
```

**Minimum Required (to test without external APIs)**:
```env
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
```

**Optional (for full functionality)**:
```env
GOOGLE_SEARCH_API_KEY=your-key
GOOGLE_SEARCH_ENGINE_ID=your-cx
SCORECARD_API_KEY=your-key
BLS_API_KEY=your-key
```

> **Note**: The agents will work with fallback data even without external API keys!

---

### Step 3: Download Google Cloud Service Account (5 minutes)

1. Go to https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Enable "Vertex AI API"
4. Go to IAM & Admin → Service Accounts
5. Create Service Account → "CareerPilot Agent"
6. Grant role: "Vertex AI User"
7. Keys → Add Key → Create New Key → JSON
8. Download and save as `service-account.json` in `apps/agents/`

---

### Step 4: Start the Agent Server (30 seconds)

```bash
python main.py
```

**You should see**:
```
╔═══════════════════════════════════════════════════════╗
║       CareerPilot AI - Agent Server                  ║
║                                                       ║
║  Server: http://localhost:8000                       ║
║  Docs:   http://localhost:8000/docs                  ║
║  Health: http://localhost:8000/health                ║
╚═══════════════════════════════════════════════════════╝

INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## ✅ Test It Works!

### Test 1: Health Check

**In a new terminal (or browser)**:
```bash
curl http://localhost:8000/health
```

**Expected**:
```json
{
  "status": "healthy",
  "agents": {
    "intake_profiler": "ready",
    "pathway_research": "ready",
    "cost_estimator": "ready",
    "salary_outlook": "ready"
  },
  "environment": {
    "gcp_project": true,
    "search_api": false,  // OK if you don't have keys yet
    "scorecard_api": false,
    "bls_api": false
  }
}
```

---

### Test 2: Generate Mechanical Engineer Roadmap

**Copy-paste this into your terminal**:

```bash
curl -X POST http://localhost:8000/api/plan ^
  -H "Content-Type: application/json" ^
  -d "{\"quiz_data\": {\"career\": \"Mechanical Engineer\", \"current_education\": \"hs\", \"gpa\": 3.5, \"budget\": \"low\", \"timeline\": \"normal\", \"location\": \"miami\", \"goals\": [\"internship\", \"PE_license\"], \"has_transfer_credits\": false, \"veteran_status\": false, \"work_schedule\": \"full-time-student\"}}"
```

**Expected** (simplified):
```json
{
  "success": true,
  "roadmap": {
    "paths": {
      "cheapest": {
        "total_cost": 28000,
        "steps": [
          {"institution": "Miami Dade College", "description": "AS.EGR"},
          {"institution": "FIU", "description": "BS Mechanical Engineering"},
          {"description": "FE Exam"},
          {"description": "PE License"}
        ]
      }
    },
    "metadata": {
      "career": "Mechanical Engineer",
      "salary_outlook": {
        "median_salary": 95300,
        "growth_rate": "4%"
      }
    }
  }
}
```

---

### Test 3: Generate Software Developer Roadmap

```bash
curl -X POST http://localhost:8000/api/plan ^
  -H "Content-Type: application/json" ^
  -d "{\"quiz_data\": {\"career\": \"Software Developer\", \"current_education\": \"hs\", \"gpa\": 3.2, \"budget\": \"medium\", \"timeline\": \"normal\", \"location\": \"miami\", \"goals\": [\"internship\"], \"has_transfer_credits\": false, \"veteran_status\": false, \"work_schedule\": \"full-time-student\"}}"
```

**Key Difference**: Software Developer will have **NO required licenses** (unlike Mechanical Engineer)

---

### Test 4: Run Engineering Tests

```bash
pytest tests/agents/test_pathway_research.py -v
```

**Expected**:
```
test_mechanical_engineer_pathway PASSED
test_electrical_engineer_pathway PASSED
test_software_developer_pathway PASSED
test_registered_nurse_pathway PASSED
```

---

## 🎯 What Each Agent Does

### 1️⃣ IntakeProfilerAgent
**Input**: Quiz data (career, GPA, budget, timeline)
**Output**: Structured profile with flags

**Example**:
```json
{
  "career": "Mechanical Engineer",
  "category": "STEM-Engineering",
  "flags": ["community_college_optimal", "bright_futures_eligible", "license_required"],
  "recommendations": ["Start at MDC with AS.EGR", "Apply for Bright Futures"]
}
```

---

### 2️⃣ PathwayResearchAgent
**Input**: Career profile
**Output**: MDC programs, transfer options, licenses

**Example**:
```json
{
  "mdc_programs": [{"code": "AS.EGR", "name": "Engineering AS"}],
  "transfer_options": [{"university": "FIU", "program": "BS ME", "abet_accredited": true}],
  "certifications": [{"name": "FE Exam", "required": true}],
  "licenses": [{"name": "PE License", "required": true, "state": "Florida"}]
}
```

---

### 3️⃣ CostEstimatorAgent
**Input**: Profile + pathway data
**Output**: 3 cost paths

**Example**:
```json
{
  "cheapest_path": {"total": 28000, "breakdown": {"mdc": 6800, "fiu": 13130}},
  "fastest_path": {"total": 32200},
  "prestige_path": {"total": 120000, "breakdown": {"mdc": 6800, "mit": 112000}}
}
```

---

### 4️⃣ SalaryOutlookAgent
**Input**: Career name
**Output**: Salary, growth rate, ROI

**Example**:
```json
{
  "occupation": "Mechanical Engineers",
  "bls_code": "17-2141",
  "median_salary": 95300,
  "growth_rate": "4% (2023-2033)",
  "roi_years": 6.2
}
```

---

### 5️⃣ OrchestratorAgent
**Coordinates all agents** → Produces final roadmap with:
- 3 paths (cheapest, fastest, prestige)
- Nodes and edges for visualization
- Citations (source URLs)
- Metadata

---

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'vertexai'"
```bash
pip install -r requirements.txt
```

### "Missing GCP_PROJECT_ID in environment"
Edit `.env` and add your GCP project ID

### "Failed to authenticate with Vertex AI"
- Ensure `service-account.json` exists
- Check `GOOGLE_APPLICATION_CREDENTIALS=./service-account.json` in `.env`

### "ImportError: attempted relative import with no known parent package"
```bash
# Add apps/agents to PYTHONPATH
cd apps/agents
export PYTHONPATH=$PYTHONPATH:$(pwd)  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%CD%      # Windows
```

---

## 📚 Next Steps

### Option 1: Add More API Keys (Better Data)
- Get Google Custom Search API key → real MDC/FIU program data
- Get College Scorecard API key → actual tuition costs
- Get BLS API key → up-to-date salary data

### Option 2: Test More Careers
```bash
# Electrical Engineer
curl -X POST http://localhost:8000/api/plan -H "Content-Type: application/json" -d "{\"quiz_data\": {\"career\": \"Electrical Engineer\", ...}}"

# Registered Nurse
curl -X POST http://localhost:8000/api/plan -H "Content-Type: application/json" -d "{\"quiz_data\": {\"career\": \"Registered Nurse\", ...}}"
```

### Option 3: Build the Frontend
See `SETUP.md` → Section 2 (Next.js Quiz Interface)

### Option 4: Deploy to Cloud
See `SETUP.md` → Deployment section

---

## 🎉 You're Done!

Your multi-agent AI system is now running!

**What you built**:
✅ 4 specialized AI agents (IntakeProfiler, PathwayResearch, CostEstimator, SalaryOutlook)
✅ 1 orchestrator agent (coordinates everything)
✅ 3 API integrations (Google Search, College Scorecard, BLS)
✅ FastAPI server with RESTful endpoints
✅ Engineering-focused test suite
✅ Complete type safety with Pydantic
✅ Security best practices (no hard-coded credentials)

**Test it now**: http://localhost:8000/docs (FastAPI auto-generated docs)

---

**Questions?** See:
- `README.md` - Complete documentation
- `SETUP.md` - Detailed setup guide
- `IMPLEMENTATION_STATUS.md` - What's built vs what's pending

**Happy roadmap generating!** 🚀
