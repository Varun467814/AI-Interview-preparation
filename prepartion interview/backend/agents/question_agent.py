# backend/agents/question_agent.py
"""
Agent 4: Question Generator Agent
Generates personalised interview questions based on:
  - Candidate's skills & projects
  - JD required skills & role
  - Skill gap (focuses on missing skills)

To enable live LLM-generated questions, set GEMINI_API_KEY or OPENAI_API_KEY
in a .env file at backend/.env and uncomment the LLM section below.
"""
import random
from typing import Any


# ── Static question banks (used in rule-based / mock mode) ───────────────────

TECHNICAL_QUESTIONS_BY_SKILL: dict[str, list[str]] = {
    "Python": [
        "Explain the difference between a list and a tuple in Python.",
        "What are Python decorators and when would you use them?",
        "How does Python's GIL (Global Interpreter Lock) affect multithreading?",
        "What is the difference between deep copy and shallow copy?",
        "Explain Python's generator functions and their advantages.",
    ],
    "Machine Learning": [
        "Explain the bias-variance tradeoff in machine learning.",
        "What is the difference between supervised and unsupervised learning?",
        "How would you handle class imbalance in a dataset?",
        "Explain what regularisation is and why it is used.",
        "What is cross-validation and why is it important?",
    ],
    "Sql": [
        "What is the difference between INNER JOIN and LEFT JOIN?",
        "Explain normalisation and the different normal forms.",
        "How would you optimise a slow SQL query?",
        "What are indexes and how do they improve performance?",
        "Explain the difference between WHERE and HAVING clauses.",
    ],
    "Java": [
        "What is the difference between an abstract class and an interface in Java?",
        "Explain Java's garbage collection mechanism.",
        "What are Java generics and why are they useful?",
        "Explain the concept of multithreading in Java.",
        "What is the difference between == and .equals() in Java?",
    ],
    "React": [
        "What is the virtual DOM and how does React use it?",
        "Explain the difference between controlled and uncontrolled components.",
        "What are React Hooks and what problem do they solve?",
        "How does useEffect work and what are its dependencies?",
        "Explain the concept of lifting state up in React.",
    ],
    "Aws": [
        "Explain the difference between EC2, Lambda, and ECS.",
        "What is S3 and what are its use cases?",
        "How does auto-scaling work in AWS?",
        "What is the purpose of IAM roles and policies?",
        "Explain the difference between RDS and DynamoDB.",
    ],
    "Docker": [
        "What is the difference between a Docker image and a container?",
        "Explain Docker volumes and when you would use them.",
        "How does Docker networking work?",
        "What is a Dockerfile and what are its key instructions?",
        "How would you optimise the size of a Docker image?",
    ],
    "Deep Learning": [
        "Explain the architecture of a Convolutional Neural Network (CNN).",
        "What is backpropagation and how does it work?",
        "Explain the vanishing gradient problem and how to address it.",
        "What is transfer learning and when is it useful?",
        "Explain the attention mechanism in transformers.",
    ],
    "Nlp": [
        "What is tokenisation and why is it important in NLP?",
        "Explain the difference between stemming and lemmatisation.",
        "What is TF-IDF and how is it used?",
        "Explain word embeddings like Word2Vec or GloVe.",
        "What are transformer models and how do they differ from RNNs?",
    ],
    "Mongodb": [
        "What is the difference between SQL and NoSQL databases?",
        "Explain MongoDB's document model.",
        "What are aggregation pipelines in MongoDB?",
        "How does MongoDB handle indexing?",
        "What is sharding in MongoDB and when is it used?",
    ],
}

GENERAL_TECHNICAL_QUESTIONS = [
    "Describe your approach to debugging a complex production issue.",
    "What is the difference between REST and GraphQL APIs?",
    "Explain the concept of microservices architecture.",
    "How do you ensure code quality in your projects?",
    "What is CI/CD and why is it important?",
    "Explain the SOLID principles of object-oriented design.",
    "What is the CAP theorem in distributed systems?",
    "How would you design a URL shortener system?",
    "What are design patterns and can you name a few you've used?",
    "Explain time complexity and Big-O notation with an example.",
]

HR_QUESTIONS = [
    "Tell me about yourself and your journey into software development.",
    "Why are you interested in this particular role and company?",
    "Describe a challenging project you worked on and how you overcame obstacles.",
    "Where do you see yourself professionally in 5 years?",
    "How do you handle tight deadlines and multiple competing priorities?",
    "Tell me about a time you had a disagreement with a teammate. How did you resolve it?",
    "What is your greatest professional strength and one area you're working to improve?",
    "Describe your ideal work environment and team culture.",
    "How do you stay updated with the latest trends in technology?",
    "Why are you looking for a new opportunity?",
]

PROJECT_QUESTIONS_TEMPLATES = [
    "Walk me through one of your most complex projects from start to finish.",
    "What was the biggest technical challenge in your {role} project and how did you solve it?",
    "How did you architect the system for scalability in your projects?",
    "What would you do differently if you were to redo your most recent project?",
    "How did you handle version control and collaboration in your team projects?",
    "What testing strategies did you use in your projects?",
    "How did you measure the performance and success of your projects?",
]

SKILL_GAP_QUESTIONS_TEMPLATES = [
    "We use {skill} heavily in this role. What is your current level of experience with it?",
    "How would you approach learning {skill} quickly if required for this position?",
    "Can you describe any exposure you've had to {skill}, even if indirect?",
]


def generate_questions(
    resume_data: dict[str, Any],
    jd_data: dict[str, Any],
    skill_gap_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate a personalised question set for the candidate.
    """
    candidate_skills = resume_data.get("skills", [])
    missing_skills   = skill_gap_data.get("missing_skills", [])
    role_title       = jd_data.get("role_title", "Software Engineer")

    # ── Technical questions (from candidate's actual skills) ─────────────────
    technical: list[str] = []
    for skill in candidate_skills:
        skill_title = skill.title()
        if skill_title in TECHNICAL_QUESTIONS_BY_SKILL:
            technical.extend(random.sample(TECHNICAL_QUESTIONS_BY_SKILL[skill_title], k=min(2, len(TECHNICAL_QUESTIONS_BY_SKILL[skill_title]))))
        if len(technical) >= 8:
            break

    # Fill up with general technical questions if needed
    remaining = [q for q in GENERAL_TECHNICAL_QUESTIONS if q not in technical]
    fill_count = max(0, 5 - len(technical))
    if fill_count > 0 and remaining:
        technical.extend(random.sample(remaining, k=min(fill_count, len(remaining))))
    technical = technical[:8]

    # ── HR / Behavioural questions ────────────────────────────────────────────
    hr = random.sample(HR_QUESTIONS, k=min(5, len(HR_QUESTIONS)))

    # ── Project-based questions ───────────────────────────────────────────────
    project = [
        t.replace("{role}", role_title)
        for t in random.sample(PROJECT_QUESTIONS_TEMPLATES, k=min(4, len(PROJECT_QUESTIONS_TEMPLATES)))
    ]

    # ── Skill-gap bridging questions ──────────────────────────────────────────
    gap_questions: list[str] = []
    for skill in missing_skills[:3]:
        template = random.choice(SKILL_GAP_QUESTIONS_TEMPLATES)
        gap_questions.append(template.replace("{skill}", skill))

    return {
        "technical_questions":    technical,
        "hr_questions":           hr,
        "project_questions":      project,
        "skill_gap_questions":    gap_questions,
        "total_questions":        len(technical) + len(hr) + len(project) + len(gap_questions),
        "difficulty_level":       _determine_difficulty(resume_data),
    }


def _determine_difficulty(resume_data: dict[str, Any]) -> str:
    yoe = resume_data.get("years_of_experience", 0)
    skill_count = len(resume_data.get("skills", []))
    if yoe >= 5 or skill_count >= 15:
        return "Advanced"
    elif yoe >= 2 or skill_count >= 8:
        return "Intermediate"
    else:
        return "Beginner"
