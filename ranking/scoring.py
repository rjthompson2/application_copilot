# USER PROFILE

PREFERRED_ROLES = [
    "backend",
    "software engineer",
    "full stack",
    "data engineer"
]

PREFERRED_SENIORITY = ["junior", "entry", "mid"]

REMOTE_BONUS = 0.1

MIN_SCORE = 0.4

# CORE SCORER
def score_job(job, profile):
    score = 0.0

    title = (job.get("title") or "").lower()
    desc = (job.get("description") or "").lower()
    skills = (job.get("skills") or "").lower()
    seniority = (job.get("seniority") or "").lower()

    text = title + " " + desc

    # 1. ROLE MATCH (30%)
    role_score = 0
    for role in PREFERRED_ROLES:
        if role in text:
            role_score = 1
            break

    score += role_score * 0.3

    # 2. SKILL MATCH (40%)
    skill_score = 0
    total_weight = sum(profile["skills"].values())

    for skill, weight in profile["skills"].items():
        if skill in text:
            skill_score += weight

    skill_score = min(skill_score / total_weight, 1.0)
    score += skill_score * 0.4

    # 3. SENIORITY FIT (20%)
    seniority_score = 1 if any(s in seniority for s in PREFERRED_SENIORITY) else 0.5
    score += seniority_score * 0.2

    # 4. DESCRIPTION QUALITY BONUS (10%)
    if len(desc) > 1000:
        score += 0.1

    return round(min(score, 1.0), 3)

def compute_resume_score(job, profile, faiss_score):
    job_skills = set((job.get("skills") or "").split(","))
    profile_skills = profile.get("skills", {})

    skill_score = 0
    total_weight = sum(profile_skills.values()) + 1e-5

    for skill, weight in profile_skills.items():
        if skill in job_skills:
            skill_score += weight

    skill_score /= total_weight

    final_score = (0.6 * faiss_score + 0.4 * skill_score)

    return round(final_score, 3), skill_score