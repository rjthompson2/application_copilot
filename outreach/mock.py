from outreach.models import Contact
from outreach.ranking import rank_contacts


MOCK_CONTACTS = {
    "OpenAI": [
        {
            "name": "Sarah Chen",
            "title": "Technical Recruiter",
            "linkedin_url":
                "https://linkedin.com/in/sarahchen"
        },

        {
            "name": "Michael Patel",
            "title": "Engineering Manager",
            "linkedin_url":
                "https://linkedin.com/in/michaelpatel"
        },

        {
            "name": "Emily Rodriguez",
            "title": "Senior Backend Engineer",
            "linkedin_url":
                "https://linkedin.com/in/emilyrodriguez"
        }
    ]
}


async def mock_linkedin_search(company):

    return MOCK_CONTACTS.get(company, [])


async def run_mock():

    job = {
        "title": "Backend Engineer",
        "company": "OpenAI"
    }

    raw_contacts = await mock_linkedin_search(
        job["company"]
    )

    contacts = []

    for c in raw_contacts:

        contact = Contact(
            name=c["name"],
            title=c["title"],
            company=job["company"],
            linkedin_url=c["linkedin_url"]
        )

        contacts.append(contact)

    ranked = rank_contacts(
        contacts,
        job["title"]
    )

    print("\n=== Ranked Contacts ===\n")

    for contact in ranked:

        print(
            f"""
Name: {contact.name}
Title: {contact.title}
Company: {contact.company}
Score: {contact.relevance_score}
LinkedIn: {contact.linkedin_url}
"""
        )


if __name__ == "__main__":

    import asyncio

    asyncio.run(run_mock())