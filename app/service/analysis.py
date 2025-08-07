from typing import Optional
from app.models.call import (
    PrankCallAnalysis,
    StreamingCallChunk,
    StreamingAnalysisUpdate,
)
from datetime import datetime


class StreamingCallProcessor:
    def __init__(self, agent):
        self.agent = agent
        self.active_calls = {}  # Store state for active calls
        self.analysis_cache = {}  # Cache for intermediate results

    async def process_chunk(self, chunk: StreamingCallChunk) -> StreamingAnalysisUpdate:
        """Process a single chunk of streaming call data"""

        # Initialize call state if new call
        if chunk.call_id not in self.active_calls:
            self.active_calls[chunk.call_id] = {
                "transcript": "",
                "chunks": [],
                "start_time": datetime.now(),
                "confidence_history": [],
                "current_analysis": None,
            }

        call_state = self.active_calls[chunk.call_id]
        call_state["chunks"].append(chunk)

        # Update transcript
        if chunk.audio_chunk:  # Assuming it's already transcribed
            call_state["transcript"] += f" {chunk.audio_chunk}"

        # Perform analysis if we have enough content or it's final
        analysis_update = None
        if len(call_state["transcript"]) > 50 or chunk.is_final:
            analysis_update = await self.analyze_partial_transcript(
                chunk.call_id, call_state["transcript"], chunk.is_final
            )
            call_state["current_analysis"] = analysis_update
            if analysis_update:
                call_state["confidence_history"].append(
                    analysis_update.confidence_score
                )

        # Determine current status
        status = "processing"
        suggested_action = "Continue monitoring"

        if analysis_update:
            if analysis_update.is_prank_call and analysis_update.confidence_score > 0.8:
                status = "prank_suspected"
                suggested_action = analysis_update.suggestion
            elif (
                not analysis_update.is_prank_call
                and analysis_update.confidence_score > 0.7
            ):
                status = "emergency_detected"
                suggested_action = analysis_update.suggestion

        if chunk.is_final:
            status = "completed"
            suggested_action = "Call completed - final analysis provided"

        return StreamingAnalysisUpdate(
            call_id=chunk.call_id,
            analysis=analysis_update,
            confidence_trend=call_state["confidence_history"],
            current_status=status,
            suggested_action=suggested_action,
            update_timestamp=datetime.now().isoformat(),
        )

    async def analyze_partial_transcript(
        self, call_id: str, transcript: str, is_final: bool
    ) -> Optional[PrankCallAnalysis]:
        """Analyze partial transcript with appropriate prompt engineering"""

        # Modify system prompt for partial analysis
        partial_analysis_prompt = f"""
        Analyze this PARTIAL emergency call transcript. The call is still in progress.
        
        CURRENT TRANSCRIPT: {transcript}
        
        INSTRUCTIONS:
        1. Provide preliminary assessment based on available information
        2. If this is clearly a prank, indicate HIGH confidence
        3. If this appears to be a genuine emergency, recommend immediate attention
        4. If insufficient information, indicate low confidence and need for more data
        5. NEVER miss a potential real emergency due to incomplete information

        CONTEXT:
        call_id: {call_id}
        is_partial: {not is_final}
        transcript_length: {len(transcript)}
        """

        try:
            result = await self.agent.run(
                partial_analysis_prompt,
            )
            return result.data
        except Exception as e:
            # Return None to continue processing if analysis fails
            print(f"Analysis failed for call {call_id}: {e}")
            return None
