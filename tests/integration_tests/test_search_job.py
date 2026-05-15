import pytest
from search.search import search_jobs

@pytest.mark.asyncio
async def test_search_with_resume():

    resume = "Python AWS SQL"

    profile = {
        "skills": ["Python", "AWS", "SQL"]
    }

    jobs = await search_jobs(resume, profile, k=5)

    assert len(jobs) > 0