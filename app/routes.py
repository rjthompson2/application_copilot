from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import aiosqlite
from outreach.search import find_contacts
from outreach.templates import get_outreach_angle
from search.search import search_jobs
from app.main import templates
from utils import DB_NAME, RESUME_FILE,CONFIG_PATH
import os
from resume.resume import build_user_profile, load_resume, extract_upload
from job_ingestion.main import main as ingest_jobs
from resume.resume import parse_resume
from outreach.provider import PlaywrightLinkedInProvider
from outreach.search import set_provider, find_contacts
from config import SEARCH_QUERY, LOCATION
import traceback


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    resume_text = None
    profile = None

    # Use saved resume
    if os.path.exists(RESUME_FILE):
        try:
            resume_text = load_resume(RESUME_FILE)
            profile = build_user_profile(resume_text)
        except Exception as e:
            print("ERROR:", e)
            print("TRACEBACK:", traceback.format_exc())
            resume_text = None
            profile = None
    else:
        return RedirectResponse("/settings", status_code=307)

    # No resume → leave as None
    jobs = await search_jobs(resume_text, profile)
    resume = parse_resume(resume_text)
    matching_missing = {}

    for job in jobs:
        skills = job['skills'].split(",")

        matching_skills = [skill for skill in skills if skill in resume["skills"]]
        missing_skills = [skill for skill in skills if skill not in resume["skills"]]

        if len(missing_skills) == 0:
            missing_skills = ['none']
        if len(matching_skills) == 0:
            matching_skills = ['none']

        matching_missing[job["id"]] = {"matching": matching_skills, "missing": missing_skills}
    

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "jobs": jobs,
            "matching_missing": matching_missing,
            "has_resume": profile is not None
        }
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


@router.get("/outreach/{job_id}")
async def outreach(job_id: int):

    set_provider(PlaywrightLinkedInProvider())
    contacts, title = await find_contacts(job_id)

    angle = get_outreach_angle(
        title
    )

    if not contacts:
        return {
            "contacts": [],
            "success": False
        }

    print(contacts)

    return JSONResponse({
        "contacts": [
            {
                "title": c['title'],
                "url": c['url'],
                "score": c['score'],
                "appearances": c['appearances']
            }
            for c in contacts if c['score'] > 0
        ],

        "suggested_angle": angle
    })


@router.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    settings = {
        "Search Query": SEARCH_QUERY,
        "Location": LOCATION
    }
    
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request, 
            "settings": settings
        }
    )

@router.get("/waiting", response_class=HTMLResponse)
async def loading_screen(request: Request):
    return templates.TemplateResponse(
        "loading.html",
        {
            "request": request
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

@router.post("/settings/save", response_class=HTMLResponse)
async def settings(request: Request):
    print("Saving...")
    form = await request.form()

    
    config_string = ""
    for key, value in form.items():
        key = key.replace(" ", "_").upper()
        config_string += key + ' = "' + value + '"\n'
        print(key+":", value)
    
    config_string += 'MAX_PAGES = 3'

    with open(CONFIG_PATH, "w") as config_file:
        config_file.write(config_string)

    return RedirectResponse("/settings", status_code=303)

@router.post("/settings/resume", response_class=HTMLResponse)
async def upload_resume(request: Request, file: UploadFile = File(None)):
    # Upload new resume
    if not file or not file.filename:
        return RedirectResponse("/settings", status_code=400)
    
    resume_text = await extract_upload(file)
    RESUME_FILE.write_text(resume_text, encoding="utf-8")
    return RedirectResponse("/settings", status_code=303)