from ingestion.utils import extract_seniority, extract_skills

async def enrich_job(page, url):
    # 1. NAVIGATION (safe mode)
    try:
        await page.goto(url, wait_until="commit", timeout=90000)
    except:
        return None

    await page.wait_for_timeout(5000)

    print("URL:", page.url)

    # 2. SHELL PAGE DETECTION
    html = await page.content()

    is_shell = (
        "<h1" not in html and
        "show-more-less" not in html and
        len(html) < 5000
    )

    if is_shell:
        print("Shell page detected")

    # 3. HYDRATION ATTEMPT
    await page.mouse.wheel(0, 800)
    await page.wait_for_timeout(3000)

    # 4. EXTRACTION LAYER (DOM)
    async def extract_title():
        selectors = [
            "h1",
            ".top-card-layout__title",
            ".topcard__title"
        ]

        for sel in selectors:
            try:
                val = await page.locator(sel).first.text_content(timeout=3000)
                if val:
                    return val.strip()
            except:
                continue

        return ""

    async def extract_company():
        selectors = [
            "a.topcard__org-name-link",
            ".topcard__flavor",
        ]

        for sel in selectors:
            try:
                val = await page.locator(sel).first.text_content(timeout=3000)
                if val:
                    return val.strip()
            except:
                continue

        return ""

    async def extract_location():
        try:
            return await page.locator(".topcard__flavor--bullet").first.text_content(timeout=3000)
        except:
            return ""

    async def extract_description():
        try:
            return await page.locator(".show-more-less-html__markup").first.text_content(timeout=5000)
        except:
            return ""

    # 5. EXECUTE EXTRACTION
    title = await extract_title()
    company = await extract_company()
    location = await extract_location()
    description = await extract_description()

    # 6. FALLBACK LAYER (CRITICAL)
    if not title:
        try:
            title = await page.title()
        except:
            title = ""

    if not title:
        slug = url.split("/jobs/view/")[-1].split("?")[0]
        title = slug.replace("-", " ")

    # 7. RETURN STRUCTURED DATA
    return {
        "title": title,
        "company": company,
        "location": location,
        "description": description,
        "skills": extract_skills(description),
        "seniority": extract_seniority(description)
    }

