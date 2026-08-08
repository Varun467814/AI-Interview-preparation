# backend/agents/skill_gap_agent.py
"""
Agent 3: Skill Gap Analysis Agent
Compares candidate skills against JD required skills and produces:
  - Matching skills
  - Missing skills
  - Match percentage
  - Readiness level
"""
from typing import Any


def analyze_skill_gap(
    resume_data: dict[str, Any],
    jd_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Compare resume skills vs required JD skills.
    Returns matching skills, missing skills, and match score.
    """
    candidate_skills = {s.lower() for s in resume_data.get("skills", [])}
    required_skills  = {s.lower() for s in jd_data.get("required_skills", [])}

    if not required_skills:
        # Fallback when JD parsing found nothing
        return {
            "matching_skills": [],
            "missing_skills": [],
            "match_percentage": 0,
            "readiness_level": "Unknown",
            "recommendation": "Upload a more detailed job description for accurate analysis.",
        }

    matching = sorted(candidate_skills & required_skills)
    missing  = sorted(required_skills - candidate_skills)

    match_pct = round(len(matching) / len(required_skills) * 100)

    # ── Readiness label ───────────────────────────────────────────────────────
    if match_pct >= 80:
        readiness = "Interview Ready 🟢"
        recommendation = (
            "You have strong alignment with the role. "
            "Focus on practising system design and behavioural questions."
        )
    elif match_pct >= 50:
        readiness = "Partially Ready 🟡"
        recommendation = (
            "You meet many requirements. Bridge the skill gaps by building "
            "small projects using the missing technologies."
        )
    elif match_pct >= 25:
        readiness = "Needs Preparation 🟠"
        recommendation = (
            "Several key skills are missing. Enrol in targeted courses and "
            "build portfolio projects to close the gaps before applying."
        )
    else:
        readiness = "Not Ready 🔴"
        recommendation = (
            "Significant skill gaps exist. Consider a structured learning path "
            "covering the required technologies over the next 3-6 months."
        )

    # ── Experience gap ────────────────────────────────────────────────────────
    candidate_exp = resume_data.get("years_of_experience", 0)
    required_exp  = jd_data.get("required_experience_years", 0)
    exp_gap = max(0, required_exp - candidate_exp)

    return {
        "matching_skills": [s.title() for s in matching],
        "missing_skills":  [s.title() for s in missing],
        "match_percentage": match_pct,
        "readiness_level":  readiness,
        "recommendation":   recommendation,
        "candidate_experience_years": candidate_exp,
        "required_experience_years":  required_exp,
        "experience_gap_years":        exp_gap,
    }
