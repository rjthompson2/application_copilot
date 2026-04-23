import asyncio
from search.search import search_jobs
from resume.resume import load_resume
from config import RESUME_FILE


async def main():
    resume_text = load_resume(RESUME_FILE)

    results = await search_jobs(resume_text, k=10)

    print("\nTop Matches:\n")

    for i, job in enumerate(results, 1):
        print(f"{i}. {job[1]} @ {job[2]} ({job[3]})")


if __name__ == "__main__":
    asyncio.run(main())