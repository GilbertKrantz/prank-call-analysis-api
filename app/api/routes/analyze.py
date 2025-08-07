import logging
import json
from fastapi import APIRouter, WebSocket

from app.api.dependencies import get_call_service
from app.models.call import StreamingCallChunk

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket(path="/ws/analyze-call-stream")
async def call_analysis_endpoint(websocket: WebSocket):
    """WebSocket endpoint for streaming call analysis"""
    call_processor = get_call_service()
    await websocket.accept()

    try:
        while True:
            # Receive chunk data
            data = await websocket.receive_text()
            chunk_data = json.loads(data)
            chunk = StreamingCallChunk(**chunk_data)

            # Process the chunk
            analysis_update = await call_processor.process_chunk(chunk)

            # Send analysis update
            await websocket.send_text(analysis_update.json())

            # If final chunk, close connection
            if chunk.is_final:
                await websocket.close()
                break

    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()
