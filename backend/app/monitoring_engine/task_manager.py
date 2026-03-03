"""
Task manager for coordinating monitoring tasks.
"""
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

from app.monitoring_engine.scheduler import get_scheduler
from app.monitoring_engine.health_checker import run_health_check, close_global_http_client
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
        
        # Add periodic health check job - use sync wrapper for APScheduler
        self.scheduler.add_job(
            job_id=self.HEALTH_CHECK_JOB_ID,
            func=self._run_health_check_sync_wrapper,
            trigger="interval",
            seconds=settings.monitoring_interval_seconds,
            name="Health Check All Endpoints"
        )
        
        self.is_running = True
        logger.info(f"Monitoring started with interval {settings.monitoring_interval_seconds} seconds")
        
        # Run initial health check immediately
        await self._run_health_check_wrapper()
    
    async def stop_monitoring(self):
        """Stop the monitoring tasks."""
        if not self.is_running:
            logger.warning("Monitoring is not running")
            return
        
        # Remove health check job
        try:
            self.scheduler.remove_job(self.HEALTH_CHECK_JOB_ID)
        except Exception as e:
            logger.warning(f"Error removing job: {e}")
        
        # Shutdown scheduler with error handling for event loop issues
        try:
            self.scheduler.shutdown(wait=True)
        except Exception as e:
            logger.warning(f"Error shutting down scheduler: {e}")
        
        # Close global HTTP client with event loop check
        try:
            # Check if event loop is running before trying to close
            try:
                loop = asyncio.get_running_loop()
                # If we can get here, there's a running loop
                await close_global_http_client()
            except RuntimeError:
                # No running event loop - use asyncio.run for cleanup
                try:
                    asyncio.run(close_global_http_client())
                except Exception as e2:
                    logger.warning(f"Error closing HTTP client (asyncio.run): {e2}")
        except Exception as e:
            logger.warning(f"Error closing HTTP client: {e}")
        
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
            logger.debug("Running health check...")
            result = await run_health_check()
            logger.debug(f"Health check result: {result}")
        except Exception as e:
            logger.error(f"Error running health check: {e}", exc_info=True)
    
    def _run_health_check_sync_wrapper(self):
        """Sync wrapper for APScheduler to call async function."""
        try:
            # Get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running (e.g., in uvicorn), use create_task
                asyncio.create_task(self._run_health_check_wrapper())
            else:
                # If no loop running, run the coroutine
                loop.run_until_complete(self._run_health_check_wrapper())
        except RuntimeError as e:
            # Handle case where there's no event loop
            logger.warning(f"Could not get event loop: {e}")
            try:
                asyncio.run(self._run_health_check_wrapper())
            except Exception as e2:
                logger.error(f"Failed to run health check: {e2}")
    
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
            try:
                self.scheduler.remove_job(self.HEALTH_CHECK_JOB_ID)
            except Exception as e:
                logger.warning(f"Error removing job: {e}")
            
            # Add new job with updated interval
            self.scheduler.add_job(
                job_id=self.HEALTH_CHECK_JOB_ID,
                func=self._run_health_check_sync_wrapper,
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
