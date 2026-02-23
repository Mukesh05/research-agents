@echo off
REM Launch script for Streamlit frontend on Windows

echo Starting Streamlit frontend on http://localhost:8501
streamlit run frontend/streamlit_app.py --server.port 8501
