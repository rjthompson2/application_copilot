OUTREACH_ANGLES = {
    "backend": (
        "Mention backend APIs, scalability, "
        "and distributed systems experience."
    ),

    "data": (
        "Highlight ETL pipelines, analytics, "
        "and database work."
    ),

    "security": (
        "Mention security tooling, threat analysis, "
        "or compliance experience."
    )
}


def get_outreach_angle(job_title):
    title = job_title.lower()

    if "backend" in title:
        return OUTREACH_ANGLES["backend"]

    if "data" in title:
        return OUTREACH_ANGLES["data"]

    if "security" in title:
        return OUTREACH_ANGLES["security"]

    return (
        "Highlight relevant technical experience "
        "and interest in the role."
    )