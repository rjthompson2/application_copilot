import re

CANONICAL_SKILLS = {
    "python": ["python", "py", "python3"],
    "javascript": ["javascript", "js", "node", "nodejs"],
    "typescript": ["typescript", "ts"],
    "aws": ["aws", "amazon web services"],
    "sql": ["sql", "postgres", "postgresql", "mysql"],
    "docker": ["docker", "containers"],
    "react": ["react", "reactjs"],
    "flask": ["flask"],
    "java": ["java"],
}

def build_lookup():
    lookup = {}

    for canonical, variants in CANONICAL_SKILLS.items():
        for v in variants:
            lookup[v] = canonical

    return lookup


SKILL_LOOKUP = build_lookup()

def normalize_text(text):
    return re.sub(r"[^a-z0-9\s]", " ", text.lower())

def extract_normalized_skills(text):
    text = normalize_text(text)
    found = set()

    for variant, canonical in SKILL_LOOKUP.items():
        pattern = r"\b" + re.escape(variant) + r"\b"
        if re.search(pattern, text):
            found.add(canonical)

    return list(found)