"""FastAPI application initialization."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.routes import auth
from app.api import tasks

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Hackathon Todo API",
    description="Backend API for Phase II Todo Application with Authentication",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://your-vercel-frontend-url.vercel.app",  # baad mein add kar lena
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Hackathon Todo API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
