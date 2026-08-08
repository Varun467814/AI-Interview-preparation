# backend/agents/resume_agent.py
"""
Agent 1: Resume Analysis Agent
Extracts skills, projects, experience and builds a candidate profile.
To enable live LLM responses, set OPENAI_API_KEY or GEMINI_API_KEY in your .env.
"""
import os
import re
from typing import Any

# ── Common tech skill keywords for rule-based extraction ──────────────────────
SKILL_KEYWORDS = [
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "kotlin", "swift", "ruby", "php", "scala", "r", "matlab", "bash", "shell",
    # Web
    "html", "css", "react", "angular", "vue", "nextjs", "nodejs", "express",
    "django", "fastapi", "flask", "spring", "asp.net", "jquery",
    # Data / ML / AI
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow",
    "pytorch", "keras", "scikit-learn", "pandas", "numpy", "matplotlib",
    "hugging face", "langchain", "openai", "gemini", "llm", "rag",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle",
    "elasticsearch", "cassandra", "firebase",
    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "github actions",
    "jenkins", "terraform", "ansible", "linux",
    # Tools
    "git", "jira", "figma", "postman", "swagger", "rest api", "graphql",
    "microservices", "agile", "scrum",
]


def analyze_resume(resume_text: str) -> dict[str, Any]:
    """
    Extract structured information from raw resume text.
    Uses rule-based NLP; swap in LLM call when API key is available.
    """
    text_lower = resume_text.lower()

    # ── 1. Extract skills ─────────────────────────────────────────────────────
    found_skills = sorted({
        kw.title() for kw in SKILL_KEYWORDS if kw in text_lower
    })

    # ── 2. Extract name (first non-empty line heuristic) ──────────────────────
    lines = [l.strip() for l in resume_text.splitlines() if l.strip()]
    candidate_name = lines[0] if lines else "Candidate"

    # ── 3. Extract email ──────────────────────────────────────────────────────
    email_match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", resume_text)
    email = email_match.group(0) if email_match else "N/A"

    # ── 4. Extract phone ──────────────────────────────────────────────────────
    phone_match = re.search(r"(\+?\d[\d\s\-().]{7,}\d)", resume_text)
    phone = phone_match.group(0).strip() if phone_match else "N/A"

    # ── 5. Extract education ──────────────────────────────────────────────────
    edu_keywords = ["b.tech", "b.e", "m.tech", "mca", "bca", "b.sc", "m.sc",
                    "bachelor", "master", "phd", "degree", "university", "college"]
    education_lines = [
        l.strip() for l in lines
        if any(kw in l.lower() for kw in edu_keywords)
    ]
    education = education_lines[:3] if education_lines else ["Not found"]

    # ── 6. Extract experience section ────────────────────────────────────────
    exp_section = _extract_section(resume_text, ["experience", "work history", "employment"])
    experience_summary = exp_section[:500] if exp_section else "No experience section detected."

    # ── 7. Extract projects section ───────────────────────────────────────────
    proj_section = _extract_section(resume_text, ["project", "projects"])
    projects_summary = proj_section[:500] if proj_section else "No projects section detected."

    # ── 8. Detect years of experience ────────────────────────────────────────
    yoe_match = re.search(r"(\d+)\+?\s*year", text_lower)
    years_of_exp = int(yoe_match.group(1)) if yoe_match else 0

    return {
        "candidate_name": candidate_name,
        "email": email,
        "phone": phone,
        "education": education,
        "skills": found_skills,
        "years_of_experience": years_of_exp,
        "experience_summary": experience_summary,
        "projects_summary": projects_summary,
        "raw_text_length": len(resume_text),
    }


def _extract_section(text: str, headers: list[str]) -> str:
    """Pull out text under a section heading."""
    lines = text.splitlines()
    collecting = False
    section_lines: list[str] = []
    stop_keywords = ["education", "skills", "certifications", "references",
                     "awards", "languages", "hobbies", "summary", "objective"]

    for line in lines:
        line_lower = line.strip().lower()
        if any(h in line_lower for h in headers):
            collecting = True
            continue
        if collecting:
            if any(sk in line_lower for sk in stop_keywords) and line_lower not in headers:
                if section_lines:
                    break
            section_lines.append(line)

    return "\n".join(section_lines).strip()
