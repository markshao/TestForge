from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

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

# Mount screenshots directory
screenshots_dir = os.path.join(os.getcwd(), "screenshots")
if not os.path.exists(screenshots_dir):
    os.makedirs(screenshots_dir)
app.mount("/screenshots", StaticFiles(directory=screenshots_dir), name="screenshots")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
