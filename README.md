## Team

Team Name: VendorIQ

- Anisetti Chaitanya Lakshmi
- Kodali Laxmi Yasasvi
- Sankepally Abhinaya Reddy 


# VendorIQ — Intelligent Next Best Action Platform

> Agentic Decision Intelligence for Vendor Onboarding & Risk Assessment  
> Built for Hackathon: **Intelligent Next Best Action Platform**

---

## What is VendorIQ?

VendorIQ is a **reusable Agentic Decision Intelligence Platform** that automates vendor onboarding for large enterprises.

It ingests vendor documents, retrieves organizational procurement policies from a vector database, runs a multi-agent compliance and risk analysis, and recommends the next best action — with full explainability and a human-in-the-loop approval step.

**Business Domain:** B2B Procurement / Vendor Management

**Problem Solved:** Procurement teams manually review hundreds of vendor submissions per year. Each review requires reading documents, checking policies, assessing risk, and deciding on approval. VendorIQ automates this entire workflow using coordinated AI agents while keeping humans in control of final decisions.

---

## Live Evaluation Results

> Run `python evaluation_pipeline.py` to reproduce these results.

| Metric | Result |
|---|---|
| Risk Classification Accuracy | **100%** |
| Recommendation Accuracy | **100%** |
| Average Confidence Score | **73%** |
| Scenarios Evaluated | **5** |
| Document Agent avg latency | 14.4ms |
| Compliance Agent avg latency | 0.2ms |
| Risk Agent avg latency | 0.0ms |
| Decision Agent avg latency | 5255ms (Gemini API call) |

---

## Architecture

```
Vendor Uploads PDFs
        │
        ▼
┌─────────────────────┐
# VendorIQ — Intelligent Next Best Action Platform

Agentic Decision Intelligence for Vendor Onboarding & Risk Assessment.

---

## Quick Overview

VendorIQ analyzes vendor submissions (PDFs), retrieves relevant procurement policies, runs a multi-agent pipeline (document -> RAG -> compliance -> risk -> decision), and surfaces a recommended next action with explainability and a human-in-the-loop approval path.

---

## Quick Start

Prerequisites:

- Python 3.11+
- Node.js 18+
- MongoDB (Atlas or local)

Backend (run in project root):

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# create or edit .env with GEMINI_API_KEY and MONGODB_URI
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Frontend (run in project root):

```bash
cd frontend
npm install
npm run dev
```

Notes:

- Frontend dev server proxies `/api` to `http://localhost:8000` (see `frontend/vite.config.js`).
- Leave `GEMINI_API_KEY` empty to force the rule-based decision fallback during evaluation.

---

## Project Structure (high level)

| Path | Purpose |
|---|---|
| `backend/agents/` | Agent implementations: planner, document, compliance, risk, decision, memory |
| `backend/api/` | FastAPI routers for upload, what-if, approve, history |
| `backend/rag/` | ChromaDB initialization and policy seeds |
| `backend/database/` | MongoDB connection (Motor) |
| `backend/sample_data/` | Generated sample PDFs for evaluation |
| `frontend/` | React + Vite frontend (pages, components) |
| `backend/config.py` | Settings and `.env` mapping |
| `backend/main.py` | FastAPI app entrypoint |
| `backend/evaluation_pipeline.py` | End-to-end, rule-based evaluation script (uses sample PDFs) |
| `backend/evaluation.py` | Statistical/visual evaluation harness (synthetic data + plots) |

---

## Running Evaluations

- End-to-end hackathon pipeline (uses sample PDFs, safe fallback):

```bash
cd backend
source venv/bin/activate
python evaluation_pipeline.py
```

- Statistical evaluation (synthetic dataset → plots):

```bash
cd backend
source venv/bin/activate
python evaluation.py
```

Outputs:

- `backend/evaluation_report.json` (pipeline report)
- `backend/evaluation_results.json` and `backend/evaluation_plots/` (plots from `evaluation.py`)

---

## Environment Variables (`backend/.env`)

| Variable | Purpose | Example |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini key (optional) | `your_gemini_api_key_here` |
| `MONGODB_URI` | MongoDB connection URI | `mongodb+srv://user:pass@host/db` |
| `MONGODB_DB_NAME` | Database name used by app | `vendoriq` |
| `CHROMA_PERSIST_DIR` | Local ChromaDB directory | `./chroma_db` |

---

## Project Overview

VendorIQ is an agentic decision-intelligence prototype for automated vendor onboarding. It combines document parsing, retrieval-augmented generation (RAG) for policy lookup, deterministic compliance checks, risk scoring, and (optionally) LLM-based recommendations to produce an explainable next best action.

---

## Additional Notes

- Keep `backend/.env` out of source control. Use secrets manager for production keys.
- The `evaluation_pipeline.py` uses a safe rule-based fallback if `GEMINI_API_KEY` is not configured.
- `frontend/vite.config.js` proxies `/api` to `http://localhost:8000` during development.
- To generate the sample PDFs used by evaluations: `python backend/sample_data/generate_samples.py`.
- If you want, I can add a `docker-compose.yml` to run the frontend, backend and a local MongoDB together.

Open a **second terminal**, keep the backend running in the first:

```bash
cd vendoriq/frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

---

### Step 4 — Run the Evaluation Pipeline

```bash
# In backend terminal with venv activated
cd vendoriq/backend
source venv/bin/activate
python evaluation_pipeline.py
```

Expected results:

```
Risk Classification Accuracy     100.0%
Recommendation Accuracy          100.0%
Average Confidence Score          73.0%
OVERALL SCORE:                    100%
Full report saved to: evaluation_report.json
```

---

### Step 5 — Test with the UI

1. Open http://localhost:5173
2. Drag all 8 PDFs from `backend/sample_data/vendor_docs/` onto the upload area
3. Click **Analyze Documents**
4. Watch the agent timeline execute in real time
5. Review the Dashboard — Compliance Checklist, Confidence Meter, Evidence Panel
6. Click **Approve**, **Reject**, or **Defer** to record your human decision
7. Go to **History** to see all decisions stored in MongoDB

---

## Commands Reference

Every time you open a new terminal, run these:

**Terminal 1 — Backend**

```bash
cd vendoriq/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend**

```bash
cd vendoriq/frontend
npm run dev
```

**Terminal 3 — Evaluation**

```bash
cd vendoriq/backend
source venv/bin/activate
python evaluation_pipeline.py
```

---

## Environment Variables

Create `backend/.env` with the following:

```env
GEMINI_API_KEY=AIzaSy...your_key_here...
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/vendoriq
MONGODB_DB_NAME=vendoriq
CHROMA_PERSIST_DIR=./chroma_db
LOG_LEVEL=INFO
```

---

## API Reference

### POST /upload

Upload vendor PDFs and run the full agentic pipeline.

```bash
curl -X POST http://localhost:8000/upload \
  -F "files=@sample_data/vendor_docs/gst_certificate.pdf" \
  -F "files=@sample_data/vendor_docs/pan_card.pdf"
```

Returns full analysis with vendor info, compliance checklist, risk level, and AI decision.

---

### POST /approve

Record a human procurement officer's decision.

```bash
curl -X POST http://localhost:8000/approve \
  -H "Content-Type: application/json" \
  -d '{
    "vendor_name": "Nexus Manufacturing Pvt Ltd",
    "recommendation": "Approve Vendor",
    "human_decision": "Approved",
    "notes": "All documents verified.",
    "confidence_score": 0.95,
    "risk_level": "Low",
    "compliance_score": 100.0
  }'
```

---

### GET /history

Retrieve all past vendor decisions from MongoDB.

```bash
curl http://localhost:8000/history?limit=20
```

---

### POST /whatif

Simulate how a change would affect the recommendation.

```bash
curl -X POST http://localhost:8000/whatif \
  -H "Content-Type: application/json" \
  -d '{
    "vendor_name": "Sunrise Textiles Ltd",
    "scenario": "The vendor uploads a renewed ISO certificate valid for 3 years",
    "current_analysis": {"recommendation": "Request Missing Documents"}
  }'
```

---

## Evaluation Scenarios

| Scenario | Vendor | Risk | Compliance | Recommendation | Match |
|---|---|---|---|---|---|
| SC-001 | Nexus Manufacturing Pvt Ltd | Low | 100% | Approve Vendor | ✅ |
| SC-002 | Sunrise Textiles Ltd | Medium | 83.3% | Request Missing Documents | ✅ |
| SC-003 | Global Tech Solutions Pvt | High | 50% | Escalate for Manual Review | ✅ |
| SC-004 | BrightPath Logistics | High | 16.7% | Request Missing Documents | ✅ |
| SC-005 | AlphaSecure Systems | Low | 100% | Escalate for Manual Review | ✅ |

---

## How to Extend the Platform

**Add a new agent:**

1. Create `backend/agents/my_new_agent.py` with a `run_my_agent()` function
2. Import and call it in `backend/agents/planner.py`
3. Add a new `AgentStep` to the timeline

**Add a new knowledge source / policy:**

1. Add entries to `PROCUREMENT_POLICIES` in `backend/rag/chroma_store.py`
2. ChromaDB re-seeds automatically on next startup

**Add a new compliance rule:**

1. Add a new check block in `backend/agents/compliance_agent.py`
2. Risk and Decision agents automatically incorporate the new violation

**Add a new UI page:**

1. Create `frontend/src/pages/MyPage.jsx`
2. Add a route in `frontend/src/App.jsx`
3. Add a nav link in `frontend/src/components/Navbar.jsx`

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `502 Bad Gateway` in the frontend | Backend is not running. Start it with `uvicorn main:app --reload --port 8000` |
| `ECONNREFUSED` in Vite terminal | Same as above — backend must run first |
| `ModuleNotFoundError` on startup | Run `pip install -r requirements.txt` with venv activated |
| ChromaDB telemetry warnings | Harmless. Ignore `capture() takes 1 positional argument` messages |
| MongoDB connection timeout | Atlas → Network Access → allow your IP or use `0.0.0.0/0` |
| Gemini 403 or quota error | Check `GEMINI_API_KEY` in `.env`. Rule-based fallback activates automatically |
| `sentence-transformers` slow first run | Normal — downloads the 90MB embedding model once on first startup |
| Port 8000 already in use | Run on `--port 8001` and update `vite.config.js` proxy target to match |

---

## License

MIT
