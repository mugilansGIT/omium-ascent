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
## API

# 1. Clone and enter directory
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate



## Front-end running

- cd frontend
- npm install
- npm run dev




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



## OMIUM
<img width="2556" height="1365" alt="image" src="https://github.com/user-attachments/assets/28fba7a4-3b35-472f-a685-3e0fcb1a184e" />
<img width="2540" height="1134" alt="image" src="https://github.com/user-attachments/assets/7bebc0e2-5007-459c-8d65-026d920838be" />
<img width="2188" height="649" alt="image" src="https://github.com/user-attachments/assets/5bbf49e8-ac9f-4e67-a4ab-43d8f5a8e977" />

<img width="2548" height="1019" alt="image" src="https://github.com/user-attachments/assets/c080c506-6b78-41ee-ad79-7ac5fe2a6c44" />

---

