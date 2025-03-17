import json
import time
import requests
from bs4 import BeautifulSoup
import markdownify
from flask import current_app
from app import cache
from app.llm import summarize_text
from app.database import store_article, get_article, store_links, get_links, get_summary, store_summaries
import re

# Wikipedia API Endpoint
WIKI_API_URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "WikiTutorBot/1.0 (andy.n.brandt@gmail.com)",
    "Accept-Encoding": "gzip"
}


def get_cache():
    """Returns the Flask cache instance inside an application context."""
    with current_app.app_context():
        if not cache:
            raise RuntimeError("Flask cache is NOT initialized! Ensure cache.init_app(app) was called in `app/__init__.py`.")
        return cache


def get_internal_links(topic):
    """Fetch internal links for a Wikipedia article, using Flask-Caching."""
    cache = get_cache()

    cached_links = cache.get(f"links:{topic}")
    if cached_links:
        print(f"✅ Retrieved internal links for '{topic}' from Redis cache.")
        return cached_links

    # ✅ Check the database
    stored_links = get_links(topic)
    if stored_links:
        print(f"✅ Retrieved internal links for '{topic}' from database.")
        cache.set(f"links:{topic}", stored_links, timeout=86400)  # ✅ Cache for 1 day
        return stored_links

    # ✅ Fetch from Wikipedia API if not cached
    print(f"🌍 Fetching internal links for '{topic}' from Wikipedia API...")

    params = {
        "action": "parse",
        "format": "json",
        "page": topic,
        "prop": "text",
        "redirects": 1
    }

    time.sleep(0.1)
    response = requests.get(WIKI_API_URL, params=params, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    if "parse" not in data:
        return None

    soup = BeautifulSoup(data["parse"]["text"]["*"], "lxml")
    content_div = soup.select_one("div.mw-parser-output")
    if not content_div:
        return None

    seen_links = set()
    for p in content_div.find_all("p", recursive=False):
        for a in p.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/wiki/") and ":" not in href:
                topic_name = href.split("/wiki/")[-1].split("#")[0]
                seen_links.add(topic_name)

    final_links = list(seen_links)

    # ✅ Store in database & Cache
    store_links(topic, final_links)
    cache.set(f"links:{topic}", final_links, timeout=86400)  # ✅ Cache for 1 day

    print(f"📝 Stored internal links for '{topic}' in database and Redis.")

    return final_links




def get_article_text(topic):
    """Fetch Wikipedia article intro from cache or database. If missing, fetch it from Wikipedia and store only the intro."""
    print(f"🔍 Checking database for '{topic}' intro section...")

    stored_article = get_article(topic)  # ✅ Ensure this only returns the intro

    if stored_article:
        print(f"✅ Retrieved intro section of '{topic}' from database.")
        cache.set(f"article:{topic}", stored_article, timeout=86400)  # ✅ Cache it for fast access
        return stored_article
    else:
        print(f"⚠️ Article '{topic}' not found in database. Fetching intro from Wikipedia...")

    # ✅ Fetch from Wikipedia API
    intro_text = fetch_wikipedia_intro(topic)  # ✅ Ensure this only extracts the intro

    if intro_text:
        print(f"📝 Storing intro section of '{topic}' in database...")
        store_article(topic, intro_text)  # ✅ Store **only the intro** in SQLite
        cache.set(f"article:{topic}", intro_text, timeout=86400)  # ✅ Cache intro
        return intro_text
    else:
        print(f"❌ Could not retrieve intro section for '{topic}'.")
        return None  # Fail gracefully


def fetch_wikipedia_intro(topic):
    """Fetches all paragraphs from the Wikipedia intro section and stops at <div class='mw-heading mw-heading2'>."""
    print(f"🌍 Fetching intro section for '{topic}' from Wikipedia API...")

    params = {
        "action": "parse",
        "format": "json",
        "page": topic,
        "prop": "text",
        "redirects": 1
    }

    response = requests.get(WIKI_API_URL, params=params, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    if "parse" not in data:
        print(f"❌ Wikipedia API did not return expected data for '{topic}'")
        return None

    soup = BeautifulSoup(data["parse"]["text"]["*"], "lxml")
    content_div = soup.select_one("div.mw-parser-output")

    if not content_div:
        print(f"❌ No content found for '{topic}'")
        return None

    # ✅ Extract all paragraphs until reaching <div class="mw-heading mw-heading2">
    intro_text = []
    for element in content_div.children:
        # ✅ Stop at <div class="mw-heading mw-heading2">
        if element.name == "div" and "mw-heading2" in element.get("class", []):
            print("⛔ Stopping extraction at first <div class='mw-heading mw-heading2'>")
            break

        # ✅ Capture paragraph text
        if element.name == "p" and element.text.strip():
            intro_text.append(str(element))

    if not intro_text:
        print(f"❌ No valid intro text found for '{topic}'")
        return None

    # ✅ Convert HTML to markdown format
    markdown_text = markdownify.markdownify("".join(intro_text), heading_style="ATX")

    # ✅ Remove Wikipedia citations like [1], [2], etc.
    markdown_text = re.sub(r"\[\d+\]", "", markdown_text)

    # ✅ Strip extra whitespace
    markdown_text = markdown_text.strip()

    # ✅ Debugging: Print the extracted intro
    print(f"📝 Final Extracted Intro (first 500 chars):\n{markdown_text[:500]}...")

    return markdown_text


def get_summarized_article(topic, level="basic"):
    """
    Retrieves a Wikipedia article summary at a given level.
    If the summary is missing, generate all 3 levels at once and store them.
    """
    # ✅ Check if the requested summary already exists in the database
    print(f"🔍 Checking for {level} summary of '{topic}' in database.")
    existing_summary = get_summary(topic, level)
    if existing_summary:
        print(f"✅ Retrieved {level} summary of '{topic}' from database.")
        return existing_summary  # ✅ Ensure returning the correct data type

    # ✅ If missing, fetch the full article text
    print(f"🔍 '{topic}' summary not found in database, searching Wikipedia")
    article_text = get_article_text(topic)
    if not article_text:
        print(f"❌ Error: Could not retrieve article text for '{topic}'.")
        return None  # If the article itself isn't available, return nothing

    # ✅ Generate all 3 summaries in a single LLM call (cost-efficient)
    summaries_dict = summarize_text(article_text)

    # ✅ Ensure summaries_dict is a dictionary
    if not isinstance(summaries_dict, dict):
        print(f"❌ Error: Expected a dictionary but got {type(summaries_dict)}. Cannot store summaries.")
        return None  # Handle error gracefully

    # ✅ Store summaries only if they are valid
    store_summaries(topic, summaries_dict)
    print(f"📝 Stored all summaries for '{topic}' in database.")

    # ✅ Return only the summary requested by the user (or None if missing)
    return summaries_dict.get(level)




def invalidate_cache(topic):
    """Manually remove a topic from Redis cache."""
    cache = get_cache()
    cache.delete(f"article:{topic}")
    cache.delete(f"links:{topic}")
    print(f"🗑️ Cache invalidated for '{topic}'. Fresh data will be fetched next time.")


if __name__ == "__main__":
    topic = "Logic"  # ✅ Change this for testing different articles

    print(f"\n🔍 Checking database and cache for internal links for: {topic}")
    internal_links = get_internal_links(topic)

    if internal_links:
        print(f"✅ Internal links retrieved for '{topic}' ({len(internal_links)} found).")
    else:
        print(f"❌ No internal links found for '{topic}'.")

    print("\n🔗 Internal Links (First 10 for preview):", internal_links[:10])

    print(f"\n🔍 Checking database and cache for article text for: {topic}")
    article_text = get_article_text(topic)

    if article_text:
        print(f"✅ Article text successfully retrieved for '{topic}'.")
    else:
        print(f"❌ Failed to retrieve article text for '{topic}'.")

    print("\n📄 Article Content (First 500 characters preview):")
    print(article_text[:500] + "..." if article_text else "❌ No content available.")
