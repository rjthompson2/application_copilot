from urllib.parse import quote


RECRUITER_KEYWORDS = [
    "recruiter",
    "technical recruiter",
    "talent acquisition",
    "staffing"
]

MANAGER_KEYWORDS = [
    "engineering manager",
    "director",
    "head of engineering",
    "team lead"
]


def build_linkedin_search_url(
    company,
    role,
    keywords=None
):
    """
    Generate a LinkedIn people search URL.
    """

    query = f"{company} {role}"

    if keywords:
        query += " " + " ".join(keywords)

    encoded = quote(query)

    return (
        "https://www.linkedin.com/search/results/people/"
        f"?keywords={encoded}"
    )


def generate_linkedin_queries(job):

    company = job["company"]
    title = job["title"]

    return [
        {
            "type": "recruiter",
            "query":
                f"{company} technical recruiter"
        },

        {
            "type": "manager",
            "query":
                f"{company} engineering manager {title}"
        },

        {
            "type": "talent",
            "query":
                f"{company} talent acquisition"
        }
    ]


def get_linkedin_search_targets(job):

    queries = generate_linkedin_queries(job)

    targets = []

    for q in queries:

        targets.append({
            "type": q["type"],

            "query": q["query"],

            "url": build_linkedin_search_url(
                company=job["company"],
                role=q["query"]
            )
        })

    return targets


def infer_department(job_title):

    title = job_title.lower()

    if "backend" in title:
        return "engineering"

    if "data" in title:
        return "data"

    if "security" in title:
        return "security"

    return "general"