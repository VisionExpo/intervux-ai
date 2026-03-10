# Intervux AI - Resume Processing Pipeline Plan

## Goal
Implement a resume processing pipeline to extract structured data from resumes, which will then be used to feed the interview engine.

## Pipeline Stages
1.  **Resume Ingestion**: Handle PDF, DOCX, and TXT formats.
2.  **Text Extraction**: Extract raw text from the documents.
3.  **Section Detection**: Identify different sections like "Experience", "Skills", "Education".
4.  **Entity Extraction (NER)**: Extract named entities like names, companies, skills, etc.
5.  **Skill Normalization**: Normalize the extracted skills (e.g., "k8s" -> "Kubernetes").
6.  **Profile Builder**: Create a structured candidate profile.
7.  **Database Storage**: Store the profile in the database.

## Tech Stack
-   **FastAPI**: For the API endpoint.
-   **PyMuPDF**: For PDF processing.
-   **python-docx**: For DOCX processing.
-   **spaCy**: For NER and NLP tasks.
-   **PostgreSQL**: For storing the profiles.

## Implementation Plan

### Phase 1: Setup and Ingestion
-   [ ] Create a new module `backend/resume_parser`.
-   [ ] Add `PyMuPDF`, `python-docx`, and `spacy` to `requirements.txt`.
-   [ ] Implement a service for PDF text extraction.
-   [ ] Implement a service for DOCX text extraction.
-   [ ] Implement a service for TXT file reading.
-   [ ] Create a factory function to handle different file types.

### Phase 2: API Endpoint
-   [ ] Create a new router in `backend/routes/resume_routes.py`.
-   [ ] Add an endpoint `/resumes/upload` that accepts a file upload.
-   [ ] The endpoint should save the file and use the ingestion service to extract text.

### Phase 3: NLP Processing
-   [ ] Integrate `spaCy` for NER.
-   [ ] Download and set up the `en_core_web_sm` model.
-   [ ] Implement entity extraction for skills, experience, etc.
-   [ ] Create a skill normalization dictionary/service.

### Phase 4: Profile and Storage
-   [ ] Create a `CandidateProfile` Pydantic model.
-   [ ] Implement a `ProfileBuilder` service to create the profile from extracted data.
-   [ ] Create a new database table for candidate profiles.
-   [ ] Implement a service to save the profile to the database.

### Phase 5: Integration with Interview Engine
-   [ ] Modify the `InterviewEngine` to accept a candidate profile.
-   [ ] Use the profile to tailor interview questions based on candidate skills.
