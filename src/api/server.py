"""FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Code Reviewer",
    version="0.1.0",
    description="AI-powered code review automation"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "status": "ok",
        "name": "AI Code Reviewer",
        "version": "0.1.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/v1/info")
async def info():
    """API information."""
    return {
        "name": "AI Code Reviewer API",
        "version": "0.1.0",
        "endpoints": ["/", "/health", "/api/v1/info"]
    }
