🧠 Overview
The goal is to find the most relevant parts of a resume PDF for a particular job role. Our pipeline:
Parses PDFs using layout-aware tools
Detects section and subsection structure
Uses a lightweight relevance scoring system (no ML models)
Ranks and returns results in a clean JSON format

📁 Directory Structure
graphql
Copy
Edit
├── input/                  # Input folder
│   ├── sample.pdf         # here jsut as smpe and comaptibility test stored more                               #will work with more than 7 to 10 pdf more PDF resumes
│   └── challenge1b_input.json  # JSON config with "persona" and "jd"
│
├── output/                 # Output folder
│   └── challenge1b_output.json
│
├── src/                    # Source code
│   ├── pdf_processor.py
│   ├── text_analyzer_lite.py
│   └── section_ranker_lite.py,etc
│
├── main.py                 # Entry point
├── Dockerfile              # Docker setup
└── requirements_lite.txt   # Minimal dependencies
🧪 Input Format (input/*.json)
json
Copy
Edit
{
  "persona": "I'm a backend engineer interested in system design roles with Go and Kubernetes.",
  "jd": "Looking for a software engineer with expertise in backend systems, Docker, Kubernetes, and cloud deployment.",
  "pdf": "resume1.pdf"
}
📤 Output Format (output/challenge1b_output.json)
json
Copy

Edit
{
  "extracted_sections": [
    {
      "document": "resume1.pdf",
      "section_title": "Experience",
      "importance_rank": 1,
      "page_number": 2
    }
  ],
  "subsection_analysis": [
    {
      "document": "resume1.pdf",
      "refined_text": "Worked on scalable cloud-native backend with Kubernetes.",
      "page_number": 2
    }
  ]
}
🚀 Quick Start
Place your PDFs and input config in ./input/

Run the pipeline using Docker

Results are saved to ./output/challenge1b_output.json

🐳 Docker Instructions
bash
Copy
Edit
# Build the Docker image
docker build -t challenge_1b_adobe .

# Run the container (make sure input/ and output/ exist in your project root)
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output challenge_1b_adobe
⚙️ Dependencies
pdfplumber

PyPDF2

numpy

Installable via:

bash
Copy
Edit
pip install -r requirements_lite.txt
📌 Notes
No large ML models are used — optimized for speed and minimal footprint.

Works completely offline.

Flexible: any .json in the input folder is picked up automatically.

