import re


CANONICAL_SKILLS = {
    # Programming Languages
    "python": ["python", "py", "python3"],
    "javascript": ["javascript", "js", "node", "nodejs"],
    "typescript": ["typescript", "ts"],
    "java": ["java"],
    "c": ["c"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "csharp", ".net"],
    "go": ["go", "golang"],
    "rust": ["rust"],
    "php": ["php"],
    "ruby": ["ruby"],
    "swift": ["swift"],
    "kotlin": ["kotlin"],
    "scala": ["scala"],
    "r": ["r programming", "r language"],

    # Frontend
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "react": ["react", "reactjs"],
    "vue": ["vue", "vuejs"],
    "angular": ["angular"],
    "nextjs": ["nextjs", "next.js"],
    "svelte": ["svelte"],
    "tailwind": ["tailwind", "tailwindcss"],
    "bootstrap": ["bootstrap"],

    # Backend
    "flask": ["flask"],
    "django": ["django"],
    "fastapi": ["fastapi"],
    "express": ["express", "expressjs"],
    "spring": ["spring", "spring boot"],
    "laravel": ["laravel"],
    "asp.net": ["asp.net", "aspnet"],

    # Databases
    "sql": ["sql"],
    "postgresql": ["postgres", "postgresql"],
    "mysql": ["mysql"],
    "sqlite": ["sqlite"],
    "mongodb": ["mongodb", "mongo"],
    "redis": ["redis"],
    "dynamodb": ["dynamodb"],
    "elasticsearch": ["elasticsearch", "elastic search"],

    # Cloud
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "cloudflare": ["cloudflare"],

    # DevOps
    "docker": ["docker", "containers"],
    "kubernetes": ["kubernetes", "k8s"],
    "terraform": ["terraform"],
    "ansible": ["ansible"],
    "jenkins": ["jenkins"],
    "github actions": ["github actions", "github workflows", "git-based"],
    "ci/cd": ["ci/cd", "continuous integration", "continuous deployment"],

    # Data / ML
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning"],
    "artificial intelligence": ["ai", "artificial intelligence"],
    "llms": ["llm", "large language models"],
    "nlp": ["nlp", "natural language processing"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "data analysis": ["data analysis", "analytics"],
    "data engineering": ["data engineering", "etl"],
    "spark": ["spark", "apache spark"],

    # APIs
    "rest api": ["rest", "rest api", "restful"],
    "graphql": ["graphql"],
    "grpc": ["grpc"],
    "microservices": ["microservices", "microservice architecture"],

    # Security
    "cybersecurity": ["cybersecurity", "information security"],
    "oauth": ["oauth"],
    "sso": ["single sign-on", "sso"],
    "iam": ["identity and access management", "iam"],
    "penetration testing": ["penetration testing", "pentesting"],
    "soc": ["security operations center", "soc"],

    # Tools
    "git": ["git"],
    "github": ["github", "git", "git-based"],
    "gitlab": ["gitlab"],
    "jira": ["jira"],
    "linux": ["linux"],
    "unix": ["unix"],
    "bash": ["bash", "shell scripting"],
    "powershell": ["powershell"],

    # Methodologies
    "agile": ["agile"],
    "scrum": ["scrum"],
    "kanban": ["kanban"],
    "test driven development": ["tdd", "test driven development"],
    "object oriented programming": ["oop", "object oriented programming"],

    # Soft Skills
    "communication": ["communication", "verbal communication", "written communication"],
    "leadership": ["leadership", "team leadership"],
    "teamwork": ["teamwork", "collaboration", "cross-functional collaboration"],
    "problem solving": ["problem solving", "critical thinking"],
    "time management": ["time management"],
    "adaptability": ["adaptability", "flexibility"],
    "mentoring": ["mentoring", "coaching"],
    "project management": ["project management"],
    "stakeholder management": ["stakeholder management"],
    "customer service": ["customer service"],
    "presentation skills": ["presentation skills", "public speaking"],
    "attention to detail": ["attention to detail"],
    "analytical thinking": ["analytical thinking"],
    "decision making": ["decision making"],
    "conflict resolution": ["conflict resolution"]
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