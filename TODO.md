# Intervux AI - WebSocket Architecture Refactoring Plan

## Current Architecture
The current `InterviewSocket` class in `backend/sockets/interview.py` is a giant handler (~1200 lines) that handles:
- WebSocket connection management
- JWT token verification  
- Rate limiting and session slots
- Resume parsing
- Question generation
- Audio buffering and streaming
- STT transcription
- Answer evaluation
- TTS synthesis with visemes
- Report generation

## Proposed Architecture

```
WebSocket Gateway
        │
        ▼
Interview Session Manager
        │
        ▼
Interview Engine
        │
        ▼
AI Services
(STT / LLM / Evaluation / TTS)
```

## Phase 1: Create New Directory Structure ✅

### 1.1 Create directories
```
backend/
├── sockets/
│   └── interview_gateway.py   (NEW - thin WebSocket layer)
├── sessions/
│   └── interview_session.py   (NEW - lifecycle management)
├── engines/
│   └── interview_engine.py    (NEW - AI logic)
├── services/
│   ├── stt_service.py         (EXISTING)
│   ├── tts_service.py         (EXISTING)
│   └── evaluation_service.py  (NEW - wrapper for evaluation)
│   └── audio_buffer.py        (NEW - isolated audio handling)
└── models/
    └── interview_state.py     (EXISTING - needs enhancement)
```

## Phase 2: Create Models ✅

### 2.1 Enhance InterviewState (`backend/models/interview.py`)
- ✅ Add state machine enum: `CONNECTING`, `WAITING_RESUME`, `QUESTION`, `LISTENING`, `PROCESSING`, `NEXT_QUESTION`, `COMPLETE`
- ✅ Add guard transitions
- ✅ Keep existing state attributes

### 2.2 Message Protocol
```python
# Client → Server
- resume_upload
- audio_chunk  
- stream_end / audio_end

# Server → Client
- avatar_sync
- avatar_visemes
- phase
- evaluation
- next_question
- interview_complete
- error
```

## Phase 3: Create Services ✅

### 3.1 Create Evaluation Service (`backend/services/evaluation_service.py`)
- ✅ Wrapper around `evaluate_answer_dual`
- ✅ Expose methods: `evaluate_answer()`, `evaluate_answer_lightweight()`, `evaluate_full()`

### 3.2 Create Audio Buffer (`backend/services/audio_buffer.py`)
- ✅ Thread-safe audio buffer
- ✅ Methods: `add()`, `bytes()`, `clear()`, `size_bytes`, `duration_seconds`

## Phase 4: Create Interview Engine ✅

### 4.1 Create `InterviewEngine` (`backend/engines/interview_engine.py`)
- ✅ `start_interview()` - Parse resume, generate initial question
- ✅ `process_audio()` - Transcribe audio
- ✅ `evaluate_answer()` - Evaluate answer, generate next question
- ✅ `complete_interview()` - Generate final report
- ✅ Score normalization
- ✅ Skill performance summary

## Phase 5: Create Session Manager ✅

### 5.1 Create `InterviewSession` (`backend/sessions/interview_session.py`)
- ✅ Manage interview lifecycle
- ✅ Route messages to engine
- ✅ State machine transitions
- ✅ Audio buffering during streaming

## Phase 6: Session Registry ✅

### 6.1 Create Session Registry (`backend/sessions/registry.py`)
- ✅ Global session registry
- ✅ Methods: `register()`, `unregister()`, `get()`, `cleanup_all()`

## Phase 7: Create WebSocket Gateway ✅

### 7.1 Create `InterviewGateway` (`backend/sockets/interview_gateway.py`)
- ✅ Thin network I/O layer
- ✅ JWT token verification
- ✅ Rate limiting
- ✅ Session slot management
- ✅ Message routing to session

## Phase 8: Update Main App ✅

### 8.1 Update `backend/main.py`
- ✅ Import `InterviewGateway` instead of `InterviewSocket`
- ✅ Update WebSocket endpoint to use gateway
- ✅ Update shutdown to use gateway

## Implementation Status

| Phase | Status |
|-------|--------|
| Phase 1: Directory Structure | ✅ Complete |
| Phase 2: Models (State Machine) | ✅ Complete |
| Phase 3: Services | ✅ Complete |
| Phase 4: Interview Engine | ✅ Complete |
| Phase 5: Session Manager | ✅ Complete |
| Phase 6: Session Registry | ✅ Complete |
| Phase 7: WebSocket Gateway | ✅ Complete |
| Phase 8: Main App Integration | ✅ Complete |

## Files Created/Modified

### New Files
- `backend/services/audio_buffer.py` - Audio buffer service
- `backend/services/evaluation_service.py` - Evaluation wrapper
- `backend/engines/interview_engine.py` - Core AI engine
- `backend/sessions/interview_session.py` - Session manager
- `backend/sessions/registry.py` - Session registry
- `backend/sockets/interview_gateway.py` - WebSocket gateway

### Modified Files
- `backend/models/interview.py` - Added state machine
- `backend/main.py` - Updated to use new gateway

## Testing Notes

The old `InterviewSocket` in `backend/sockets/interview.py` is kept as a backup and can be removed after the new architecture is tested and validated.

