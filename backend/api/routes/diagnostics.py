from fastapi import APIRouter, HTTPException, Depends
from backend.core.telemetry import SessionTelemetry
from backend.core.security.jwt_service import Role, TokenData, require_role

router = APIRouter()

@router.get("/session/{session_id}/timeline")
async def get_session_timeline(session_id: str, current_user: TokenData = Depends(require_role(Role.ADMIN))):
    """
    Retrieve the exact chronological JSON array of everything that happened in a session.
    A developer can read this JSON and mentally (or programmatically) replay the exact sequence 
    of websocket messages, phase changes, and AI latencies, reconstructing the session exactly as it unfolded.
    """
    # Admin only: the timeline exposes user IDs, socket IDs and file names.
    
    timeline = await SessionTelemetry.get_timeline(session_id)
    if not timeline:
        raise HTTPException(status_code=404, detail="No telemetry found for this session ID")
        
    return {"session_id": session_id, "timeline": timeline}
