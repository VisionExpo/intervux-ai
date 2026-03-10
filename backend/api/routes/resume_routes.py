from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
from backend.resume_parser.services import parse_resume, extract_entities
from backend.resume_parser.models import CandidateProfile

router = APIRouter()

# Define a temporary directory to store uploaded resumes
TEMP_DIR = "uploads/resumes"

@router.post("/upload", response_model=CandidateProfile)
async def upload_resume(file: UploadFile = File(...)):
    """
    Uploads a resume file, parses it, extracts entities, and returns a candidate profile.
    """
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
        
    file_path = os.path.join(TEMP_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ["pdf", "docx", "txt"]:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PDF, DOCX, or TXT file.")
            
        # Parse the resume to extract text
        text = parse_resume(file_path, file_extension)
        
        # Extract entities to build the profile
        profile = extract_entities(text)
        
        return profile
        
    except Exception as e:
        # Clean up the saved file in case of an error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        # Optionally, you can leave the file for debugging or remove it.
        # For this example, we'll remove it after processing.
        if os.path.exists(file_path):
             os.remove(file_path)

