from fastapi import APIRouter, Depends, HTTPException, status
from app.models.call import StreamingCallChunk
from app.service.analysis import StreamingCallProcessor
from app.api.dependencies import get_call_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "call-analysis-service",
        "version": "1.0.0",
    }


@router.get("/health/detailed")
async def detailed_health_check(
    call_processor: StreamingCallProcessor = Depends(get_call_service),
):
    """Detailed health check with service status."""
    health_status = {
        "status": "healthy",
        "service": "call-analysis-service",
        "version": "1.0.0",
        "components": {},
    }

    # Check call processor/service health
    try:
        # Perform a simple test to verify the service is working
        test_chunk = StreamingCallChunk(
            session_id="health-check",
            chunk_id="test",
            content="test",
            is_final=False,
            timestamp=0,
        )
        _ = await call_processor.process_chunk(test_chunk)
        health_status["components"]["call_processor"] = {
            "status": "healthy",
        }
    except Exception as e:
        logger.error(f"Call processor health check failed: {e}")
        health_status["components"]["call_processor"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        health_status["status"] = "unhealthy"

    # Return appropriate status code
    if health_status["status"] == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=health_status
        )

    return health_status


@router.get("/health/ready")
async def readiness_check(
    call_processor: StreamingCallProcessor = Depends(get_call_service),
):
    """Readiness check for Kubernetes."""
    try:
        # Quick test of essential service
        test_chunk = StreamingCallChunk(
            session_id="readiness-check",
            chunk_id="test",
            content="test",
            is_final=False,
            timestamp=0,
        )
        _ = await call_processor.process_chunk(test_chunk)
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not ready", "error": str(e)},
        )


@router.get("/health/live")
async def liveness_check():
    """Liveness check for Kubernetes."""
    return {"status": "alive"}
