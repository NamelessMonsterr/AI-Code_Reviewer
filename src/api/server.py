"""FastAPI application."""
from fastapi import FastAPI

app = FastAPI(title="AI Code Reviewer", version="0.1.0")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "status": "ok",
        "name": "AI Code Reviewer",
        "version": "0.1.0"
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}
