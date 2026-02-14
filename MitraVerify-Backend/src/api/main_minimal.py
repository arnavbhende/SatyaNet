"""
Minimal FastAPI Application for MitraVerify - Without ML Dependencies
"""
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="MitraVerify API",
    description="AI-powered misinformation detection system for Indian digital ecosystem",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to MitraVerify API",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "Running in minimal mode without ML components"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.1.0"}

@app.get("/api/v1/health")
async def api_health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-06-17T00:00:00Z",
        "version": "0.1.0"
    }

@app.post("/api/v1/analyze")
async def analyze_content():
    """Mock analyze endpoint - returns demo response"""
    return {
        "overall_verdict": "pending",
        "confidence": 0.5,
        "analysis": {
            "text_analysis": {
                "prediction": "neutral",
                "confidence": 0.5,
                "explanation": "ML components not loaded - running in demo mode"
            },
            "image_analysis": None,
            "evidence": []
        },
        "message": "Running in minimal mode - ML components not available"
    }

def main():
    """Main entry point for running the server"""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
