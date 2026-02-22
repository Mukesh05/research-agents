# Plan: FastAPI endpoint with async job tracking

Transform the CLI research assistant into an async REST API using FastAPI. The API will accept research queries with output preferences, track job progress, and serve generated PDF/PPTX files via download URLs.

**Key decisions:**
- **Async job tracking**: Prevents timeout on long-running research (30-60s)
- **Rich payload**: User controls output formats, theme, and visualization preferences
- **Replace CLI**: Single API interface instead of maintaining both
- **File serving**: Static file endpoint for downloading generated outputs

**Steps**

1. **Add FastAPI dependencies** to [requirements.txt](requirements.txt)
   - Add `fastapi>=0.115.0`, `uvicorn[standard]>=0.30.0`, `python-multipart>=0.0.9`

2. **Create request/response models** in [models/schemas.py](models/schemas.py)
   - Add `ResearchRequest` with fields: `query`, `output_formats`, `theme`, `include_visualization`
   - Add `JobSubmitResponse` with: `job_id`, `status`, `message`
   - Add `JobStatusResponse` with: `job_id`, `status`, `progress`, `result`, `file_urls`, `error`
   - Add `JobStatus` enum: `pending`, `running`, `completed`, `failed`

3. **Create job tracking system** as new file [api/job_manager.py](api/job_manager.py)
   - In-memory dict to store job state (job_id → JobStatusResponse)
   - UUID-based job ID generation
   - Thread-safe access with asyncio locks
   - Background task executor using `asyncio.create_task()`

4. **Create FastAPI application** as new file [api/server.py](api/server.py)
   - Initialize FastAPI app with CORS middleware
   - `POST /api/research` - Submit research job, return job_id immediately
   - `GET /api/research/{job_id}` - Poll job status and retrieve results
   - `GET /api/outputs/{filename}` - Serve PDF/PPTX files from [output/](output/) directory
   - Background task to run research agent and update job status

5. **Refactor research logic** in [agents/research_agent.py](agents/research_agent.py)
   - Extract agent execution into standalone async function `run_research_async()`
   - Accept `ResearchRequest` instead of CLI args
   - Return file paths in addition to `ResearchResponse`
   - Add error handling with detailed messages for API consumption

6. **Update main entry point** in [main.py](main.py)
   - Remove CLI argument parsing
   - Replace with uvicorn server launcher: `uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)`

7. **Create API directory structure**
   - New directory `api/` with `__init__.py`, `server.py`, `job_manager.py`

**Verification**

Run the server:
```bash
python main.py
```

Test endpoints:
```bash
# Submit job
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What is quantum computing?", "output_formats": ["pdf", "pptx"], "theme": "navy-teal"}'

# Check status (use job_id from above)
curl http://localhost:8000/api/research/{job_id}

# Download file (use filename from status response)
curl http://localhost:8000/api/outputs/{filename} --output report.pdf
```

Visit API docs: `http://localhost:8000/docs`

**Decisions**
- **Async over sync**: Research queries take 30-60s; async prevents timeout and allows concurrent jobs
- **In-memory job storage**: Simplest for MVP; can migrate to Redis/DB later if persistence needed
- **Replace CLI**: Single interface reduces maintenance; API is more flexible
- **Static file serving**: Direct file downloads via FastAPI's `FileResponse` instead of base64 encoding
