import re
from datetime import datetime
from ranking.skills import extract_normalized_skills

ROLE_PATTERN = re.compile(
    r"""
    (?P<title>.+?)\s*,\s*
    (?P<company>.+?),\s*
    (?P<location>.+?),\s*
    (?P<dates>(?:\w+\s\d{4})\s*-\s*(?:Present|\w+\s\d{4}))
    """,
    re.VERBOSE
)


def extract_roles(resume_text):
    matches = list(ROLE_PATTERN.finditer(resume_text))

    roles = []

    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(resume_text)

        role_text = resume_text[start:end]

        roles.append({
            "title": match.group("title"),
            "company": match.group("company"),
            "dates": match.group("dates"),
            "text": role_text
        })

    return roles


def parse_years(date_str):
    try:
        start_str, end_str = [s.strip() for s in date_str.split("-")]

        start = datetime.strptime(start_str, "%B %Y")

        if "Present" in end_str:
            end = datetime.now()
        else:
            end = datetime.strptime(end_str, "%B %Y")

        return max((end - start).days / 365, 0.25)

    except:
        return 1.0
    

def extract_skills_from_role(text):
    # Prefer explicit "Leveraged Knowledge"
    match = re.search(r"Leveraged Knowledge\s*:\s*(.+)", text)

    if match:
        return extract_normalized_skills(match.group(1))

    # fallback → whole role text
    return extract_normalized_skills(text)