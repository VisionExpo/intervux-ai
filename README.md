# Intervux AI: AI-Driven 3D Mock Interviewer

<div align="center">

![Version](https://img.shields.io/badge/version-1.0-blue?style=flat)
![Status](https://img.shields.io/badge/status-active-success?style=flat)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red?style=flat&logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/AI-Gemini%201.5%20Pro-4285F4?style=glat&logo=google&logoColor=white)
![Vision](https://img.shields.io/badge/Vision-OpenCV%20%2B%20FER-5C3EE8>style=flat&logo=opencv&logoColor=white)
![Avatar](https://img.shields.io/badge/Avatar-Three.js%20%2F%20RPM-black?style=flat&logo=three.js&logoColor=white)
![Editor](https://img.shields.io/badge/Code-Monaco%20Editor-1E1E1E?style=flat&logo=visiual-studio&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)
![Rendor](https://img.shields.io/badge/Render-Deployment-46E3B7?style=flat&logo=render&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat)

</div>

<div align="center">
    <strong>The world's first "Double-Sided" AI Interviewer that Reads Your Face, Hears Your Voice, Reviews Your Code and Reacts in 3D.</strong>
</div>

## Overview
**PrepMaster** is a next-generation mock interview platform designed to simulate the pressure and fluidity of a real technical interview. It goes beyond simple text chat by integrating **3D Avatars**, **Real-Time Emotion Detection** and **Agentic Document Parsing**.

Unlike standard chatbots, PrepMaster acts as a **"Double-Sided"** partner:
1. It **Sees** what you see (via Agent OCR of your resume).
2. It **Hears** when you interrupt (via Full-Duplex Audio).
3. It **Feels** your anxiety (via Facial Micro-Expression Analysis).

## Features

- **3D Holographic Interviewer**: A realistic 3D Avatar (Three.js/Ready Player Me) that speaks, blinks and maintain eye contact with lip-sync animation.
- **Live Coding Sandbox**: An embedded **Monaco Code Editor** where candidates solve DSA problems. The AI reviews code completely (Big 0) and syntax in real-time.
- **Emotion & Confidence Analysis**: Uses Computer Vision (OpenCV) to detect facial micro-expressions (Nervousness, Confidence) to grade non-verbal skills.
- **Agent OCR-RAG**: Intelligent resume parsing using Vision-Language Models (50% token reduction vs raw text).
- **Double-Sided Audio**: Full-Duplex communication allowing users to interrupt the AI naturally using Voice Activity Detection (VAD).
- **Low Latency**: Optimized WebRTC streaming for realistic conversational flow.
- **Privacy Focused**: No data retention; sessions are stateless and video analysis happens locally.

## Core Modules

1. **Agent OCR:** "Looks" at the resume PDF as an image to extract structure without raw text bloat.
2. **Coding Engine:** A secure sandbox (`streamlit-code-editor`) for executing and grading Python/SQL snippets.
3. **Vision Engine:** Real-time facial expression recognition (FER) to assess candidate anxiety.
4. **Duplex Bridge:** Handles audio interruptions so you can talk over the AI.

## Tech Stack

<div align="center">

|     Domain     |       Technology       |                  Purpose                |
|:---------------|:-----------------------|:----------------------------------------|
|**Frontend**    | `Streamlit` + `HTML5`  | Core Interface                          |
|**Code Editor** | `streamlit-code-editor`| Embedded Monaco Editor for coding tasks |
|**3D Engine**   | `Three.js` / `RPM`     | Rendering the Interviewer Avatar        |
|**Vision AI**   | `OpenCV` + `FER`       | Emotion & Enxiety Detection             |
|**Reasoning**   | `Gemini 1.5 Flash`     | Brain (Logic & Conversation)            |
|**Audio**       |`Streamlit-WebRTC`      | Real-time Video/Audio Streaming         |
|**Deploy**      | `Docker` -> `Render`   | Containerization                        |

</div>

## Quick Start

1. **Clone the repository:**
    ```bash
    git clone https://github.com/VisionExpo/PrepMaster.git
    cd PrepMaster

2. **Create and activate virtual environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate # Windows
    source venv/bin/activate # Linux/Mac

3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt

4. **Set up environment variables:**
    # Create a .env file:
    ```env
    GOOGLE_API_KEY=your_gemini_key
    GROQ_API_KEY=your_groq_key

5. **Start the application:**
    ```bash
    streamlit run app.py

This will open the Web Interfave at:
http://localhost:8501


## System Architecture

## Roadmap

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE)

<div align="center">
Made with love by <strong>Vishal</strong>
</div>
