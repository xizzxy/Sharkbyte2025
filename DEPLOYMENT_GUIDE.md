# 🚀 CareerPilot AI - Complete Deployment Guide

## 📦 What You Have Now

✅ **Python Multi-Agent System** (Fully functional)
✅ **Cloudflare Worker** (BFF API with caching)
✅ **Next.js Beautiful UI** (Quiz + Roadmap visualization)
✅ **Seed Data** (Fallback for offline mode)

---

## 🎯 Deployment Options

### Option 1: Local Development (Start Here)

**Best for**: Testing everything works before deploying

#### Step 1: Start Python Agents

```bash
cd apps/agents
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Edit .env with your API keys
python main.py
# Runs on http://localhost:8000
```

#### Step 2: Start Cloudflare Worker (Optional for local dev)

```bash
cd apps/worker
npm install
npm run dev
# Runs on http://localhost:8787
```

**OR skip Worker and connect Next.js directly to Python**:
Edit `apps/web/.env.local`:
```
NEXT_PUBLIC_WORKER_API_URL=http://localhost:8000/api/plan
```

#### Step 3: Start Next.js Frontend

```bash
cd apps/web
npm install
npm run dev
# Runs on http://localhost:3000
```

**Open http://localhost:3000** → Beautiful landing page! 🎉

---

### Option 2: Production Deployment

#### 1️⃣ Deploy Python Agents to Google Cloud Run

```bash
cd apps/agents

# Create Dockerfile
cat > Dockerfile <<EOF
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD exec uvicorn main:app --host 0.0.0.0 --port \$PORT
EOF

# Build and deploy
gcloud run deploy careerpilot-agents \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT_ID=your-project-id,GCP_LOCATION=us-central1" \
  --set-secrets="GOOGLE_APPLICATION_CREDENTIALS=service-account:latest,GOOGLE_SEARCH_API_KEY=google-search-key:latest,SCORECARD_API_KEY=scorecard-key:latest,BLS_API_KEY=bls-key:latest"

# Get the URL
gcloud run services describe careerpilot-agents --region us-central1 --format 'value(status.url)'
# Copy this URL for Worker config
```

#### 2️⃣ Deploy Cloudflare Worker

```bash
cd apps/worker

# Install Wrangler CLI
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Create KV namespaces
wrangler kv:namespace create "ROADMAP_CACHE"
wrangler kv:namespace create "RATE_LIMIT"

# Update wrangler.toml with the IDs returned
# Also update PYTHON_AGENT_API_URL with your Cloud Run URL

# Deploy
wrangler deploy

# Get Worker URL
# https://careerpilot-worker.your-subdomain.workers.dev
```

#### 3️⃣ Deploy Next.js to Cloudflare Pages

```bash
cd apps/web

# Build
npm run build

# Option A: Deploy via Wrangler
npx wrangler pages deploy .next/static --project-name=careerpilot

# Option B: Connect GitHub repo to Cloudflare Pages
# 1. Push code to GitHub
# 2. Go to Cloudflare Dashboard → Pages → Create Project
# 3. Connect GitHub repo
# 4. Build settings:
#    - Build command: npm run build
#    - Build output directory: .next
#    - Root directory: apps/web

# Set environment variable:
# NEXT_PUBLIC_WORKER_API_URL=https://careerpilot-worker.your-subdomain.workers.dev
```

---

## 🔑 Required API Keys (Where to Get Them)

### 1. Google Cloud (Vertex AI) - REQUIRED

**Used for**: AI agents (Gemini)

**Steps**:
1. Go to https://console.cloud.google.com/
2. Create new project: "CareerPilot"
3. Enable APIs:
   - Vertex AI API
   - Generative Language API
4. Create Service Account:
   - IAM & Admin → Service Accounts → Create
   - Name: "careerpilot-agent"
   - Role: "Vertex AI User"
5. Create JSON key:
   - Actions → Manage Keys → Add Key → Create New Key → JSON
   - Download and save as `apps/agents/service-account.json`
6. Add to `.env`:
   ```
   GCP_PROJECT_ID=your-project-id
   GCP_LOCATION=us-central1
   GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
   ```

**Cost**: Pay-per-use (Gemini ~$0.001/1K tokens)

---

### 2. Google Custom Search - OPTIONAL

**Used for**: Searching MDC/FIU/FAU websites

**Steps**:
1. Create search engine: https://programmablesearchengine.google.com/
2. Settings:
   - Name: "CareerPilot Educational Search"
   - Sites to search:
     - `mdc.edu`
     - `fiu.edu`
     - `fau.edu`
     - `floridashines.org`
     - `ed.gov`
3. Get Engine ID from control panel
4. Get API key: https://developers.google.com/custom-search/v1/overview
5. Add to `.env`:
   ```
   GOOGLE_SEARCH_API_KEY=your-api-key
   GOOGLE_SEARCH_ENGINE_ID=your-engine-id
   ```

**Cost**: Free (100 queries/day)

**Fallback**: Seed data in `data/seed/mdc_programs.json`

---

### 3. College Scorecard API - OPTIONAL

**Used for**: Tuition costs, completion rates

**Steps**:
1. Register: https://api.data.gov/signup/
2. Confirm email
3. Copy API key
4. Add to `.env`:
   ```
   SCORECARD_API_KEY=your-api-key
   ```

**Cost**: Free (1000 requests/hour)

**Fallback**: Hardcoded tuition estimates in agent

---

### 4. BLS Public Data API - OPTIONAL

**Used for**: Salary data, job outlook

**Steps**:
1. Register: https://data.bls.gov/registrationEngine/
2. Confirm email
3. Copy registration key
4. Add to `.env`:
   ```
   BLS_API_KEY=your-registration-key
   ```

**Cost**: Free (500 requests/day with key, 25/day without)

**Fallback**: Seed data in `data/seed/bls_occupation_codes.json`

---

## 🧪 Testing the Complete System

### Test 1: Local Full Stack

```bash
# Terminal 1: Python agents
cd apps/agents && python main.py

# Terminal 2: Cloudflare Worker
cd apps/worker && npm run dev

# Terminal 3: Next.js
cd apps/web && npm run dev

# Open http://localhost:3000
# Take quiz → Get beautiful roadmap!
```

### Test 2: Bypass Worker (Direct to Python)

```bash
# Terminal 1: Python agents
cd apps/agents && python main.py

# Terminal 2: Next.js (no worker)
cd apps/web
# Edit .env.local: NEXT_PUBLIC_WORKER_API_URL=http://localhost:8000/api/plan
npm run dev

# Open http://localhost:3000
```

### Test 3: Production URLs

```bash
# Test Cloud Run agents
curl https://your-cloud-run-url.run.app/health

# Test Worker
curl https://your-worker.workers.dev/health

# Open Next.js site
# https://careerpilot.pages.dev
```

---

## 📊 Architecture Flow

```
User Browser
    ↓
Next.js (Cloudflare Pages)
http://localhost:3000 or https://careerpilot.pages.dev
    ↓
Quiz Form (12 questions)
    ↓
POST /api/plan
    ↓
Cloudflare Worker (Edge API)
http://localhost:8787 or https://worker.workers.dev
    ↓
[Check KV Cache]
    ↓
Python Agents (Cloud Run)
http://localhost:8000 or https://agents.run.app
    ↓
OrchestratorAgent
    ├─ IntakeProfilerAgent
    ├─ PathwayResearchAgent (→ Google Search)
    ├─ CostEstimatorAgent (→ College Scorecard)
    └─ SalaryOutlookAgent (→ BLS API)
    ↓
Roadmap JSON
    ↓
[Cache in KV]
    ↓
Return to Next.js
    ↓
Beautiful React Flow Visualization! 🎉
```

---

## 🎨 What the UI Looks Like

### Landing Page (`/`)
- Gradient hero section: "CareerPilot AI"
- 4 feature cards (Smart Pathways, Cost Analysis, Career Outlook, Florida-Focused)
- Popular career cards with emojis
- "How It Works" 3-step guide
- CTA button: "Start Your Journey"

### Quiz Page (`/quiz`)
- 12 beautiful questions in a card layout
- Dropdowns, radio buttons, checkboxes
- Real-time validation
- Loading state with spinner: "Generating your roadmap..."
- Error handling

### Roadmap Page (`/roadmap`)
- Split layout:
  - **Left sidebar**:
    - 3 path cards (Cheapest, Fastest, Prestige)
    - Salary outlook stats
    - Step-by-step breakdown
    - Source citations
    - Download PDF / Share buttons
  - **Right side**:
    - Interactive React Flow graph
    - Color-coded nodes (MDC=blue, University=purple, Cert=green, License=yellow)
    - Minimap & controls
    - Legend

---

## 🔧 Troubleshooting

### "No API keys" - App Still Works!

**All external APIs are optional**. The system has fallbacks:
- ✅ Google Search → Seed data (`mdc_programs.json`)
- ✅ College Scorecard → Hardcoded tuition estimates
- ✅ BLS API → Seed salary data (`bls_occupation_codes.json`)

### "Worker not working"

**Bypass it!** Connect Next.js directly to Python:
```bash
# apps/web/.env.local
NEXT_PUBLIC_WORKER_API_URL=http://localhost:8000/api/plan
```

### "Python agents timeout"

Increase timeout in `.env`:
```
AGENT_TIMEOUT=60
```

### "React Flow not showing"

Check browser console for errors. Make sure `reactflow` package installed:
```bash
cd apps/web
npm install reactflow
```

---

## 🎉 You're Done!

**You now have a complete, production-ready application**:

✅ **Backend**: Python multi-agent system with Vertex AI
✅ **API Layer**: Cloudflare Worker with caching
✅ **Frontend**: Beautiful Next.js UI with React Flow
✅ **Security**: All secrets in .env, nothing hard-coded
✅ **Testing**: Engineering-focused test suite
✅ **Documentation**: Complete setup guides

**Next steps**:
1. Test locally (see "Testing" section above)
2. Deploy to production (see "Option 2" above)
3. Add more careers (update prompts + seed data)
4. Customize UI colors/branding

**Questions?** See:
- [README.md](README.md) - Project overview
- [QUICK_START.md](QUICK_START.md) - 10-minute setup
- [SETUP.md](SETUP.md) - Detailed guide

**Enjoy building the future of educational planning!** 🚀
