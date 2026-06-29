# VendorIQ — Architecture

This document describes the architectural components, data flow, and integrations for VendorIQ.

---

## High-level Overview

VendorIQ orchestrates several specialist agents to analyze vendor-submitted documents and recommend a next best action. The pipeline is designed for explainability and human oversight.

Components:

- Frontend: React + Vite + Tailwind — user interface for uploads, dashboard, history, and what-if analysis.
- Backend API: FastAPI (uvicorn) exposing upload, what-if, approve, history endpoints.
- Agents (Python modules): Planner, Document, Policy/RAG, Compliance, Risk, Decision, Memory.
- Vector DB / RAG: ChromaDB for policy retrieval.
- Database: MongoDB (Motor async) for storing decisions and audit trail.
- LLM: Google Gemini (optional) used by Decision Agent; rule-based fallback available.

Ports and endpoints (default):

- Frontend dev server: `localhost:5173`
- Backend API: `localhost:8000` (proxied by frontend)
- Key API routes:
  - `POST /api/upload` — upload files (documents) and run analysis
  - `POST /api/whatif` — run a what-if injection scenario
  - `POST /api/approve` — record human approval / override
  - `GET  /api/history` — fetch stored decision history

---

## Data Flow

1. User uploads PDF(s) from the UI (`UploadPage`). The frontend sends a `multipart/form-data` POST to `/api/upload`.
2. Backend `upload` router receives files and calls the `planner` agent.
3. Planner coordinates:
   - Document Agent: extracts structured fields (GST, PAN, ISO dates, audit score, bank details) using PyMuPDF.
   - Policy/RAG Agent: queries ChromaDB to retrieve relevant policy excerpts.
   - Compliance Agent: applies rule checks to compute compliance checklist and score.
   - Risk Agent: computes risk level based on failures and business rules.
   - Decision Agent: uses Gemini (if configured) or rule-based fallback to produce recommendation, confidence, evidence, and next-best-action.
4. Response payload is returned to the frontend and also optionally written to MongoDB by the Memory Agent.
5. UI renders the `DashboardPage` with recommendation, confidence meter, evidence panel, agent timeline, and human approval controls. Human decisions are sent to `POST /api/approve`.

---

## Agents — Responsibilities

| Agent | Responsibility |
|---|---|
| `planner.py` | Orchestrates the end-to-end flow, error handling, and combining outputs into a single analysis object |
| `document_agent.py` | PDF parsing and structured field extraction (PyMuPDF) |
| `policy_agent.py` | ChromaDB interaction and retrieval of relevant policy excerpts |
| `compliance_agent.py` | Runs policy checks and builds a checklist + compliance score |
| `risk_agent.py` | Converts compliance results into a `Low`/`Medium`/`High` risk level |
| `decision_agent.py` | LLM invocation (Gemini) or rule-based fallback to produce recommendation, reason, and evidence |
| `memory_agent.py` | Persists decisions to MongoDB and retrieves historical patterns |

---

## RAG / ChromaDB

- Seeded with procurement policy documents during repo initialization (`rag/chroma_store.py`).
- Chroma persists locally (by default `./chroma_db`) and can be re-seeded as needed.
- Retrieval is used by the Decision and Compliance agents to provide policy citations and evidence.

---

## API Contract (concise)

- `POST /api/upload` — Request: `files[]` (PDFs), optional `what_if_scenario` JSON. Response: analysis object with `vendor_info`, `compliance`, `risk`, `decision`, `agent_timeline`, `policy_excerpts`.
- `POST /api/whatif` — Request: scenario patch; Response: hypothetical analysis.
- `POST /api/approve` — Request: `{ vendor_name, human_decision, notes, confidence_score, risk_level, compliance_score }`. Response: saved confirmation.
- `GET /api/history` — Query params: `limit`; Response: stored decision records.

---

## Deployment & Runtime Notes

- When `GEMINI_API_KEY` is not configured, the Decision Agent falls back to a deterministic rule-based recommender. This is safe for local evaluation and tests.
- For production: provide `GEMINI_API_KEY` and ensure the key is kept secret (do not commit `.env` to git).
- Chroma persistence directory should be mounted or persisted when deploying (avoid re-indexing each restart).
- MongoDB should use a secure, network-restricted connection string (Atlas recommended for demo/hackathon).

---

## Observability & Testing

- Logs: structured logger in `backend/utils/logger.py` — adjust `LOG_LEVEL` in `.env` or `config.py`.
- Evaluation scripts:
  - `backend/evaluation_pipeline.py` — runs sample scenarios and prints a textual report, saves `evaluation_report.json`.
  - `backend/evaluation.py` — generates synthetic dataset statistics and PNG plots in `backend/evaluation_plots/`.

---

## Key Design Decisions

- Agent-based modular architecture: each responsibility (document parsing, policy retrieval, compliance checking, risk scoring, decisioning, memory) is isolated to make testing and replacement easier.
- Rule-based fallback for Decision Agent: safe default when LLM key is absent to allow offline evaluation and avoid accidental API costs.
- RAG-driven explainability: ChromaDB returns policy excerpts to support evidence-based recommendations.
- Async backend with FastAPI + Motor: non-blocking I/O for file uploads and DB operations.
- Frontend-first UX: React + Vite + Tailwind ensures a responsive, themeable dashboard that can be used in demos without backend (mock mode).


## Setup Summary

1. Backend:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# create .env with GEMINI_API_KEY and MONGODB_URI
uvicorn main:app --reload
```

2. Frontend:

```bash
cd frontend
npm install
npm run dev
```

3. Run quick evaluation (optional):

```bash
cd backend
source venv/bin/activate
python evaluation_pipeline.py
```

---