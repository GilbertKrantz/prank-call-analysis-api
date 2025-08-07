from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn


from app.api.routes import analyze, health
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Init lifespan context manager
@asynccontextmanager
async def app_lifespan(_: FastAPI):
    # startup
    logger.info("Starting up BIBOT KPI SPEC API")

    yield

    logger.info("Shutting Down BIBOT KPI SPEC API")


# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="BIBOT: Samsung Electronics VD Division Chatbot API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=app_lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(analyze.router, prefix="/ws/v1", tags=["analyze"])


@app.get("/")
async def root():
    """Root endpoint with welcome message."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "docs": "/docs",
        "status": "running",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8080,
        log_level="info",
        reload=True,
        workers=2,
    )
