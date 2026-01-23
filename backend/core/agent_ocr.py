import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment varialbles
load_dotenv()

class ResumeParser:
    def __init__(self):
        # Get the key
        api_key = os.getenv("GOOGLE_API_KEY")

        # Configure the library
        genai.configure(api_key=api_key)

    def parse(self, file_path):
        """
        Uploads a PDF to Gemini and extracts structured data.
        """
        print(f"Processing resume:{file_path}")

        # To upload the PDF
        uploaded_file = genai.upload_file(file_path)

        # Initialize the model
        model = genai.GenerativeModel("gemini-1.5-flash", generation_config={"response_mine_type": "application/json"})

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
        # Generate Content (Prompt + File)

        response = model.generate_content([prompt,uploaded_file])

        # return the JSON File

        return response.text