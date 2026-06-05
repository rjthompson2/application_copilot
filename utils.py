from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

LINKEDIN_URL = (
    "https://www.linkedin.com/jobs/search/"
    "?keywords={query}&location={location}&start={start}"
)


CONFIG_PATH = BASE_DIR / "application_copilot" / "config.py"

DB_NAME = BASE_DIR / "application_copilot" / "job_database" / "jobs.db"

STORAGE_FILE = BASE_DIR / "application_copilot" / "job_ingestion" / "auth.json"

RESUME_FILE = BASE_DIR / "application_copilot" / "resume" / "file" / "resume.txt"

FAISS_INDEX_PATH = BASE_DIR / "application_copilot" / "ranking" / "faiss.index"
FAISS_META_PATH = BASE_DIR / "application_copilot" / "ranking" / "faiss_meta.json"

SKILL_KEYWORDS = [
    "python", "java", "go", "aws", "docker", "kubernetes",
    "sql", "react", "node", "typescript", "gcp", "azure"
]