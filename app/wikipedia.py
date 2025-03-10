# app/wikipedia.py
import requests
import time
from .utils import clean_text

WIKI_API_URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "WikiTutorBot/1.0 (andy.n.brandt@gmail.com)",
    "Accept-Encoding": "gzip"  # Compress responses to reduce bandwidth
}


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


def get_lead_links(official_title):
    """
    Fetch internal links from the lead section (section 0) using the MediaWiki parse API.
    Returns a list of link titles (only from the main namespace), excluding any that match the official_title.
    """
    normalized_title = official_title.strip()
    params = {
        "action": "parse",
        "page": normalized_title,
        "format": "json",
        "prop": "links",
        "section": "0"  # Only the lead (intro) section
    }

    try:
        response = requests.get(WIKI_API_URL, params=params, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException:
        return []  # Return empty list on error

    data = response.json()
    links = data.get("parse", {}).get("links", [])
    # Extract titles for links in the main namespace (ns == 0)
    raw_links = [link["*"] for link in links if link.get("ns") == 0]
    # Filter out any link that exactly matches the official title (ignoring case)
    filtered_links = [
        link for link in raw_links
        if link.strip().lower() != normalized_title.lower()
    ]
    return filtered_links
