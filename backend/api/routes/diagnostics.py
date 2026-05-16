from fastapi import APIRouter, HTTPException, Depends
from backend.core.telemetry import SessionTelemetry
from backend.core.security.jwt_service import get_current_user

router = APIRouter()

@router.get("/session/{session_id}/timeline")
async def get_session_timeline(session_id: str, current_user: dict = Depends(get_current_user)):
    """
    Retrieve the exact chronological JSON array of everything that happened in a session.
    A developer can read this JSON and mentally (or programmatically) replay the exact sequence 
    of websocket messages, phase changes, and AI latencies, reconstructing the session exactly as it unfolded.
    """
    # NOTE: Optional role check (e.g. check if current_user is admin or the session owner)
    # For now, relying on JWT presence. In a strict prod environment, ensure authz.
    
    timeline = await SessionTelemetry.get_timeline(session_id)
    if not timeline:
        raise HTTPException(status_code=404, detail="No telemetry found for this session ID")
        
    return {"session_id": session_id, "timeline": timeline}
