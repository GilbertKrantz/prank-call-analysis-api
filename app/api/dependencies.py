from app.service.analysis import StreamingCallProcessor
from app.utils.agent import agent


def get_call_service() -> StreamingCallProcessor:
    return StreamingCallProcessor(agent)
