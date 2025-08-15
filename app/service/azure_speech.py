import asyncio
import uuid
from datetime import datetime
import azure.cognitiveservices.speech as speechsdk
from app.models.call import StreamingCallChunk


class AzureSpeechHandler:
    def __init__(self, speech_key: str, speech_region: str, language: str = "id-ID"):
        self.speech_key = speech_key
        self.speech_region = speech_region
        self.language = language

    def create_push_stream(self):
        """Create an Azure PushAudioInputStream to send PCM audio bytes."""
        return speechsdk.audio.PushAudioInputStream()

    def create_recognizer(self, audio_stream):
        """Create a SpeechRecognizer bound to the given audio stream."""
        speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key, region=self.speech_region
        )
        speech_config.speech_recognition_language = self.language
        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
        return speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_config
        )

    async def stream_audio_to_processor(self, call_id: str, processor, websocket):
        loop = asyncio.get_running_loop()  # main asyncio loop

        audio_stream = self.create_push_stream()
        recognizer = self.create_recognizer(audio_stream)

        def recognizing_handler(evt):
            if evt.result.text.strip():
                chunk = StreamingCallChunk(
                    call_id=call_id,
                    chunk_id=str(uuid.uuid4()),
                    audio_chunk=evt.result.text,
                    timestamp=datetime.now().isoformat(),
                    is_final=False,
                )
                loop.call_soon_threadsafe(
                    asyncio.create_task,
                    self._process_and_send(processor, chunk, websocket),
                )

        def recognized_handler(evt):
            if evt.result.text.strip():
                chunk = StreamingCallChunk(
                    call_id=call_id,
                    chunk_id=str(uuid.uuid4()),
                    audio_chunk=evt.result.text,
                    timestamp=datetime.now().isoformat(),
                    is_final=True,
                )
                loop.call_soon_threadsafe(
                    asyncio.create_task,
                    self._process_and_send(processor, chunk, websocket),
                )

        recognizer.recognizing.connect(recognizing_handler)
        recognizer.recognized.connect(recognized_handler)

        recognizer.start_continuous_recognition_async()

        try:
            while True:
                audio_bytes = await websocket.receive_bytes()
                audio_stream.write(audio_bytes)
        except Exception:
            pass
        finally:
            audio_stream.close()
            recognizer.stop_continuous_recognition_async()

    async def _process_and_send(self, processor, chunk, websocket):
        update = await processor.process_chunk(chunk)
        await websocket.send_json(update.dict())
