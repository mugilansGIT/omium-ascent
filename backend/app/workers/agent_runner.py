import asyncio
import logging
from app.agents.orchestrator import OrchestratorAgent
from app.agents.hr_agent import HRAgent
from app.agents.task_agent import TaskAgent
from app.agents.notification_agent import NotificationAgent

logger = logging.getLogger(__name__)


class AgentRunner:
    def __init__(self):
        self.agents = {
            "orchestrator": OrchestratorAgent(),
            "hr_agent": HRAgent(),
            "task_agent": TaskAgent(),
            "notification_agent": NotificationAgent(),
        }
        self._tasks: list[asyncio.Task] = []

    async def start_all(self):
        logger.info("Starting all agents...")
        for name, agent in self.agents.items():
            task = asyncio.create_task(agent.start(), name=name)
            self._tasks.append(task)

    async def stop_all(self):
        for agent in self.agents.values():
            await agent.stop()
        for task in self._tasks:
            task.cancel()

    def get_status(self) -> dict:
        return {name: agent.running for name, agent in self.agents.items()}

    def get_orchestrator(self) -> OrchestratorAgent:
        return self.agents["orchestrator"]
