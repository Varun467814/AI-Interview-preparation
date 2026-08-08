# backend/main.py
"""
Personalized Interview Preparation System — FastAPI Backend
Run with: uvicorn main:app --reload --port 8000
"""
import json
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from utils.file_parser import extract_text
from agents.resume_agent import analyze_resume
from agents.jd_agent import analyze_jd
from agents.skill_gap_agent import analyze_skill_gap
from agents.question_agent import generate_questions

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Personalized Interview Preparation API",
    description="Agentic AI system that analyzes resumes, identifies skill gaps, and generates interview questions.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Allows the plain HTML frontend to call this API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "message": "Interview Prep API is running ✅"}


# ── Main analysis endpoint ────────────────────────────────────────────────────
@app.post("/analyze", tags=["Agents"])
async def analyze(
    resume: UploadFile = File(..., description="Resume file (PDF / DOCX / TXT)"),
    job_description: UploadFile = File(..., description="Job description file (PDF / DOCX / TXT)"),
    target_role: str = Form(default="", description="Target job role / title"),
):
    """
    Full pipeline:
    1. Parse uploaded files
    2. Resume Analysis Agent
    3. JD Analysis Agent
    4. Skill Gap Analysis Agent
    5. Question Generator Agent
    Returns a complete JSON report.
    """
    # ── Validate file types ───────────────────────────────────────────────────
    allowed_exts = {".pdf", ".docx", ".txt"}
    for f in [resume, job_description]:
        ext = "." + (f.filename or "").rsplit(".", 1)[-1].lower()
        if ext not in allowed_exts:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{ext}'. Allowed: PDF, DOCX, TXT.",
            )

    # ── Step 1: Parse files ───────────────────────────────────────────────────
    resume_text = await extract_text(resume)
    jd_text     = await extract_text(job_description)

    if not resume_text or len(resume_text) < 50:
        raise HTTPException(status_code=422, detail="Could not extract text from resume. Please upload a text-based PDF or DOCX.")
    if not jd_text or len(jd_text) < 30:
        raise HTTPException(status_code=422, detail="Could not extract text from job description. Please upload a text-based file.")

    # ── Step 2: Resume Agent ──────────────────────────────────────────────────
    resume_data = analyze_resume(resume_text)

    # ── Step 3: JD Agent ──────────────────────────────────────────────────────
    jd_data = analyze_jd(jd_text, target_role=target_role)

    # ── Step 4: Skill Gap Agent ───────────────────────────────────────────────
    skill_gap_data = analyze_skill_gap(resume_data, jd_data)

    # ── Step 5: Question Generator Agent ─────────────────────────────────────
    questions_data = generate_questions(resume_data, jd_data, skill_gap_data)

    # ── Compose final response ────────────────────────────────────────────────
    result = {
        "status": "success",
        "target_role": target_role or jd_data.get("role_title", "N/A"),
        "candidate_profile": {
            "name":                 resume_data["candidate_name"],
            "email":                resume_data["email"],
            "phone":                resume_data["phone"],
            "education":            resume_data["education"],
            "skills":               resume_data["skills"],
            "years_of_experience":  resume_data["years_of_experience"],
            "experience_summary":   resume_data["experience_summary"],
            "projects_summary":     resume_data["projects_summary"],
        },
        "jd_analysis": {
            "role_title":               jd_data["role_title"],
            "required_skills":          jd_data["required_skills"],
            "required_experience_years":jd_data["required_experience_years"],
            "responsibilities":         jd_data["responsibilities"],
            "keywords":                 jd_data["keywords"],
        },
        "skill_gap": {
            "matching_skills":          skill_gap_data["matching_skills"],
            "missing_skills":           skill_gap_data["missing_skills"],
            "match_percentage":         skill_gap_data["match_percentage"],
            "readiness_level":          skill_gap_data["readiness_level"],
            "recommendation":           skill_gap_data["recommendation"],
            "experience_gap_years":     skill_gap_data["experience_gap_years"],
        },
        "interview_questions": {
            "difficulty_level":     questions_data["difficulty_level"],
            "total_questions":      questions_data["total_questions"],
            "technical":            questions_data["technical_questions"],
            "hr_behavioural":       questions_data["hr_questions"],
            "project_based":        questions_data["project_questions"],
            "skill_gap_bridging":   questions_data["skill_gap_questions"],
        },
    }

    return JSONResponse(content=result)


# ── Interactive API docs at /docs (Swagger UI) ────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
