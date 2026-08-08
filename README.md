# Personalized Interview Preparation System

> Agentic AI Capstone Project | FastAPI Backend + HTML/CSS/JS Frontend

---

## 🚀 Quick Start

### 1. Start the Backend Server
Double-click **`start_server.bat`**, or run manually:
```bash
cd backend
uvicorn main:app --reload --port 8000
```
The API will be live at: `http://127.0.0.1:8000`
Swagger docs: `http://127.0.0.1:8000/docs`

### 2. Open the Frontend
Open **`frontend/index.html`** in your browser (Chrome/Edge recommended).

---

## 📁 Project Structure
```
prepartion interview/
├── start_server.bat          ← Double-click to start backend
├── backend/
│   ├── main.py               ← FastAPI app (entry point)
│   ├── requirements.txt      ← Python dependencies
│   ├── .env                  ← Add your LLM API key here
│   ├── agents/
│   │   ├── resume_agent.py   ← Agent 1: Resume Analysis
│   │   ├── jd_agent.py       ← Agent 2: JD Analysis
│   │   ├── skill_gap_agent.py← Agent 3: Skill Gap Analysis
│   │   └── question_agent.py ← Agent 4: Question Generator
│   └── utils/
│       └── file_parser.py    ← PDF / DOCX / TXT parser
└── frontend/
    ├── index.html            ← Upload page
    ├── results.html          ← Results & analysis page
    ├── css/style.css
    └── js/
        ├── upload.js
        └── results.js
```

---

## 🔧 Install Dependencies (first time only)
```bash
cd backend
pip install -r requirements.txt
```

---

## 🤖 Enable Live LLM Responses
Edit `backend/.env` and add your API key:
```
GEMINI_API_KEY=your-google-gemini-api-key-here
# or
OPENAI_API_KEY=your-openai-api-key-here
```

---

## 📡 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/analyze` | Full pipeline: parse → analyze → generate questions |

---

## 🧠 AI Agent Pipeline
1. **Resume Analysis Agent** — Extracts skills, experience, education, projects
2. **JD Analysis Agent** — Extracts required skills, responsibilities, keywords
3. **Skill Gap Analysis Agent** — Match %, missing/matching skills, readiness level
4. **Question Generator Agent** — Technical, HR, Project & Skill-Gap questions

---

## 📋 Supported File Formats
- **PDF** (.pdf)
- **Word Document** (.docx)
- **Plain Text** (.txt)
