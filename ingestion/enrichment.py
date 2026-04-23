from ingestion.utils import extract_seniority, extract_skills
import json

REQUIRED_FIELDS = ["title", "company", "location"]

# CONFIDENCE WEIGHTS
CONFIDENCE = {
    "meta": .99,
    "jsonld": 0.95,
    "dom": 0.7,
    "title_parse": 0.75,
    "description": 1.0,
    "body": 0.4
}


# HELPER: choose best value
def choose_best(candidates):
    """
    candidates = [(value, confidence)]
    """
    best_val = ""
    best_score = -1

    for val, score in candidates:
        if val and score > best_score:
            best_val = val.strip()
            best_score = score

    return best_val


# UTILS
def parse_meta_title(meta):
    if not meta:
        return "", ""

    meta = meta.replace(" | LinkedIn", "")

    if "|" in meta:
        title, company = meta.split("|")
        return title.strip(), company.strip()

    return meta.strip(), ""


def extract_location_from_description(description):
    keyword = "Location:"

    for line in description.split("\n"):
        clean = line.strip()

        if keyword.lower() in clean.lower():
            parts = clean.split(":")
            if len(parts) > 1:
                value = parts[1].strip()
                return value
                


def clean_text(text):
    if not text:
        return ""

    text = text.replace("Skip to main content", "")
    text = text.strip()

    if "(" in text:
        text = text.split("(")[0].strip()

    return text


# MAIN FUNCTION
async def enrich_job(page, url):

    # 1. NAVIGATION
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=90000)
    except:
        return None

    print("\nURL:", url)

    await page.wait_for_timeout(3000)

    # 2. HYDRATION
    for _ in range(3):
        await page.mouse.wheel(0, 2500)
        await page.wait_for_timeout(1500)

    try:
        btn = page.locator("button:has-text('See more')")
        if await btn.count() > 0:
            await btn.first.click()
    except:
        pass

    # 3. PAGE EXTRACTION
    page_title = await page.title()

    title_meta, company_meta = parse_meta_title(page_title)

    # 4. JSON-LD EXTRACTION
    title_json = ""
    company_json = ""

    try:
        scripts = page.locator('script[type="application/ld+json"]')

        for i in range(await scripts.count()):
            try:
                raw = await scripts.nth(i).inner_text()
                data = json.loads(raw)

                if isinstance(data, dict):
                    title_json = data.get("title", "")

                    org = data.get("hiringOrganization", {})
                    if isinstance(org, dict):
                        company_json = org.get("name", "")
            except:
                continue
    except:
        pass

    # 5. DESCRIPTION (About section)
    section = page.locator("h2:has-text('About the job')")
    description = ""

    if await section.count() > 0:
        try:
            container = section.locator("xpath=ancestor::*[3]")
            description = await container.inner_text()
        except:
            description = ""

    # fallback
    if not description:
        try:
            description = await page.locator(
                ".jobs-description__content"
            ).first.inner_text()
        except:
            description = ""

    # 6. LOCATION (DOM)
    location_dom = ""

    selectors = [
        "span.jobs-unified-top-card__bullet",
        ".topcard__flavor--bullet",
        "div.topcard__flavor-row span",
    ]

    for sel in selectors:
        try:
            el = page.locator(sel)
            if await el.count() > 0:
                val = await el.first.inner_text()

                if val and ("," in val or "Remote" in val):
                    location_dom = val.strip()
                    break
        except:
            continue

    # 7. BODY FALLBACK
    body_text = await page.inner_text("body")

    location_body = ""
    for line in body_text.split("\n"):
        if "," in line and len(line) < 60:
            location_body = line.strip()
            break

    location_desc = extract_location_from_description(description)

    # 8. BUILD CANDIDATES
    title = choose_best([
        (title_meta, CONFIDENCE["meta"]),
        (title_json, CONFIDENCE["jsonld"])
    ])

    company = choose_best([
        (company_meta, CONFIDENCE["meta"]),
        (company_json, CONFIDENCE["jsonld"]),
    ])

    location = choose_best([
        (location_dom, CONFIDENCE["dom"]),
        (location_body, CONFIDENCE["body"]),
        (location_desc, CONFIDENCE["description"])
    ])
    # 9. VALIDATION
    field_map = {
        "title": title,
        "company": company,
        "location": location,
    }

    missing = [k for k, v in field_map.items() if v != ""]

    if missing:
        print("Missing fields:", missing, url)

    # 10. RETURN 
    return {
        "title": clean_text(title),
        "company": clean_text(company),
        "location": clean_text(location),
        "description": description or "",
        "skills": extract_skills(description or ""),
        "seniority": extract_seniority(description or "")
    }