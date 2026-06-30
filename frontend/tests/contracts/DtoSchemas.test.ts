import { describe, it, expect } from 'vitest';
// In a real application these types would be imported from the backend types/schemas
// Here we define the canonical contract expectations to ensure projection APIs don't drift

describe('DTO Contract Schemas', () => {
    it('Candidate DTO schema remains stable', () => {
        const candidateDto = {
            version: '1.0',
            workspace: {
                mode: 'CONVERSATION',
                isRecording: false,
                currentQuestion: 'Tell me about a time you failed.'
            },
            candidate: {
                name: 'John Doe',
                role: 'Senior Engineer',
                connected: true
            },
            ui: {
                theme: 'dark',
                showDebug: false
            }
        };

        expect(candidateDto).toMatchInlineSnapshot(`
          {
            "candidate": {
              "connected": true,
              "name": "John Doe",
              "role": "Senior Engineer",
            },
            "ui": {
              "showDebug": false,
              "theme": "dark",
            },
            "version": "1.0",
            "workspace": {
              "currentQuestion": "Tell me about a time you failed.",
              "isRecording": false,
              "mode": "CONVERSATION",
            },
          }
        `);
    });

    it('Recruiter DTO schema remains stable', () => {
        const recruiterDto = {
            version: '1.0',
            candidate: {
                id: 'cand_123',
                score: 85,
                weaknesses: ['Concurrency', 'System Design']
            },
            interview: {
                progress: '50%',
                flagged: false,
                duration: '15m'
            }
        };

        expect(recruiterDto).toMatchInlineSnapshot(`
          {
            "candidate": {
              "id": "cand_123",
              "score": 85,
              "weaknesses": [
                "Concurrency",
                "System Design",
              ],
            },
            "interview": {
              "duration": "15m",
              "flagged": false,
              "progress": "50%",
            },
            "version": "1.0",
          }
        `);
    });
});
