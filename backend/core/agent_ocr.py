import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment varialbles
load_dotenv()

class ResumeParser:
    def __init__(self):
        # Get the key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")

        # Configure the library
        genai.configure(api_key=api_key)

    def parse(self, file_path):
        """
        Uploads a PDF to Gemini and extracts structured data.
        Returns: Python Dictionary(Parsed JSON)
        """
        print(f"Uploading to Gemini:{file_path}...")

        # To upload the PDF
        uploaded_file = genai.upload_file(file_path)

        # Initialize the model
        model = genai.GenerativeModel("gemini-2.5-flash", generation_config={"response_mime_type": "application/json"})

        # promt to extract info from resume
        prompt = """You are an expert Resume Parser.
                    Analyze the following details into a strict JSON format:

                        {
                            "name": "Full Name",
                            "contact": {
                                "email": "Email Address",
                                "phone": "Phone Number",
                                "linkedin": "LinkedIn URL (if present)"
                            },
                            "skills": ["List", "of", "technical", "skills"],
                            "experience": [
                                {
                                    "role": "Job Title",
                                    "company": "Company Name",
                                    "duration": "Start-End Date",
                                    "description": "Brief summary of responsibilities"
                                }
                            ],
                            "projects": [
                                {
                                    "title": "Project Name",
                                    "tech_stack":["List","of",tools],
                                    "description":"What was built"
                                    }
                                ]                            
                            }
                            """
        
        print("Analyzing document...")

        # Generate Content (Prompt + File)
        response = model.generate_content([prompt,uploaded_file])

        # Parse the string response into python dict
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            print("Error: Gemini returned invalid JSON.")
            return {}
        
# --- UNIT TEST

if __name__== "__main__":
    test_pdf = 'Vishal_Vilas_Gorule_Resume.pdf'
    
    if os.path.exists(test_pdf):
        parser = ResumeParser()
        data = parser.parse(test_pdf)

        print("\n SUCCESS! Extracted Data:")
        print(json.dumps(data,indent=2))
    else:
        print(f"File not found")
    