from job_database.database import insert_job, get_jobs
import pytest


@pytest.mark.asyncio
async def test_save_job():

    job = {
        "title": "TEST",
        "company": "TEST",
        "location": "TEST",
        "url": "TEST",
        "source": "TEST"
    }

    await insert_job(job)

    jobs = await get_jobs()

    assert len(jobs) > 0
    assert jobs[0]["title"] == "TEST"