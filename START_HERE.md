# 🚀 START HERE - CareerPilot AI

## ⚡ Quick Start (Get Running in 5 Minutes)

### Step 1: Install Python Dependencies

```bash
cd C:\Users\xizzy\Sharkbyte2025\careerpilot\apps\agents

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install
pip install -r requirements.txt
```

### Step 2: Setup Environment Variables

```bash
# Copy template
copy ..\..\. env.example .env

# Edit .env with Notepad
notepad .env
```

**Add these MINIMUM values**:
```env
GCP_PROJECT_ID=your-google-cloud-project-id
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
```

> **Note**: Download `service-account.json` from Google Cloud Console and save it in `apps/agents/` folder

### Step 3: Start Python Agents

```bash
python main.py
```

You should see:
```
╔═══════════════════════════════════════════════════════╗
║       CareerPilot AI - Agent Server                  ║
║                                                       ║
║  Server: http://localhost:8000                       ║
║  Docs:   http://localhost:8000/docs                  ║
╚═══════════════════════════════════════════════════════╝
```

### Step 4: Test It Works

**Open a new terminal** and run:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "agents": {
    "intake_profiler": "ready",
    "pathway_research": "ready",
    "cost_estimator": "ready",
    "salary_outlook": "ready"
  }
}
```

✅ **Backend is working!**

---

## 🎨 Option 1: Add Beautiful UI (Recommended)

### Install Next.js Dependencies

```bash
# New terminal
cd C:\Users\xizzy\Sharkbyte2025\careerpilot\apps\web

npm install
```

### Configure API URL

```bash
# Create .env.local
copy .env.local.example .env.local

# Edit it
notepad .env.local
```

Add this line:
```env
NEXT_PUBLIC_WORKER_API_URL=http://localhost:8000/api/plan
```

### Start Next.js

```bash
npm run dev
```

### Open Your Browser

**Go to: http://localhost:3000**

You should see a beautiful landing page! 🎉

Click **"Start Your Journey"** → Take the quiz → Get your roadmap!

---

## 🧪 Option 2: Test with curl (No UI Needed)

```bash
curl -X POST http://localhost:8000/api/plan ^
  -H "Content-Type: application/json" ^
  -d "{\"quiz_data\": {\"career\": \"Mechanical Engineer\", \"current_education\": \"hs\", \"gpa\": 3.5, \"budget\": \"low\", \"timeline\": \"normal\", \"location\": \"miami\", \"goals\": [\"internship\", \"PE_license\"], \"has_transfer_credits\": false, \"veteran_status\": false, \"work_schedule\": \"full-time-student\"}}"
```

You'll get a complete roadmap JSON! 🎯

---

## 🔑 Do I Need API Keys?

**Minimum (REQUIRED)**:
- ✅ Google Cloud Project + Vertex AI + Service Account JSON

**Optional (Has Fallbacks)**:
- ⏸️ Google Custom Search API
- ⏸️ College Scorecard API
- ⏸️ BLS API

**The app works with JUST Google Cloud!** Other APIs use fallback data if missing.

---

## 🎯 What You'll See

### Test Career: Mechanical Engineer

**Expected Output**:
- ✅ Cheapest Path: ~$28,000 (MDC → FIU)
- ✅ MDC Program: AS.EGR (Engineering)
- ✅ Transfer: FIU or FAU (ABET-accredited)
- ✅ Certifications: FE Exam (Fundamentals of Engineering)
- ✅ License: PE License (Professional Engineer)
- ✅ Salary: $95,300 median
- ✅ ROI: ~6 years

### UI Flow:
1. **Landing Page** → Click "Start Your Journey"
2. **Quiz Page** → Answer 12 questions
3. **Roadmap Page** → See beautiful React Flow graph with 3 paths!

---

## 🆘 Troubleshooting

### "Missing GCP_PROJECT_ID"
→ Edit `.env` file in `apps/agents/` and add your Google Cloud project ID

### "ModuleNotFoundError"
→ Make sure you're in the virtual environment:
```bash
cd apps/agents
venv\Scripts\activate
pip install -r requirements.txt
```

### "Port 8000 already in use"
→ Kill existing Python process or change port in `.env`:
```env
AGENT_SERVER_PORT=8001
```

### "Next.js won't start"
→ Make sure you installed dependencies:
```bash
cd apps/web
npm install
```

### "Roadmap not generating"
→ Check Python terminal for errors. Agent will show detailed progress:
```
[Orchestrator] Starting roadmap generation for: Mechanical Engineer
[Orchestrator] Step 1: Profiling student...
[Orchestrator] Step 2: Researching pathways...
...
```

---

## 📚 Learn More

- **[QUICK_START.md](QUICK_START.md)** - 10-minute guide with examples
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Deploy to production
- **[COMPLETE_SUMMARY.md](COMPLETE_SUMMARY.md)** - Everything you got
- **[README.md](README.md)** - Full documentation

---

## ✨ You're Ready!

**You now have**:
✅ Working Python multi-agent system
✅ Beautiful Next.js UI (optional)
✅ Complete documentation
✅ Test examples
✅ Deployment guides

**Start here**:
1. `cd apps/agents && python main.py` (Start backend)
2. `cd apps/web && npm run dev` (Start UI - optional)
3. Open http://localhost:3000 (or test with curl)

**Enjoy building the future of educational planning!** 🚀

**Questions?** Read the docs above or check the detailed guides!
