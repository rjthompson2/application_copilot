from collections import defaultdict


def rank_contacts(contacts):
    grouped = defaultdict(lambda: {
        "count": 0,
        "queries": set(),
        "title": "",
        "url": "",
        "score": 0
    })

    for result in contacts:

        key = result.search_url

        grouped[key]["count"] += 1
        grouped[key]["queries"].add(result.name)
        grouped[key]["title"] = result.title

    final_results = []

    for url, item in grouped.items():

        score = 0

        title = item["title"].lower()

        # Base relevance
        if "recruit" in title or "talent acquisition" in title:
            score += 30

        if "engineering manager" in title:
            score += 25

        # Strong LinkedIn profile indicator
        if "/in/" in url:
            score += 40

        # Penalize non-person pages
        if "/jobs/" in url:
            score -= 50

        if "/company/" in url:
            score -= 40

        if "/posts/" in url or "/activity/" in url:
            score -= 30


        # Duplicate boost
        score += item["count"] * 15

        # Multiple search categories boost
        score += len(item["queries"]) * 10

        final_results.append({
            "title": item["title"],
            "url": url,
            "queries_matched": list(item["queries"]),
            "appearances": item["count"],
            "score": score
        })

    final_results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return final_results