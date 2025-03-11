# app/wikipedia.py
import requests
import time
from .utils import clean_text
from app import cache

WIKI_API_URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "WikiTutorBot/1.0 (andy.n.brandt@gmail.com)",
    "Accept-Encoding": "gzip"  # Compress responses to reduce bandwidth
}

@cache.memoize()
def get_article_content(title):
    """
    Fetch the full main article content using the MediaWiki query API.
    Returns a tuple: (official_title, cleaned plain text content).
    """
    title = title.replace("_", " ")
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts|info",
        "titles": title,
        "explaintext": True,
        "redirects": 1,
        "inprop": "url"
    }

    time.sleep(0.1)  # Delay to prevent API spam

    try:
        response = requests.get(WIKI_API_URL, params=params, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        return (title, f"Error fetching data: {e}")

    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return (title, "Page not found")

    page = list(pages.values())[0]
    official_title = page.get("title", title)
    content = page.get("extract", "")
    if content:
        return (official_title, clean_text(content))
    return (official_title, "Page not found")


def get_lead_links_filtered(official_title):
    """
    Fetches all internal links from the lead section and then filters them to only
    include links that appear in the plain text extract of the lead section.
    """
    # First, get the plain text extract of the lead section
    normalized_title = official_title.strip()

    # Use the query API to get the plain text extract
    params_extract = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "titles": normalized_title,
        "explaintext": True,
        "redirects": 1,
        # You might use additional parameters or custom logic to try to isolate just the lead section.
    }
    try:
        response = requests.get(WIKI_API_URL, params=params_extract, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException:
        return []

    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    page = list(pages.values())[0] if pages else {}
    plain_text = page.get("extract", "")

    # Now get the links using the parse API as before
    params_links = {
        "action": "parse",
        "page": normalized_title,
        "format": "json",
        "prop": "links",
        "section": "0"
    }
    try:
        response = requests.get(WIKI_API_URL, params=params_links, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException:
        return []

    data = response.json()
    links = data.get("parse", {}).get("links", [])
    raw_links = [link["*"] for link in links if link.get("ns") == 0]

    # Filter out links that don't appear in the plain text extract
    filtered_links = []
    for link in raw_links:
        # Normalize both strings for a simple substring check
        if link.strip().lower() in plain_text.lower():
            filtered_links.append(link)

    return filtered_links

