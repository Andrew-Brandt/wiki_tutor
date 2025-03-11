# app/routes.py
from flask import Blueprint, jsonify
from .wikipedia import get_article_content, get_lead_links_filtered

main = Blueprint('main', __name__)


@main.route("/")
def home():
    return jsonify({"message": "Wiki Tutor API is running!"})


@main.route("/topic/<topic>", methods=["GET"])
def fetch_topic(topic):
    # Fetch the main article content and official title.
    official_title, main_content = get_article_content(topic)
    # Retrieve the lead links using the official title.
    lead_links = get_lead_links_filtered(official_title)

    # Limit the number of lead links processed (adjust as needed)
    max_links = 5
    lead_links = lead_links[:max_links]

    # Fetch article content for each lead link
    lead_link_contents = {}
    for link in lead_links:
        _, link_content = get_article_content(link)
        lead_link_contents[link] = link_content

    return jsonify({
        "topic": official_title,
        "main_content": main_content,
        "lead_links": lead_links,
        "lead_link_contents": lead_link_contents
    })
