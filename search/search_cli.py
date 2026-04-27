import asyncio
from search.search import search_jobs
from resume.resume import build_user_profile
from resume.ui import load_resume_interactive


async def main(debug=False):
    resume_text = load_resume_interactive()
    profile = build_user_profile(resume_text)

    if debug:
        print("Profile loaded:")
        print(profile)

    results = await search_jobs(resume_text, profile, k=10)

    print("\nTop Matches:\n")

    for i, job in enumerate(results, 1):
        print(f"{i}. {job['title']} @ {job['company']} ({job['location']}) - {job['score']:.2f} | {job['faiss_score']:.2f}")
        if debug:
            print("JOB:", job["skills"])


if __name__ == "__main__":
    debug = False
    asyncio.run(main(debug))