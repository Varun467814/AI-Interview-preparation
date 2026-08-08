# backend/agents/jd_agent.py
"""
Agent 2: Job Description Analysis Agent
Extracts required skills, responsibilities, and keywords from a job description.
"""
import re
from typing import Any

from agents.resume_agent import SKILL_KEYWORDS  # reuse the same skill vocab


def analyze_jd(jd_text: str, target_role: str = "") -> dict[str, Any]:
    """
    Parse a job description and return structured data.
    """
    text_lower = jd_text.lower()
    lines = [l.strip() for l in jd_text.splitlines() if l.strip()]

    # ── 1. Required skills ────────────────────────────────────────────────────
    required_skills = sorted({
        kw.title() for kw in SKILL_KEYWORDS if kw in text_lower
    })

    # ── 2. Experience requirement ─────────────────────────────────────────────
    yoe_match = re.search(r"(\d+)\+?\s*year", text_lower)
    required_experience = int(yoe_match.group(1)) if yoe_match else 0

    # ── 3. Responsibilities ───────────────────────────────────────────────────
    resp_section = _extract_section(jd_text, ["responsibilities", "duties", "what you'll do", "role"])
    responsibilities = _bullet_lines(resp_section)[:8]
    if not responsibilities:
        responsibilities = [l for l in lines if len(l) > 30][:6]

    # ── 4. Keywords / buzzwords ───────────────────────────────────────────────
    important_kws = [
        "agile", "scrum", "ci/cd", "microservices", "rest api", "cloud",
        "distributed", "scalable", "machine learning", "data-driven",
        "problem-solving", "collaboration", "communication", "leadership",
        "cross-functional", "startup", "product", "stakeholder",
    ]
    keywords = [kw.title() for kw in important_kws if kw in text_lower]

    # ── 5. Role title ─────────────────────────────────────────────────────────
    role_title = target_role or (lines[0] if lines else "Software Engineer")

    return {
        "role_title": role_title,
        "required_skills": required_skills,
        "required_experience_years": required_experience,
        "responsibilities": responsibilities,
        "keywords": keywords,
    }


def _extract_section(text: str, headers: list[str]) -> str:
    lines = text.splitlines()
    collecting = False
    section_lines: list[str] = []
    stop_keywords = ["qualifications", "requirements", "nice to have",
                     "about us", "benefits", "perks", "compensation"]

    for line in lines:
        line_lower = line.strip().lower()
        if any(h in line_lower for h in headers):
            collecting = True
            continue
        if collecting:
            if any(sk in line_lower for sk in stop_keywords):
                if section_lines:
                    break
            section_lines.append(line)

    return "\n".join(section_lines).strip()


def _bullet_lines(text: str) -> list[str]:
    """Return non-empty lines stripped of bullet characters."""
    result = []
    for line in text.splitlines():
        clean = re.sub(r"^[\s\-•*►▸]+", "", line).strip()
        if len(clean) > 10:
            result.append(clean)
    return result
