"""
FastAPI server for research agent API.
"""

import asyncio
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import (
    ResearchRequest,
    JobSubmitResponse,
    JobStatusResponse,
    JobStatus
)
from .job_manager import job_manager
from agents.research_agent import run_research_async


# Initialize FastAPI app
app = FastAPI(
    title="Research Agent API",
    description="Async API for AI-powered research with PDF/PPTX generation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Output directory for generated files
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


async def process_research_job(job_id: str, request: ResearchRequest):
    """
    Background task to process research request.

    Args:
        job_id: The job identifier
        request: Research request parameters
    """
    try:
        # Mark job as running
        await job_manager.mark_running(
            job_id,
            progress=f"Processing research query: {request.query[:50]}..."
        )

        # Execute research agent
        result = await run_research_async(request)

        # Generate file URLs based on what was created
        file_urls = {}

        if result.get("pdf_path"):
            filename = Path(result["pdf_path"]).name
            file_urls["pdf"] = f"/api/outputs/{filename}"

        if result.get("pptx_path"):
            filename = Path(result["pptx_path"]).name
            file_urls["pptx"] = f"/api/outputs/{filename}"

        if result.get("visualization_path"):
            filename = Path(result["visualization_path"]).name
            file_urls["visualization"] = f"/api/outputs/{filename}"

        # Mark job as completed
        await job_manager.mark_completed(
            job_id,
            result=result["response"],
            file_urls=file_urls
        )

    except Exception as e:
        # Mark job as failed
        error_msg = f"Research failed: {str(e)}"
        await job_manager.mark_failed(job_id, error_msg)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Research Agent API",
        "version": "1.0.0",
        "endpoints": {
            "submit_research": "POST /api/research",
            "check_status": "GET /api/research/{job_id}",
            "download_file": "GET /api/outputs/{filename}",
            "docs": "GET /docs"
        }
    }


@app.post("/api/research", response_model=JobSubmitResponse)
async def submit_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit a research job for async processing.

    Args:
        request: Research request with query and preferences
        background_tasks: FastAPI background tasks

    Returns:
        JobSubmitResponse with job_id for tracking
    """
    # Create job
    job_id = job_manager.create_job(request)

    # Add background task
    background_tasks.add_task(process_research_job, job_id, request)

    return JobSubmitResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message=f"Research job submitted successfully. Use job_id to check status."
    )


@app.get("/api/research/{job_id}", response_model=JobStatusResponse)
async def get_research_status(job_id: str):
    """
    Check the status of a research job.

    Args:
        job_id: The job identifier

    Returns:
        JobStatusResponse with current status and results (if completed)

    Raises:
        HTTPException: If job not found
    """
    job = await job_manager.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )

    return job


@app.get("/api/outputs/{filename}")
async def download_file(filename: str):
    """
    Download a generated output file (PDF, PPTX, etc.).

    Args:
        filename: Name of the file to download

    Returns:
        FileResponse with the requested file

    Raises:
        HTTPException: If file not found
    """
    file_path = OUTPUT_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File {filename} not found"
        )

    # Determine media type based on extension
    media_types = {
        ".pdf": "application/pdf",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }

    media_type = media_types.get(file_path.suffix, "application/octet-stream")

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename
    )


@app.get("/api/jobs")
async def list_all_jobs():
    """
    List all jobs (for debugging/admin).

    Returns:
        Dictionary of all jobs
    """
    return {"jobs": job_manager.list_jobs()}


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "research-agent-api"}
