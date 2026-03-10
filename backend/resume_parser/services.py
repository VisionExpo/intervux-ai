import pdfplumber
import docx
import spacy
from .models import CandidateProfile

# Load the spacy model
nlp = spacy.load("en_core_web_sm")

def parse_pdf(file_path: str) -> str:
    """Extracts text from a PDF file."""
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def parse_docx(file_path: str) -> str:
    """Extracts text from a DOCX file."""
    doc = docx.Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "
"
    return text

def parse_txt(file_path: str) -> str:
    """Reads text from a TXT file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def parse_resume(file_path: str, file_type: str) -> str:
    """
    Parses a resume file based on its type and returns the extracted text.
    """
    if file_type == "pdf":
        return parse_pdf(file_path)
    elif file_type == "docx":
        return parse_docx(file_path)
    elif file_type == "txt":
        return parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

def extract_entities(text: str) -> CandidateProfile:
    """
    Extracts entities from the resume text using spaCy NER
    and returns a CandidateProfile.
    """
    doc = nlp(text)
    
    # This is a very basic implementation.
    # It will need to be significantly improved with more sophisticated
    # section detection and entity extraction logic.
    
    profile = CandidateProfile()
    
    for ent in doc.ents:
        if ent.label_ == "PERSON" and not profile.name:
            profile.name = ent.text
        elif ent.label_ == "ORG":
            profile.companies.append(ent.text)
        # Email and phone numbers are not typically picked up by default NER
        # and would require custom patterns.
    
    # Simple skill matching (example)
    skills = ["python", "docker", "aws", "machine learning", "kubernetes", "javascript"]
    text_lower = text.lower()
    for skill in skills:
        if skill in text_lower:
            profile.skills.append(skill)
            
    return profile
