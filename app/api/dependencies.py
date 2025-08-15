from app.core.config import settings
from app.service.analysis import StreamingCallProcessor
from app.service.azure_speech import AzureSpeechHandler
from app.utils.agent import agent


def get_call_service() -> StreamingCallProcessor:
    return StreamingCallProcessor(agent)


def azure_speech_handler() -> AzureSpeechHandler:
    if settings.AZURE_SPEECH_KEY is None or settings.AZURE_SPEECH_REGION is None:
        raise ValueError(
            "Azure Speech Key and Region must be set in the environment variables."
        )

    return AzureSpeechHandler(
        settings.AZURE_SPEECH_KEY,
        settings.AZURE_SPEECH_REGION,
    )
