# CareerPilot AI

**Multi-agent AI application** that generates complete educational + career roadmaps for Miami Dade College students.

## 🎯 Overview

CareerPilot AI helps MDC students navigate their path from community college to career by:

✅ Analyzing career goals, budget, timeline, and academic profile
✅ Researching MDC programs and transfer universities
✅ Identifying licensing requirements and certifications
✅ Calculating costs and ROI
✅ Generating visual roadmaps with 3 paths: **Cheapest**, **Fastest**, **Prestige**

### Technology Stack

- **Frontend**: Next.js + Tailwind CSS + React Flow
- **Backend**: Cloudflare Worker (BFF API)
- **Agents**: Python + Google ADK + Vertex AI (Gemini)
- **Database**: Cloudflare KV / D1
- **APIs**: Google Custom Search, College Scorecard, BLS Public Data

---

## 📂 Project Structure

```
careerpilot/
├── apps/
│   ├── web/                # Next.js quiz + roadmap UI
│   ├── worker/             # Cloudflare Worker API
│   └── agents/             # Python multi-agent system
│       ├── agents/         # Agent implementations
│       ├── tools/          # API wrappers (Search, Scorecard, BLS)
│       ├── prompts/        # System prompts for each agent
│       ├── schemas/        # Pydantic data models
│       └── tests/          # Unit, integration, E2E tests
├── packages/
│   ├── shared-types/       # TypeScript/Python type definitions
│   └── prompts/            # Centralized prompts
├── data/seed/              # Fallback data (MDC programs, BLS codes)
├── infra/
│   ├── cloudflare/         # D1 schema, wrangler config
│   └── gcp/                # Cloud Run deployment scripts
├── .env.example            # Environment variables template
├── .gitignore              # Security: excludes .env, keys
└── README.md               # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm 9+
- **Python** 3.10+
- **Google Cloud Platform** account (for Vertex AI)
- **API Keys**:
  - Google Custom Search API key + Engine ID
  - College Scorecard API key
  - BLS API key (optional, increases rate limits)

### 1. Clone & Install

```bash
git clone <your-repo-url> careerpilot
cd careerpilot

# Install Node dependencies (monorepo)
npm install

# Install Python dependencies
cd apps/agents
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit .env and fill in your API keys:
# - GCP_PROJECT_ID, GCP_LOCATION
# - GOOGLE_APPLICATION_CREDENTIALS (path to service-account.json)
# - GOOGLE_SEARCH_API_KEY, GOOGLE_SEARCH_ENGINE_ID
# - SCORECARD_API_KEY (optional - fallback data available)
# - BLS_API_KEY (optional - fallback data available)
```

**IMPORTANT**: Download your Google Cloud service account JSON key and save it as `service-account.json` in the `apps/agents/` directory (never commit this file!).

**NOTE**: The College Scorecard and BLS API keys are optional. If not provided, the system will use realistic fallback data for common Florida institutions and occupations. This allows you to test the application without registering for all APIs immediately.

### 3. Run Python Agents (Development)

```bash
cd apps/agents
python main.py
# Server starts on http://localhost:8000
```

### 4. Run Cloudflare Worker (Development)

```bash
cd apps/worker
npm run dev
# Worker starts on http://localhost:8787
```

### 5. Run Next.js Frontend (Development)

```bash
cd apps/web
npm run dev
# Web app starts on http://localhost:3000
```

---

## 🧠 Agent Architecture

### OrchestratorAgent
- Coordinates all sub-agents
- Synthesizes final roadmap with 3 paths
- Resolves conflicts and validates outputs

### IntakeProfilerAgent
- Analyzes quiz responses
- Extracts structured profile (career category, constraints, flags)
- Provides personalized recommendations

### PathwayResearchAgent
- Searches MDC programs (AS.EGR, AS.NUR, etc.)
- Finds transfer universities with articulation agreements
- Identifies licensing requirements (FE, PE, NCLEX, etc.)
- Uses Google Custom Search (restricted to .edu domains)

### CostEstimatorAgent
- Queries College Scorecard API for tuition data
- Calculates 3 paths: cheapest, fastest, prestige
- Estimates financial aid (Pell Grant, Bright Futures)

### SalaryOutlookAgent
- Maps career to BLS occupation code
- Retrieves salary trends from BLS API
- Calculates ROI (years to break even)

---

## 🔑 API Keys Setup

### Google Custom Search

1. Create a Custom Search Engine at https://programmablesearchengine.google.com/
2. Restrict to: `mdc.edu, fiu.edu, fau.edu, floridashines.org, ed.gov`
3. Get API key: https://developers.google.com/custom-search/v1/overview
4. Add to `.env`:
   ```
   GOOGLE_SEARCH_API_KEY=your-key
   GOOGLE_SEARCH_ENGINE_ID=your-engine-id
   ```

### College Scorecard API

1. Register at https://api.data.gov/signup/
2. Add to `.env`:
   ```
   SCORECARD_API_KEY=your-key
   ```

### BLS Public Data API

1. (Optional) Register at https://data.bls.gov/registrationEngine/
2. Increases rate limit from 25/day to 500/day
3. Add to `.env`:
   ```
   BLS_API_KEY=your-key
   ```

### Google Cloud (Vertex AI)

1. Create GCP project at https://console.cloud.google.com/
2. Enable Vertex AI API
3. Create service account with "Vertex AI User" role
4. Download JSON key → save as `apps/agents/service-account.json`
5. Add to `.env`:
   ```
   GCP_PROJECT_ID=your-project-id
   GCP_LOCATION=us-central1
   GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
   ```

---

## 🧪 Testing

### Run All Tests

```bash
# Python agents
cd apps/agents
pytest tests/ -v

# Next.js (if tests are configured)
cd apps/web
npm test

# End-to-end tests
cd apps/web
npx playwright test
```

### Engineering-Focused Test Examples

**Mechanical Engineer Pathway Test**:
```bash
pytest tests/integration/test_orchestrator.py::test_full_mechanical_engineer_roadmap -v
```

**Electrical Engineer with AA Test**:
```bash
pytest tests/integration/test_orchestrator.py::test_full_electrical_engineer_roadmap -v
```

**Software Developer (No License) Test**:
```bash
pytest tests/integration/test_orchestrator.py::test_full_software_developer_roadmap -v
```

See [Enhanced Testing Strategy](#enhanced-testing-strategy) section for complete test coverage.

---

## 📊 Data Sources

| API | Purpose | Rate Limit |
|-----|---------|------------|
| Google Custom Search | MDC programs, transfer agreements | 100 queries/day (free) |
| College Scorecard | Tuition, completion rates | 1000 requests/hour |
| BLS Public Data | Salary, job outlook | 25/day (500/day with key) |
| Vertex AI (Gemini) | Agent intelligence | Pay-per-use |

---

## 🔐 Security

✅ **Never commit** `.env`, `.env.local`, or `service-account.json`
✅ All credentials loaded from environment variables
✅ `.gitignore` configured to exclude secrets
✅ Cloudflare Workers use encrypted environment variables

---

## 🚢 Deployment

### Deploy Python Agents (Google Cloud Run)

```bash
cd apps/agents
gcloud run deploy careerpilot-agents \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

### Deploy Cloudflare Worker

```bash
cd apps/worker
npm run deploy
# Update .env with worker URL
```

### Deploy Next.js (Cloudflare Pages)

```bash
cd apps/web
npm run build
# Connect repo to Cloudflare Pages dashboard
```

---

## 📈 Roadmap Output Example

```json
{
  "paths": {
    "cheapest": {
      "id": "cheapest",
      "name": "Most Affordable Path",
      "total_cost": 28000,
      "duration": "4 years",
      "steps": [
        {
          "type": "program",
          "institution": "Miami Dade College",
          "description": "AS in Engineering (AS.EGR)",
          "duration": "2 years",
          "cost": 6800
        },
        {
          "type": "program",
          "institution": "FIU",
          "description": "BS Mechanical Engineering",
          "duration": "2 years",
          "cost": 13130
        },
        {
          "type": "certification",
          "institution": "NCEES",
          "description": "FE Exam",
          "cost": 175
        }
      ],
      "roi": 6.2
    },
    "fastest": {...},
    "prestige": {...}
  },
  "nodes": [...],  // React Flow nodes
  "edges": [...],  // React Flow edges
  "citations": [...]
}
```

---

## 🤝 Contributing

1. Follow the agent design patterns in `apps/agents/agents/base.py`
2. Add tests for all new features
3. Update prompts in `apps/agents/prompts/` when modifying agent logic
4. Run `pytest` before committing

---

## 📝 License

[Your License Here]

---

## 🆘 Troubleshooting

### "Missing GOOGLE_APPLICATION_CREDENTIALS"
→ Download service account JSON from GCP and save as `service-account.json`

### "No results found for institution"
→ College Scorecard uses exact names. Try "Florida International University" not "FIU"

### "Search API error: 429"
→ Daily quota exceeded. Upgrade Google Custom Search plan or wait 24 hours.

### Agent timeouts
→ Increase `AGENT_TIMEOUT` in `.env` (default: 30 seconds)

---

## 📚 Additional Resources

- [Google ADK Documentation](https://cloud.google.com/vertex-ai/docs)
- [College Scorecard API Docs](https://collegescorecard.ed.gov/data/documentation/)
- [BLS API Guide](https://www.bls.gov/developers/api_signature_v2.htm)
- [React Flow Docs](https://reactflow.dev/)
- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)

---

## Enhanced Testing Strategy

### Unit Tests (Tool Functions)

All API tool wrappers have unit tests with mocked responses:

- `test_search_mdc_engineering_programs()` - Verify MDC program search
- `test_get_fiu_engineering_tuition()` - College Scorecard API
- `test_get_mechanical_engineer_salary()` - BLS API for occupation code 17-2141

### Agent Intelligence Tests

Each agent has tests verifying correct reasoning:

- **IntakeProfilerAgent**: Flags setting (bright_futures_eligible, license_required)
- **PathwayResearchAgent**: ABET accreditation checks, FE/PE exam requirements
- **CostEstimatorAgent**: Cheapest path < 2x prestige path
- **SalaryOutlookAgent**: ROI calculations, salary ranges

### Integration Tests (Full Orchestrator)

End-to-end tests for complete roadmap generation:

```python
# Mechanical Engineer: HS → MDC AS.EGR → FIU BS ME → FE → PE
test_full_mechanical_engineer_roadmap()

# Electrical Engineer with AA: Direct to university (skip MDC)
test_full_electrical_engineer_roadmap()

# Software Developer: No required license
test_full_software_developer_roadmap()
```

### Performance Tests

- `test_orchestrator_completes_under_30_seconds()` - First request
- `test_cache_hit_under_1_second()` - Cached roadmap

### End-to-End Tests (Playwright)

```typescript
// Fill quiz for ME → Submit → Verify roadmap has FE Exam node
test('Mechanical Engineer roadmap generation')

// EE with AA → Verify no MDC nodes (direct to university)
test('Electrical Engineer with transfer credits')

// Software Dev → Verify no required license nodes
test('Software Developer roadmap - no license required')
```

Run specific engineering tests:
```bash
pytest tests/agents/test_pathway_research.py::test_mechanical_engineer_pathway -v
pytest tests/agents/test_pathway_research.py::test_electrical_engineer_pathway -v
pytest tests/agents/test_pathway_research.py::test_software_developer_pathway -v
```

---

**Built with ❤️ for Miami Dade College students**
