"""
FastAPI backend for research agent.
"""

from .server import app
from .job_manager import JobManager

__all__ = ["app", "JobManager"]
