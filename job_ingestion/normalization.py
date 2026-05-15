import re
from urllib.parse import urlparse, parse_qs


def normalize_url(url: str) -> str:
    """
    Remove tracking params and normalize job URLs
    """

    try:
        parsed = urlparse(url)

        # remove query params except key job identifiers
        qs = parse_qs(parsed.query)

        keep_params = {}

        for k in ["jk", "vjk", "id"]:
            if k in qs:
                keep_params[k] = qs[k][0]

        clean_query = "&".join([f"{k}={v}" for k, v in keep_params.items()])

        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{clean_query}".rstrip("?")

    except:
        return url


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9\s\-\+]", "", text)

    return text.strip()


def make_job_signature(title: str, company: str, location: str) -> str:
    """
    Core dedupe key (fast layer)
    """

    return normalize_text(f"{title}|{company}|{location}")