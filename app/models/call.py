from typing import List, Optional
from pydantic import BaseModel, Field


class PrankCallAnalysis(BaseModel):
    """Output model for prank call classification"""

    is_prank_call: bool = Field(
        ..., description="Whether the call is classified as a prank call"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for the classification (0.0 to 1.0)",
    )
    trust_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Trust score of the caller based on historical data (0.0 to 1.0)",
    )
    location: str = Field(..., description="Location extracted from the call")
    reasoning: str = Field(
        ...,
        description="Explanation of why the call was classified as prank or legitimate",
    )
    key_indicators: List[str] = Field(
        ..., description="Key phrases or behaviors that influenced the decision"
    )
    suggestion: str = Field(
        ..., description="Action recommendation for emergency services"
    )
    escalation_required: bool = Field(
        ..., description="Whether the call requires immediate human review"
    )


class StreamingCallChunk(BaseModel):
    """Model for individual chunks of streaming call data"""

    call_id: str
    chunk_id: str
    audio_chunk: Optional[str]  # Base64 encoded audio or text transcription
    timestamp: str
    is_final: bool = False  # Indicates if this is the final chunk


class StreamingAnalysisUpdate(BaseModel):
    """Model for real-time analysis updates"""

    call_id: str
    analysis: Optional[PrankCallAnalysis]  # Analysis result
    confidence_trend: List[float]  # Confidence scores over time
    current_status: (
        str  # "processing", "prank_suspected", "emergency_detected", "completed"
    )
    suggested_action: str  # Immediate recommendations
    update_timestamp: str
