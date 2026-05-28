from dataclasses import dataclass

@dataclass
class Contact:
    name: str
    title: str
    company: str
    search_url: str = ""
    relevance_score: float = 0.0
    contact_type: str = "unknown"