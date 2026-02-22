"""
Job tracking and management for async research tasks.
"""

import uuid
import asyncio
from typing import Dict, Optional
from datetime import datetime

from models.schemas import (
    JobStatus,
    JobStatusResponse,
    ResearchRequest,
    ResearchResponse
)


class JobManager:
    """
    Manages research job lifecycle with in-memory storage.
    Thread-safe with asyncio locks for concurrent access.
    """

    def __init__(self):
        self._jobs: Dict[str, JobStatusResponse] = {}
        self._lock = asyncio.Lock()

    def create_job(self, request: ResearchRequest) -> str:
        """
        Create a new job and return its ID.

        Args:
            request: The research request parameters

        Returns:
            job_id: UUID string for tracking the job
        """
        job_id = str(uuid.uuid4())

        job = JobStatusResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            progress="Job created, waiting to start",
            result=None,
            file_urls=None,
            error=None
        )

        self._jobs[job_id] = job
        return job_id

    async def get_job(self, job_id: str) -> Optional[JobStatusResponse]:
        """
        Retrieve job status by ID.

        Args:
            job_id: The job identifier

        Returns:
            JobStatusResponse or None if not found
        """
        async with self._lock:
            return self._jobs.get(job_id)

    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: Optional[str] = None,
        result: Optional[ResearchResponse] = None,
        file_urls: Optional[dict] = None,
        error: Optional[str] = None
    ):
        """
        Update job status and metadata.

        Args:
            job_id: The job identifier
            status: New job status
            progress: Progress message
            result: Research result (if completed)
            file_urls: Generated file URLs (if completed)
            error: Error message (if failed)
        """
        async with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].status = status
                if progress is not None:
                    self._jobs[job_id].progress = progress
                if result is not None:
                    self._jobs[job_id].result = result
                if file_urls is not None:
                    self._jobs[job_id].file_urls = file_urls
                if error is not None:
                    self._jobs[job_id].error = error

    async def mark_running(self, job_id: str, progress: str = "Research in progress"):
        """Mark job as running."""
        await self.update_job_status(job_id, JobStatus.RUNNING, progress=progress)

    async def mark_completed(
        self,
        job_id: str,
        result: ResearchResponse,
        file_urls: dict
    ):
        """Mark job as completed with results."""
        await self.update_job_status(
            job_id,
            JobStatus.COMPLETED,
            progress="Research completed successfully",
            result=result,
            file_urls=file_urls
        )

    async def mark_failed(self, job_id: str, error: str):
        """Mark job as failed with error message."""
        await self.update_job_status(
            job_id,
            JobStatus.FAILED,
            progress="Job failed",
            error=error
        )

    def list_jobs(self) -> Dict[str, JobStatusResponse]:
        """Get all jobs (for debugging/admin purposes)."""
        return self._jobs.copy()


# Global job manager instance
job_manager = JobManager()
