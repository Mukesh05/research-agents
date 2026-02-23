import streamlit as st
import requests
import time
from typing import Dict, List, Optional, Any

# Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'job_id' not in st.session_state:
    st.session_state.job_id = None
if 'job_status' not in st.session_state:
    st.session_state.job_status = None

# API Client Functions


def submit_research(query: str, output_formats: List[str], theme: str, include_visualization: bool) -> Optional[Dict]:
    """Submit a research request to the API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/research",
            json={
                "query": query,
                "output_formats": output_formats,
                "theme": theme,
                "include_visualization": include_visualization
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(
            f"❌ Cannot connect to backend at {API_BASE_URL}. Please ensure the API server is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Please try again.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error submitting research: {str(e)}")
        return None


def get_job_status(job_id: str) -> Optional[Dict]:
    """Get the status of a research job."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/research/{job_id}", timeout=10)
        if response.status_code == 404:
            st.error(f"❌ Job {job_id} not found")
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to backend at {API_BASE_URL}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error fetching job status: {str(e)}")
        return None


def download_file(file_url: str) -> Optional[bytes]:
    """Download a file from the API."""
    try:
        # Construct full URL if relative path
        if file_url.startswith('/'):
            full_url = f"{API_BASE_URL}{file_url}"
        else:
            full_url = file_url

        response = requests.get(full_url, timeout=30)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error downloading file: {str(e)}")
        return None


# Streamlit App UI
st.set_page_config(
    page_title="Research Agents",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Research Agents")
st.markdown(
    "AI-powered research assistant that generates comprehensive reports and presentations")

# Research Submission Form
st.header("Submit Research Query")

with st.form("research_form"):
    query = st.text_area(
        "Research Question",
        placeholder="e.g., What are the latest developments in quantum computing?",
        height=100,
        help="Enter your research question or topic. The AI will search and compile information."
    )

    col1, col2 = st.columns(2)

    with col1:
        theme = st.selectbox(
            "Presentation Theme",
            options=["navy-teal", "navy-gold", "charcoal-blue"],
            help="Color theme for PowerPoint presentations"
        )

    with col2:
        output_formats = st.multiselect(
            "Output Formats",
            options=["pdf", "pptx"],
            default=["pdf", "pptx"],
            help="Select which file formats to generate"
        )

    include_visualization = st.checkbox(
        "Include Data Visualizations",
        value=True,
        help="Automatically create charts and visualizations when numerical data is found"
    )

    submitted = st.form_submit_button(
        "Start Research", use_container_width=True, type="primary")

    if submitted:
        if not query.strip():
            st.error("❌ Please enter a research question")
        elif not output_formats:
            st.error("❌ Please select at least one output format")
        else:
            # Submit the research job
            result = submit_research(
                query, output_formats, theme, include_visualization)
            if result:
                st.session_state.job_id = result.get('job_id')
                st.session_state.job_status = None  # Reset status
                st.success(
                    f"✅ Research job submitted! Job ID: {result.get('job_id')}")
                st.rerun()

# Status Polling and Results Display
if st.session_state.job_id:
    st.divider()
    st.header("Research Progress")

    # Fetch current job status
    job_status = get_job_status(st.session_state.job_id)

    if job_status:
        st.session_state.job_status = job_status
        status = job_status.get('status')
        progress_msg = job_status.get('progress')

        # Display status
        if status == 'pending':
            with st.status("⏳ Pending...", expanded=True):
                st.write("Job is queued and waiting to start")
            time.sleep(2)
            st.rerun()

        elif status == 'running':
            with st.status("🔄 Running...", expanded=True):
                if progress_msg:
                    st.write(progress_msg)
                else:
                    st.write("Research in progress...")
            time.sleep(2)
            st.rerun()

        elif status == 'completed':
            st.success("✅ Research Completed!")

            result = job_status.get('result')
            if result:
                # Display topic
                topic = result.get('topic')
                if topic:
                    st.subheader(f"📋 {topic}")

                # Display summary
                summary = result.get('summary')
                if summary:
                    st.markdown("### Summary")
                    st.markdown(summary)

                # Display sources
                sources = result.get('sources', [])
                if sources:
                    st.markdown("### Sources")
                    for i, source in enumerate(sources, 1):
                        if isinstance(source, dict):
                            title = source.get('title', 'Untitled')
                            url = source.get('url', '')
                            if url:
                                st.markdown(f"{i}. [{title}]({url})")
                            else:
                                st.markdown(f"{i}. {title}")
                        else:
                            st.markdown(f"{i}. {source}")

                # Display tools used
                tools_used = result.get('tools_used', [])
                if tools_used:
                    st.caption(f"🛠️ Tools used: {', '.join(tools_used)}")

            # File downloads
            file_urls = job_status.get('file_urls')
            if file_urls:
                st.divider()
                st.markdown("### 📥 Download Files")

                cols = st.columns(len(file_urls))
                for idx, (file_type, file_url) in enumerate(file_urls.items()):
                    with cols[idx]:
                        # Extract filename from URL
                        filename = file_url.split('/')[-1]

                        # Determine mime type
                        mime_type = "application/pdf" if file_type == "pdf" else "application/vnd.openxmlformats-officedocument.presentationml.presentation"

                        # Download file content
                        file_content = download_file(file_url)

                        if file_content:
                            st.download_button(
                                label=f"📄 Download {file_type.upper()}",
                                data=file_content,
                                file_name=filename,
                                mime=mime_type,
                                use_container_width=True
                            )

            # New research button
            st.divider()
            if st.button("Start New Research", use_container_width=True):
                st.session_state.job_id = None
                st.session_state.job_status = None
                st.rerun()

        elif status == 'failed':
            error = job_status.get('error', 'Unknown error occurred')
            st.error(f"❌ Research Failed: {error}")

            # New research button
            st.divider()
            if st.button("Start New Research", use_container_width=True):
                st.session_state.job_id = None
                st.session_state.job_status = None
                st.rerun()

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This research assistant uses AI agents to:
    - 🔍 Search the web for relevant information
    - 📚 Query Wikipedia for authoritative sources
    - 📊 Create data visualizations (when applicable)
    - 📄 Generate PDF reports
    - 🎯 Create PowerPoint presentations
    
    **How to use:**
    1. Enter your research question
    2. Select output preferences
    3. Click "Start Research"
    4. Wait for completion (typically 1-3 minutes)
    5. Download your files
    """)

    st.divider()

    st.markdown(f"**API Status:** {API_BASE_URL}")

    # Health check
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if health_response.status_code == 200:
            st.success("✅ Connected")
        else:
            st.error("❌ Not responding")
    except:
        st.error("❌ Offline")

    st.divider()

    st.caption("Powered by Claude AI & FastAPI")
