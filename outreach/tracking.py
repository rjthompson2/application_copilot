import aiosqlite
from utils import DB_NAME


async def save_outreach(
    job_id,
    contact_name,
    contacted=False,
    responded=False
):
    query = """
    INSERT INTO outreach_history (
        job_id,
        contact_name,
        contacted,
        responded
    )
    VALUES (?, ?, ?, ?)
    """

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            query,
            (
                job_id,
                contact_name,
                contacted,
                responded
            )
        )

        await db.commit()