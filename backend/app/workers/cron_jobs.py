from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)


def setup_cron_jobs(agent_runner):
    scheduler = AsyncIOScheduler()
    orchestrator = agent_runner.get_orchestrator()

    # Daily at 9AM IST
    scheduler.add_job(
        orchestrator.trigger_daily_tasks,
        CronTrigger(hour=9, minute=0, timezone="Asia/Kolkata"),
        id="daily_tasks"
    )

    # Every hour - check overdue tasks
    scheduler.add_job(
        orchestrator._check_overdue_tasks,
        CronTrigger(minute=0),
        id="overdue_check"
    )

    # Every Monday 8AM - weekly trend scan
    scheduler.add_job(
        lambda: orchestrator.publish("trend:scan_requested", {"trigger": "weekly_cron"}),
        CronTrigger(day_of_week="mon", hour=8, timezone="Asia/Kolkata"),
        id="weekly_trend_scan"
    )

    scheduler.start()
    logger.info("Cron jobs scheduled")
