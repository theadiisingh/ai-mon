"""
Task manager for coordinating monitoring tasks.
"""
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

from app.monitoring_engine.scheduler import get_scheduler
from app.monitoring_engine.health_checker import run_health_check
from app.core.config import settings
from loguru import logger


class TaskManager:
    """Manager for monitoring tasks."""
    
    # Job IDs
    HEALTH_CHECK_JOB_ID = "health_check_all"
    
    def __init__(self):
        self.scheduler = get_scheduler()
        self.is_running = False
    
    async def start_monitoring(self):
        """Start the monitoring tasks."""
        if self.is_running:
            logger.warning("Monitoring is already running")
            return
        
        # Start the scheduler
        self.scheduler.start()
        
        # Add periodic health check job
        self.scheduler.add_job(
            job_id=self.HEALTH_CHECK_JOB_ID,
            func=self._run_health_check_wrapper,
            trigger="interval",
            seconds=settings.monitoring_interval_seconds,
            name="Health Check All Endpoints"
        )
        
        self.is_running = True
        logger.info("Monitoring started")
    
    async def stop_monitoring(self):
        """Stop the monitoring tasks."""
        if not self.is_running:
            logger.warning("Monitoring is not running")
            return
        
        # Remove health check job
        self.scheduler.remove_job(self.HEALTH_CHECK_JOB_ID)
        
        # Shutdown scheduler
        self.scheduler.shutdown()
        
        self.is_running = False
        logger.info("Monitoring stopped")
    
    async def restart_monitoring(self):
        """Restart the monitoring tasks."""
        await self.stop_monitoring()
        await asyncio.sleep(1)  # Give time for cleanup
        await self.start_monitoring()
        logger.info("Monitoring restarted")
    
    async def _run_health_check_wrapper(self):
        """Wrapper for running health checks."""
        try:
            await run_health_check(None)
        except Exception as e:
            logger.error(f"Error running health check: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get the status of monitoring tasks."""
        jobs = self.scheduler.list_jobs()
        
        return {
            "is_running": self.is_running,
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in jobs
            ]
        }
    
    def update_health_check_interval(self, seconds: int):
        """Update the health check interval."""
        if self.is_running:
            # Remove existing job
            self.scheduler.remove_job(self.HEALTH_CHECK_JOB_ID)
            
            # Add new job with updated interval
            self.scheduler.add_job(
                job_id=self.HEALTH_CHECK_JOB_ID,
                func=self._run_health_check_wrapper,
                trigger="interval",
                seconds=seconds,
                name="Health Check All Endpoints"
            )
            
            logger.info(f"Health check interval updated to {seconds} seconds")
        else:
            logger.warning("Cannot update interval - monitoring not running")


# Global task manager instance
task_manager = TaskManager()


def get_task_manager() -> TaskManager:
    """Get the global task manager instance."""
    return task_manager
