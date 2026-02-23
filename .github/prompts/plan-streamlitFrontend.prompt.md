# Plan: Streamlit Frontend for Research Agents API

Building a web UI for the FastAPI research backend that allows users to submit queries, monitor job progress with auto-refresh, and download generated PDF/PPTX reports. The frontend will connect to http://localhost:8000, track a single active job using Streamlit session state, and poll status every 2-3 seconds until completion.

**Steps**

1. **Create frontend structure**
   - Add [frontend/streamlit_app.py](frontend/streamlit_app.py) as main UI entrypoint
   - Organize with sections: research form → status tracking → results display → file downloads

2. **Add Streamlit dependencies**
   - Update [requirements.txt](requirements.txt) to include `streamlit>=1.30.0` and `requests>=2.31.0`

3. **Implement API client functions**
   - Create helper functions in [frontend/streamlit_app.py](frontend/streamlit_app.py):
     - `submit_research(query, output_formats, theme, include_visualization)` → POST to `/api/research`
     - `get_job_status(job_id)` → GET from `/api/research/{job_id}`
     - `download_file(file_url)` → GET from file URLs for `st.download_button`

4. **Build research submission form**
   - Use `st.form` with:
     - `st.text_area` for query input (required, placeholder with example query)
     - `st.selectbox` for theme (navy-teal, navy-gold, charcoal-blue)
     - `st.multiselect` for output formats (pdf, pptx, both selected by default)
     - `st.checkbox` for include_visualization (default: True)
     - Submit button → calls `submit_research()` → stores `job_id` in `st.session_state`

5. **Implement status polling with auto-refresh**
   - Check `st.session_state.job_id` exists and status is "pending" or "running"
   - Display `st.status` component with current progress message
   - Call `time.sleep(2)` then `st.rerun()` to auto-refresh every 2 seconds
   - Stop polling when status becomes "completed" or "failed"

6. **Display research results**
   - When status is "completed", show:
     - `st.success` message with topic
     - `st.markdown` with summary text
     - `st.subheader` + bullet list of sources with clickable URLs
     - `st.caption` showing tools_used (search, wiki, visualization, etc.)
   - When status is "failed", show `st.error` with error message

7. **Add file download buttons**
   - Parse `file_urls` from job response (dict with pdf/pptx keys)
   - For each available file:
     - Fetch file bytes using `download_file(url)`
     - Create `st.download_button` with appropriate filename and mime type
     - Use columns layout (`st.columns`) for side-by-side PDF/PPTX buttons

8. **Initialize session state**
   - Add initialization block at top of script:
     - `st.session_state.job_id = None` (current job)
     - `st.session_state.job_status = None` (cached status object)
   - Clear job_id on new form submission

9. **Add error handling**
   - Wrap API calls in try/except blocks
   - Display `st.error` for connection errors, 404s, or API failures
   - Show user-friendly messages (e.g., "Backend not running at http://localhost:8000")

10. **Create launch script** [frontend/run.sh](frontend/run.sh) (optional)
    - Bash script: `streamlit run frontend/streamlit_app.py --server.port 8501`
    - Add Windows equivalent [frontend/run.bat](frontend/run.bat)

11. **Update documentation**
    - Add section to [README.md](README.md) with:
      - Installation: `pip install -r requirements.txt`
      - Backend startup: `python main.py` (port 8000)
      - Frontend startup: `streamlit run frontend/streamlit_app.py` (port 8501)
      - Usage instructions with screenshots/examples

**Verification**
- Start backend: `python main.py` → verify runs on http://localhost:8000
- Start frontend: `streamlit run frontend/streamlit_app.py` → opens browser at http://localhost:8501
- Submit test query → verify status auto-refreshes every 2 seconds
- Wait for completion → verify summary/sources display
- Click download buttons → verify PDF/PPTX files download correctly
- Test error handling → stop backend, submit query → verify friendly error message

**Decisions**
- **Backend URL**: Hardcoded to `http://localhost:8000` for simplicity (can be made configurable later with environment variables)
- **Job Tracking**: Single active job only (simpler UX, no history persistence needed)
- **Polling Strategy**: 2-second intervals with `st.rerun()` (balances responsiveness vs backend load)
- **File Structure**: Frontend in dedicated `/frontend` directory to separate concerns from FastAPI backend
