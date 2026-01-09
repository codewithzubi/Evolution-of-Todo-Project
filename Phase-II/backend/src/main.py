from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.auth import router as auth_router
from .api.tasks import router as tasks_router
from .database.connection import engine
from .models.user import User
from .models.task import Task
from sqlmodel import SQLModel
import os

# Create tables
SQLModel.metadata.create_all(bind=engine)

app = FastAPI(
    title="Phase II Full-Stack Todo API",
    description="API for the Full-Stack Web Todo Application with Glassmorphism UI",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://localhost:3006",
        "http://localhost:3007",
        "http://localhost:3008",
        "http://localhost:3009",
        "http://localhost:30010",
        "http://localhost:30011",
        "http://localhost:30012",
        "http://localhost:30013",
        "http://localhost:30014",
        "http://localhost:30015",
        "http://localhost:30016",
        "http://localhost:30017",
        "http://localhost:30018",
        "http://localhost:30019",
        "http://localhost:30020"
    ],  # Allow Next.js dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Phase II Full-Stack Todo API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)