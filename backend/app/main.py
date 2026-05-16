import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.v1 import auth, employees, tasks, leaves, reports, webhooks, demo
from app.workers.agent_runner import AgentRunner
from app.workers.cron_jobs import setup_cron_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)
settings = get_settings()

import omium
import os
from dotenv import load_dotenv
load_dotenv()  # Ensure .env is loaded before reading OMIUM_API_KEY
try:
    api_key = os.getenv("OMIUM_API_KEY")
    if api_key:
        omium.init(api_key=api_key, project="ai-ops-platform")
        logger.info("Omium tracing initialized successfully!")
    else:
        logger.warning("Omium initialization skipped: OMIUM_API_KEY not found in environment")
except Exception as e:
    logger.error(f"Omium initialization failed: {e}")

agent_runner: AgentRunner = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_runner
    agent_runner = AgentRunner()
    asyncio.create_task(agent_runner.start_all())
    setup_cron_jobs(agent_runner)
    logger.info("All agents started")
    yield
    await agent_runner.stop_all()
    logger.info("All agents stopped")


app = FastAPI(
    title="AI Ops Platform API",
    version="1.0.0",
    description="AI-powered autonomous company operations & procurement system",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,         prefix="/api/v1/auth",         tags=["auth"])
app.include_router(employees.router,    prefix="/api/v1/employees",    tags=["employees"])
app.include_router(tasks.router,        prefix="/api/v1/tasks",        tags=["tasks"])
app.include_router(leaves.router,       prefix="/api/v1/leaves",       tags=["leaves"])
app.include_router(reports.router,      prefix="/api/v1/reports",      tags=["reports"])
app.include_router(webhooks.router,     prefix="/api/v1/webhooks",     tags=["webhooks"])
app.include_router(demo.router,         prefix="/api/v1/demo",         tags=["demo"])


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "agents": agent_runner.get_status() if agent_runner else {}
    }


@app.get("/")
async def root():
    return {"message": "AI Ops Platform API", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
