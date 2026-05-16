# AI Ops Platform — Backend

Multi-agent AI orchestration system for autonomous company operations & procurement.

## Stack
- **FastAPI** — async Python backend
- **Supabase** — PostgreSQL + realtime + auth
- **Redis (Upstash)** — event bus (Redis Streams)
- **Google Gemini 1.5 Flash** — AI reasoning
- **Render** — deployment

## Quick Start

```bash
# 1. Clone and enter directory
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your keys

# 5. Run
uvicorn app.main:app --reload
```

API docs available at: http://localhost:8000/docs

## Agent Architecture

```
Orchestrator
├── HR Agent           — leave requests, onboarding
├── Task Agent         — overdue tasks, assignments
├── Meeting Agent      — transcript summarization, action items
├── Trend Agent        — internet trend intelligence
├── Vendor Agent       — vendor scoring & recommendation
├── Procurement Agent  — PO drafting, vendor emails
└── Notification Agent — email + in-app notifications
```

## Environment Variables

See `.env.example` for all required variables.


