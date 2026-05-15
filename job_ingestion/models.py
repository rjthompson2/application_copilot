from dataclasses import dataclass
from typing import Optional

@dataclass
class Job:
    external_id: str
    source: str

    title: str
    company: str
    location: str

    url: str
    description: str

    salary: Optional[str] = None
    seniority: Optional[str] = None