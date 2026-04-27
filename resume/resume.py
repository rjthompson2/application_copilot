import re
from ranking.skills import extract_normalized_skills
from resume.roles import extract_roles, parse_years

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

KNOWN_SKILLS = [
    "python", "aws", "sql", "java", "docker",
    "flask", "react", "javascript", "typescript"
]


def extract_years(text):
    # crude date parsing
    match = re.findall(r"(\w+\s\d{4})\s*[-–]\s*(Present|\w+\s\d{4})", text)

    total_years = 0

    for start, end in match:
        try:
            start_date = datetime.strptime(start, "%b %Y")
            end_date = datetime.now() if end == "Present" else datetime.strptime(end, "%b %Y")

            delta = (end_date - start_date).days / 365
            total_years += max(delta, 0)
        except:
            continue

    return total_years if total_years > 0 else 1  # fallback


def build_user_profile(resume_text):
    roles = extract_roles(resume_text)

    skill_weights = {}

    for role in roles:
        years = parse_years(role["dates"])
        skills = extract_normalized_skills(role["text"])

        for skill in skills:
            skill_weights[skill] = skill_weights.get(skill, 0) + years

    # normalize
    max_val = max(skill_weights.values(), default=1)

    for k in skill_weights:
        skill_weights[k] /= max_val

    return {
        "skills": skill_weights
    }
    
# def build_user_profile(resume_text):
#     profile = {
#         "skills": {},
#         "titles": [],
#         "seniority": ""
#     }

#     sections = resume_text.split("\n\n")

#     for section in sections:
#         years = extract_years(section)

#         skills = extract_normalized_skills(section)

#         for skill in skills:
#             profile["skills"][skill] = profile["skills"].get(skill, 0) + years

#     # normalize weights
#     max_val = max(profile["skills"].values(), default=1)

#     for k in profile["skills"]:
#         profile["skills"][k] /= max_val

#     return profile

# # def build_user_profile(resume_text):
# #     profile = {
# #         "skills": {},
# #         "titles": [],
# #         "seniority": ""
# #     }

# #     sections = resume_text.split("\n\n")

# #     for section in sections:
# #         section_lower = section.lower()

# #         years = extract_years(section)

# #         for skill in KNOWN_SKILLS:
# #             if skill in section_lower:
# #                 profile["skills"][skill] = profile["skills"].get(skill, 0) + years

# #     # normalize (optional)
# #     max_years = max(profile["skills"].values(), default=1)

# #     for skill in profile["skills"]:
# #         profile["skills"][skill] /= max_years

# #     return profile

# # old version
# # def build_user_profile(resume_text):
# #     parsed = parse_resume(resume_text)

# #     skill_weights = {s: 2 for s in parsed["skills"]}

# #     return {
# #         "skills": skill_weights,
# #         "roles": parsed["roles"],
# #         "experience_years": parsed["experience_years"]
# #     }
    