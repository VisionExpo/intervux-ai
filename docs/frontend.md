# Frontend Architecture

The Intervux AI frontend is a modern, responsive React application built with Vite and focused on a high-fidelity, immersive candidate experience.

## 📁 Routing Structure
The application uses `react-router-dom` for navigation, with routes defined in `frontend/src/App.tsx`:

- `/`: Landing & Home.
- `/interviews`: Unified Interview Hub (Candidate Portal).
- `/interview/:id`: Immersive 3D Avatar Interview Interface.
- `/profile`: Candidate Profile & Resume Management.
- `/recruiter/*`: Recruiter Dashboard & Analytics.
- `/admin/*`: System Administration.

## 🧩 Key Components & Hierarchy

### 1. The Interview Interface (`InterviewPage`)
- **Components**: `AvatarContainer`, `TranscriptPanel`, `AudioControls`.
- **Logic**: Orchestrated by the `useInterview` custom hook.
- **Purpose**: Provides the "Core UX" - seeing the avatar, speaking, and seeing live feedback.

### 2. Candidate Portal (`CandidatePortal`)
- **Components**: `BentoGrid`, `InterviewCard`, `StatCard`.
- **Purpose**: A professional dashboard for candidates to track their progress and manage their profile.

### 3. Recruiter Dashboard (`RecruiterDashboard`)
- **Components**: `DataTable`, `EvaluationReport`, `CompetencyChart`.
- **Purpose**: Data-dense interface for analyzing candidate performance.

## 📡 WebSocket Integration: `useInterview` Hook
The `useInterview.ts` hook is the "heartbeat" of the candidate experience:
- **State Management**: Tracks phase (WAITING, QUESTION, LISTENING), sequence IDs, and audio chunks.
- **Synchronization**: Uses sequence IDs to ensure transcripts and audio play in the correct order.
- **Audio Pipeline**: Manages the `AudioContext`, buffers incoming chunks, and triggers animations (visemes) in sync with playback.

## 🎨 Design System
- **Styling**: Vanilla CSS Modules for maximum performance and scoped styles.
- **Aesthetics**: Sleek Dark Mode, Glassmorphism (blur backgrounds), and smooth Framer Motion transitions.
- **Typography**: Modern sans-serif stack (Inter/Roboto) for an enterprise feel.

## 🔄 State Management
- **Local State**: React `useState` and `useReducer` for UI-specific state.
- **Global Context**: (If used) Context API for authentication and theme settings.
- **Persistent State**: LocalStorage for session tokens and basic user preferences.
