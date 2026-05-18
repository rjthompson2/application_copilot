from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import aiosqlite

from search.search import search_jobs
from app.main import templates
from utils import DB_NAME, RESUME_FILE
import os
from resume.resume import build_user_profile, load_resume, extract_upload
from job_ingestion.main import main as ingest_jobs


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "jobs": []}
    )


@router.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
            SELECT id, title, company, location, url, description
            FROM jobs
            WHERE status = 'saved'
            ORDER BY created_at DESC
        """)

        rows = await cursor.fetchall()

    jobs = [
        {
            "id": r[0],
            "title": r[1],
            "company": r[2],
            "location": r[3],
            "url": r[4],
            "description": r[5],
        }
        for r in rows
    ]

    return templates.TemplateResponse(
        "history.html",
        {
            "request": request,
            "jobs": jobs
        }
    )


@router.post("/search", response_class=HTMLResponse)
async def run_search(request: Request, file: UploadFile = File(None), use_saved: str = Form(None)):
    resume_text = None
    profile = None

    # Upload new resume
    if file and file.filename:
        resume_text = await extract_upload(file)
        RESUME_FILE.write_text(resume_text, encoding="utf-8")
        
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
    jobs = await search_jobs(resume_text, profile)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "jobs": jobs,
            "has_resume": profile is not None
        }
    )


@router.post("/load", response_class=HTMLResponse)
async def load_jobs(request: Request):
    await ingest_jobs()

    return JSONResponse({"success": True})

@router.post("/save/{job_id}")
async def save_job(job_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE jobs SET status='saved' WHERE id=?", (job_id,))
        await db.commit()

    return JSONResponse({"success": True, "job_id": job_id})


@router.post("/delete/{job_id}")
async def delete_job(job_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE jobs SET show='0' WHERE id=?", (job_id,))
        await db.commit()

    return JSONResponse({"success": True, "job_id": job_id})