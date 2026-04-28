from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
import aiosqlite

from search.search import search_jobs
from app.main import templates
from config import DB_NAME, RESUME_FILE
import os
from resume.resume import build_user_profile, load_resume_file, load_resume


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "jobs": []}
    )


@router.post("/search", response_class=HTMLResponse)
async def run_search(request: Request, file: UploadFile = File(None), use_saved: str = Form(None)):
    resume_text = None
    profile = None

    # Upload new resume
    if file and file.filename:
        content = await file.read()
        with open(RESUME_FILE, "wb") as f:
            f.write(content)

        resume_text = load_resume_file(RESUME_FILE)
        profile = build_user_profile(resume_text)
    
    # Use saved doesn't exist
    elif use_saved == "true" and not os.path.exists(RESUME_FILE):
        print("Error: File does not exist")
        profile = None

    # Use saved resume
    elif use_saved == "true":
        try:
            resume_text = load_resume(RESUME_FILE)
            profile = build_user_profile(resume_text)
        except Exception as e:
            print(e)
            resume_text = None
            profile = None

    # No resume → leave as None

    jobs = await search_jobs(resume_text, profile, k=20)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "jobs": jobs,
            "has_resume": profile is not None
        }
    )


# @router.post("/search", response_class=HTMLResponse)
# async def run_search(request: Request, file: UploadFile = File(None)):
#     resume_text = None
#     profile = None

#     # Check if user uploaded a file
#     if file and file.filename:
#         content = await file.read()

#         with open(RESUME_FILE, "wb") as f:
#             f.write(content)

#         resume_text = load_resume(RESUME_FILE)
#         profile = build_user_profile(resume_text)

#     # Run search (with or without profile)
#     jobs = await search_jobs(resume_text, profile, k=20)

#     return templates.TemplateResponse(
#         "index.html",
#         {
#             "request": request,
#             "jobs": jobs,
#             "has_resume": profile is not None
#         }
#     )


@router.post("/save/{job_id}")
async def save_job(job_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE jobs SET saved=1 WHERE id=?", (job_id,))
        await db.commit()

    return RedirectResponse("/", status_code=303)


@router.post("/apply/{job_id}")
async def apply_job(job_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE jobs SET applied=1 WHERE id=?", (job_id,))
        await db.commit()

    return RedirectResponse("/", status_code=303)