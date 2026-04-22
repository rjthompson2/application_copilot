import asyncio
import random
from playwright.async_api import async_playwright

STORAGE_FILE = "auth.json"

# login utils
async def save_login_state():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        context = await browser.new_context()
        page = await context.new_page()

        # Go to LinkedIn login
        await page.goto("https://www.linkedin.com/login")

        print("👉 Log in manually, then press ENTER here...")
        input()

        # Save session (cookies + localStorage)
        await context.storage_state(path=STORAGE_FILE)
        print(f"✅ Saved session to {STORAGE_FILE}")

        await browser.close()
    

async def login_and_save(context):
    page = await context.new_page()

    await page.goto("https://www.linkedin.com/login")

    print("Please log in manually...")

    # wait until user is actually logged in
    while "login" in page.url:
        await page.wait_for_timeout(3000)

    # save session
    await context.storage_state(path="auth.json")
    print("Saved auth.json")


async def is_logged_in(page):
    await page.goto("https://www.linkedin.com/feed", wait_until="domcontentloaded")

    # If redirected to login page → not logged in
    if "login" in page.url:
        return False

    # Extra safety check: look for profile icon
    try:
        await page.wait_for_selector("img.global-nav__me-photo", timeout=5000)
        return True
    except:
        return False


# extraction
SKILLS = [
    "python","java","go","aws","docker","kubernetes",
    "sql","react","node","typescript","c++"
]

def extract_skills(text):
    if not text:
        return ""
    t = text.lower()
    return ",".join([s for s in SKILLS if s in t])


def extract_seniority(text):
    if not text:
        return "unknown"
    t = text.lower()

    if "staff" in t or "principal" in t:
        return "staff"
    if "senior" in t:
        return "senior"
    if "lead" in t:
        return "lead"
    if "intern" in t:
        return "intern"
    return "mid"


# human mimicking
async def human_delay():
    await asyncio.sleep(2 + random.random() * 2)


# safe extractions
async def safe_text(locator, timeout=5000):
    try:
        return (await locator.first.text_content(timeout=timeout) or "").strip()
    except:
        return ""
    
async def safe_attr(locator, attr):
    try:
        return await locator.first.get_attribute(attr, timeout=5000)
    except:
        return None