"""
Scheduler for periodic monitoring tasks.
"""
import asyncio
from typing import Dict, Callable, Any
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from app.core.config import settings


class MonitoringScheduler:
    """Scheduler for running periodic monitoring tasks."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs: Dict[str, Callable] = {}
    
    def add_job(
        self,
        job_id: str,
        func: Callable,
        trigger: str = "interval",
        seconds: int = None,
        minutes: int = None,
        hours: int = None,
        **kwargs
    ):
        """Add a job to the scheduler."""
        trigger_config = {}
        
        if trigger == "interval":
            if seconds:
                trigger_config["seconds"] = seconds
            elif minutes:
                trigger_config["minutes"] = minutes
            elif hours:
                trigger_config["hours"] = hours
            else:
                trigger_config["seconds"] = settings.monitoring_interval_seconds
            
            trigger_obj = IntervalTrigger(**trigger_config)
        else:
            raise ValueError(f"Unsupported trigger type: {trigger}")
        
        job = self.scheduler.add_job(
            func,
            trigger=trigger_obj,
            id=job_id,
            replace_existing=True,
            **kwargs
        )
        
        self.jobs[job_id] = func
        logger.info(f"Added job {job_id} with interval: {trigger_config}")
        
        return job
    
    def remove_job(self, job_id: str):
        """Remove a job from the scheduler."""
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.jobs:
                del self.jobs[job_id]
            logger.info(f"Removed job {job_id}")
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")
    
    def get_job(self, job_id: str):
        """Get a job by ID."""
        return self.scheduler.get_job(job_id)
    
    def list_jobs(self):
        """List all scheduled jobs."""
        return self.scheduler.get_jobs()
    
    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Monitoring scheduler started")
    
    def shutdown(self, wait: bool = True):
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("Monitoring scheduler stopped")
    
    def pause(self):
        """Pause all jobs."""
        self.scheduler.pause()
        logger.info("Monitoring scheduler paused")
    
    def resume(self):
        """Resume all jobs."""
        self.scheduler.resume()
        logger.info("Monitoring scheduler resumed")


# Global scheduler instance
scheduler = MonitoringScheduler()


def get_scheduler() -> MonitoringScheduler:
    """Get the global scheduler instance."""
    return scheduler
