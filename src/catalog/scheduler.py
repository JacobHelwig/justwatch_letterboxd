"""Background scheduler for Netflix catalog sync"""

import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Optional

from .manager import CatalogManager

logger = logging.getLogger(__name__)


class CatalogScheduler:
    """Manages scheduled Netflix catalog synchronization"""
    
    def __init__(self, catalog_manager: Optional[CatalogManager] = None):
        """Initialize scheduler with catalog manager
        
        Args:
            catalog_manager: CatalogManager instance for syncing
        """
        self.catalog_manager = catalog_manager or CatalogManager()
        self.scheduler = AsyncIOScheduler()
        self._sync_job = None
    
    def start(self):
        """Start the scheduler with daily 2 AM sync job"""
        # Add daily sync job at 2 AM
        self._sync_job = self.scheduler.add_job(
            self._run_sync,
            trigger=CronTrigger(hour=2, minute=0),
            id='netflix_catalog_sync',
            name='Daily Netflix Catalog Sync',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Catalog scheduler started - daily sync at 2:00 AM")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Catalog scheduler stopped")
    
    async def _run_sync(self):
        """Run catalog sync job (called by scheduler)"""
        try:
            logger.info("Starting scheduled Netflix catalog sync")
            start_time = datetime.now()
            
            stats = await self.catalog_manager.sync_netflix_catalog()
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Scheduled sync complete: {stats['new']} new, "
                f"{stats['removed']} removed, {stats['matched']} matched, "
                f"{stats['missing']} missing ({elapsed:.1f}s)"
            )
            
        except Exception as e:
            logger.error(f"Scheduled sync failed: {e}", exc_info=True)
    
    async def run_sync_now(self) -> dict:
        """Manually trigger a sync immediately
        
        Returns:
            Dict with sync statistics
        """
        logger.info("Manual sync triggered")
        return await self.catalog_manager.sync_netflix_catalog()
    
    def get_next_run_time(self) -> Optional[datetime]:
        """Get next scheduled sync time
        
        Returns:
            Datetime of next sync or None if not scheduled
        """
        if self._sync_job:
            return self._sync_job.next_run_time
        return None
    
    def get_status(self) -> dict:
        """Get scheduler status
        
        Returns:
            Dict with scheduler status and next run time
        """
        return {
            'running': self.scheduler.running,
            'next_run_time': self.get_next_run_time(),
            'job_id': self._sync_job.id if self._sync_job else None
        }
