from config import MAX_PAGES


async def discover_jobs(context, query, location):
    page = await context.new_page()

    all_links = set()

    for p in range(MAX_PAGES):

        start = p * 25

        url = (
            "https://www.linkedin.com/jobs/search/"
            f"?keywords={query}"
            f"&location={location}"
            f"&start={start}"
        )

        print(f"Page {p+1}: {url}")

        await page.goto(url, wait_until="domcontentloaded")

        # wait for job cards instead of fixed sleep
        try:
            await page.wait_for_selector("a[href*='/jobs/view']", timeout=10000)
        except:
            print("No job links found, stopping early")
            break

        links = await page.eval_on_selector_all(
            "a[href*='/jobs/view']",
            "els => els.map(e => e.href)"
        )

        links = {
            link.split("?")[0]
            for link in links
            if link and "/jobs/view" in link
        }

        before = len(all_links)
        all_links.update(links)
        after = len(all_links)

        print(f"Found {len(links)} links, total {after}")

        # stop if no new results
        if after == before:
            print("No new jobs → stopping pagination")
            break

    await page.close()

    links = list(set(all_links))

    return links

async def extract_title(page):
    # 1. Try DOM
    try:
        title = await page.locator("h1").first.text_content(timeout=3000)
        if title:
            return title.strip()
    except:
        pass

    # 2. Meta fallback (YOU ARE HERE MOST OF THE TIME NOW)
    try:
        title = await page.title()
        if title:
            return title.strip()
    except:
        pass

    # 3. URL fallback
    try:
        slug = page.url.split("/jobs/view/")[-1].split("/")[0]
        return slug.replace("-", " ")
    except:
        return ""

async def extract_company(page):
    candidates = [
        "a.topcard__org-name-link",
        "span.topcard__flavor",
        ".job-details-jobs-unified-top-card__company-name"
    ]

    for sel in candidates:
        try:
            text = await page.locator(sel).first.text_content(timeout=3000)
            if text:
                return text.strip()
        except:
            continue

    return ""