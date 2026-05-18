from ranking.faiss_index import get_or_build_index
import asyncio
from resume.resume import build_user_profile
from resume.ui import load_resume_interactive
from search.search import search_jobs

async def main():
    index_wrapper = await get_or_build_index()
    index = index_wrapper.index

    print("Total vectors:", index.ntotal)

    for i in range(min(5, index.ntotal)):
        vector = index.reconstruct(i).reshape(1, -1)

        D, I = index.search(vector, k=5)

        print(f"\nVector {i} nearest neighbors:")

        for score, idx in zip(D[0], I[0]):
            print(f"Index={idx} Score={score}")

    resume_text = load_resume_interactive()
    profile = build_user_profile(resume_text)
    results = await search_jobs(resume_text, profile)

if __name__ == '__main__':
    asyncio.run(main())