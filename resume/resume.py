import re

def parse_resume(text):
    text = text.lower()

    # very simple skill extraction baseline
    skill_keywords = [
        "python", "java", "c++", "javascript", "typescript",
        "aws", "docker", "kubernetes", "sql", "react", "node",
        "flask", "fastapi", "django"
    ]

    skills = [s for s in skill_keywords if s in text]

    # crude experience detection
    years = re.findall(r"(\d+)\+?\s+years", text)
    experience_years = max([int(y) for y in years], default=0)

    # role hints
    roles = []
    if "backend" in text:
        roles.append("backend")
    if "full stack" in text:
        roles.append("full stack")
    if "software engineer" in text:
        roles.append("software engineer")

    return {
        "skills": skills,
        "experience_years": experience_years,
        "roles": roles,
        "raw_text": text
    }

def load_resume(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def build_user_profile(resume_text):
    parsed = parse_resume(resume_text)

    skill_weights = {s: 2 for s in parsed["skills"]}

    return {
        "skills": skill_weights,
        "roles": parsed["roles"],
        "experience_years": parsed["experience_years"]
    }
    