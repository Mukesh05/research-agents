"""
Research Agent API Server
FastAPI-based async research assistant with PDF/PPTX generation.
"""

import uvicorn


def main():
    """Main entry point - Launch FastAPI server."""
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
