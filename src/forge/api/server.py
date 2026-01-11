from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import tasks

app = FastAPI(
    title="TestForge API",
    description="API for TestForge Autonomous Testing Agent",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
