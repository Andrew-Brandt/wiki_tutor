from flask import Blueprint, request, jsonify
from app.wikipedia import get_article_text, get_internal_links, get_summary, get_summarized_article  # ✅ Import functions properly


main = Blueprint("main", __name__)

@main.route("/topic/<topic>", methods=["GET"])
def topic_data(topic):
    """
    Retrieves only the stored intro section and internal links.
    """
    max_links = int(request.args.get("max_links", 1000))  # Default: 1000 links
    nocache = request.args.get("nocache", "false").lower() == "true"

    print(f"\n🔍 Request received for topic: {topic} (nocache={nocache})")

    # ✅ Get only the intro section from cache or database
    article_intro = get_article_text(topic) if not nocache else None

    if not article_intro:
        return jsonify({"error": f"Error retrieving data for topic: {topic}"}), 500

    # ✅ Retrieve internal links
    internal_links = get_internal_links(topic) if not nocache else None

    # ✅ Return ONLY the intro and links (Remove full_text & official_title)
    data = {
        "topic": topic,
        "intro_text": article_intro,  # ✅ Returns only the intro
        "internal_links": internal_links[:max_links] if internal_links else []
    }

    print(f"✅ Successfully retrieved intro section for '{topic}'.")

    return jsonify(data)




@main.route("/summary/<topic>", methods=["GET"])
def get_summary_route(topic):
    """Retrieves a summary of a Wikipedia article at a specified level."""
    level = request.args.get("level", "basic").lower()  # Default to 'basic'
    nocache = request.args.get("nocache", "false").lower() == "true"

    print(f"\n🔍 Request received for summary: {topic} (level={level})")

    # ✅ Use the correct function to fetch or generate summaries
    stored_summary = get_summarized_article(topic, level)

    if stored_summary:
        print(f"✅ Returning summary for '{topic}' at level '{level}'.")
        return jsonify({"topic": topic, "level": level, "summary": stored_summary})

    return jsonify({"error": f"Failed to retrieve summary for '{topic}'"}), 500



