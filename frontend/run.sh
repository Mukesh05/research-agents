#!/bin/bash
# Launch script for Streamlit frontend

echo "Starting Streamlit frontend on http://localhost:8501"
streamlit run frontend/streamlit_app.py --server.port 8501
