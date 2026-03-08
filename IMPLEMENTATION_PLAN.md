# AI Interviewer Panel Implementation Plan

## Information Gathered

### Current Project Structure

**Backend (`backend/sockets/interview.py`):**
- Full WebSocket interview handler with adaptive question engine
- Handles resume upload, audio streaming, speech-to-text, evaluation
- Sends events: `avatar_sync`, `avatar_visemes`, `emotion_update`, `evaluation`, `interview_complete`, `partial_transcript`, `phase`
- States: CONNECTING → WAITING_RESUME → ASKING_QUESTION → LISTENING → PROCESSING → COMPLETED

**Frontend:**
- React 19 + Vite
- Three.js with @react-three/fiber and @pixiv/three-vrm for 3D avatar
- Hook `useInterview.ts` manages WebSocket, audio streaming, state
- Monaco Editor not installed yet
- Tailwind CSS not installed yet
- Current `InterviewPage.tsx` has simple vertical layout

### Task Requirements

Create an AI Interviewer Panel with:
1. **Top Left**: AI Interviewer (3D avatar, AI animation, question display, state indicators)
2. **Top Right**: Coding Sandbox (Monaco editor, language selection, run button)
3. **Bottom Right**: Candidate Camera (video preview, mic indicator, connection status)
4. **Bottom**: Transcript Panel (conversation history)
5. **Continuous Audio Listening**: VAD instead of record button
6. **Greeting Flow**: Multi-step greeting before first question
7. **Question Progression**: Adaptive difficulty
8. **UI States**: CONNECTING, GREETING, QUESTION, LISTENING, PROCESSING, NEXT_QUESTION, INTERVIEW_COMPLETE
9. **Real Interview Feel**: Typing indicator, thinking state, subtle audio tones

---

## Plan

### Phase 1: Setup & Dependencies (Step 1-2)

1. **Install Monaco Editor** for coding sandbox
2. **Install Tailwind CSS** for styling
3. **Configure Tailwind**

### Phase 2: UI Components (Step 3-8)

4. **Create InterviewLayout component** - Main grid layout
5. **Create AvatarInterviewer component** - Enhanced avatar with state indicators
6. **Create CodingSandbox component** - Monaco editor with run functionality
7. **Create CandidateCamera component** - Video preview with status indicators
8. **Create TranscriptPanel component** - Conversation display

### Phase 3: Integration (Step 9-12)

9. **Update useInterview hook** - Add new states and functions
10. **Create new InterviewPage** - Compose all components
11. **Update App.tsx routing** - Route to new page
12. **Add global styles** - Animations, transitions

---

## Detailed Implementation

### File Changes Required

**New Files:**
- `frontend/src/components/interview/InterviewLayout.tsx`
- `frontend/src/components/interview/AvatarInterviewer.tsx`
- `frontend/src/components/interview/CodingSandbox.tsx`
- `frontend/src/components/interview/CandidateCamera.tsx`
- `frontend/src/components/interview/TranscriptPanel.tsx`
- `frontend/src/components/interview/AudioStreamHandler.tsx`
- `frontend/src/components/interview/index.ts` (exports)

**Modified Files:**
- `frontend/package.json` - Add dependencies
- `frontend/vite.config.ts` - Add Tailwind
- `frontend/src/index.css` - Add Tailwind directives
- `frontend/src/hooks/useInterview.ts` - Enhanced state management
- `frontend/src/pages/InterviewPage.tsx` - New layout
- `frontend/src/App.tsx` - Routing

---

## Follow-up Steps

1. Install Monaco Editor: `npm install @monaco-editor/react`
2. Install Tailwind CSS: `npm install -D tailwindcss @tailwindcss/vite`
3. Configure Tailwind in vite.config.ts
4. Create all components with proper styling
5. Test the full interview flow

