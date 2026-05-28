from outreach.models import Contact
from outreach.ranking import rank_contacts
from job_database.database import get_title
from outreach.provider import LinkedInProvider


provider = None


def set_provider(p):
    global provider
    provider = p


async def find_contacts(job_id):
    job = await get_title(job_id)

    job = job[0]
    company = job[0]
    title = job[1]

    raw_contacts = await provider.search_people(
        company,
        title
    )

    contacts = []

    for c in raw_contacts:
        contact = Contact(
            name=c["query"],
            title=c["title"],
            company=c["company"],
            search_url=c["search_url"]
        )

        contacts.append(contact)

    ranked = rank_contacts(
        contacts
    )

    return ranked, title