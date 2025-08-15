import logging
import json
from fastapi import APIRouter, Depends, WebSocket

from app.api.dependencies import get_call_service, azure_speech_handler
from app.models.call import StreamingCallChunk
from app.service.analysis import StreamingCallProcessor
from app.service.azure_speech import AzureSpeechHandler

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket(path="/analyze-call-stream")
async def call_analysis_endpoint(
    websocket: WebSocket,
    call_processor: StreamingCallProcessor = Depends(get_call_service),
):
    """WebSocket endpoint for streaming call analysis"""
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


@router.websocket("/call/{call_id}")
async def ws_call(
    websocket: WebSocket,
    call_id: str,
    call_processor: StreamingCallProcessor = Depends(get_call_service),
    speech_handler: AzureSpeechHandler = Depends(azure_speech_handler),
):
    await websocket.accept()
    await speech_handler.stream_audio_to_processor(call_id, call_processor, websocket)
