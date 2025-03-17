import sqlite3
import json
import redis
from datetime import datetime
from app import db
from app.models import Summary
from app.models import Article

# Connect to Redis (Docker Redis is running on localhost:6379)
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

DB_FILE = "instance/app.db"

def create_tables():
    """Creates the necessary database tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Table for storing article text
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT UNIQUE NOT NULL,
        full_text TEXT NOT NULL,
        retrieved_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Table for storing internal links
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT UNIQUE NOT NULL,
        internal_links TEXT NOT NULL,
        retrieved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (topic) REFERENCES articles(topic) ON DELETE CASCADE
    )
    """)

    # Table for storing summaries
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS summary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL,
        level TEXT NOT NULL,
        summary TEXT NOT NULL,
        FOREIGN KEY (topic) REFERENCES articles(topic) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

def store_article(topic, content):
    """Stores ONLY the Wikipedia article intro in the database."""


    # Convert underscores to spaces for readability
    existing_article = Article.query.filter_by(topic=topic).first()

    if existing_article:
        print(f"Article '{topic}' already exists in the database. Updating intro.")
        existing_article.full_text = content  # Update only the intro
    else:
        print(f"Adding new intro for '{topic}' to database.")
        new_article = Article(
            topic=topic,
            full_text=content  # Save only the intro
        )
        db.session.add(new_article)

    try:
        db.session.commit()  # Save only the intro
        print(f"Intro for '{topic}' successfully stored in the database.")
    except Exception as e:
        db.session.rollback()
        print(f"Database commit failed for '{topic}': {e}")





def store_links(topic, links):
    """
    Stores all Wikipedia internal links for a topic.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Store links in JSON format
    json_links = json.dumps(links)

    try:
        cursor.execute("""
        UPDATE articles SET internal_links = ?
        WHERE topic = ?
        """, (json_links, topic))  # Updates only the internal_links field

        conn.commit()
        print(f"Stored internal links for '{topic}' in database.")
    except sqlite3.IntegrityError:
        print(f"Article '{topic}' not found, skipping link storage.")
    finally:
        conn.close()



def store_summaries(topic, summaries_dict):
    """
    Stores multiple summary levels in the database for a given topic.
    """


    # Fetch the article_id using the topic
    db.session.flush()  # Ensure uncommitted objects are visible
    article = Article.query.filter_by(topic=topic).first()

    if not article:
        print(f"No article found for topic '{topic}'. Retrying after flush...")
        db.session.commit()  # Commit all pending transactions
        article = Article.query.filter_by(topic=topic).first()  # Try again

        if not article:
            print(f"Article still not found after commit! Debug needed.")
            return

        # Debugging Step: Check if the article exists in DB
        existing_articles = Article.query.all()
        print(f"DEBUG: Existing articles in DB: {[a.topic for a in existing_articles]}")

        return  # Avoid storing a summary without an associated article

    article_id = article.id  # Get the actual ID
    print(f"Found article ID: {article_id} for topic '{topic}'.")

    for level, summary_text in summaries_dict.items():
        if not summary_text:  # Skip storing empty summaries
            print(f"Skipping empty summary for '{topic}' at level '{level}'.")
            continue

        summary_entry = Summary(
            topic=topic,
            article_id=article_id,  # Now setting article_id correctly
            level=level,
            content=summary_text,
            generated_at=datetime.utcnow()
        )
        db.session.add(summary_entry)
        print(f"Queued summary for '{topic}' (level: {level}) for DB commit.")

    try:
        db.session.commit()
        print(f"Successfully stored summaries for '{topic}'.")
    except Exception as e:
        db.session.rollback()
        print(f"Failed to store summaries: {e}")


def get_summary(topic, level):
    """
    Retrieves a stored summary for a given topic and level.
    """

    summary_entry = Summary.query.filter_by(topic=topic, level=level).first()

    if summary_entry:
        print(f"Found stored summary for '{topic}' at level '{level}'. Returning it.")
        return summary_entry.content  # Corrected field name

    print(f"No stored summary found for '{topic}' at level '{level}'.")
    return None


def get_article(topic):
    """Fetch article text from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT full_text FROM articles WHERE topic = ?", (topic,))
    result = cursor.fetchone()

    conn.close()

    print(f"Fetched from DB: {result}")  # Debugging line

    return result[0] if result else None



def get_links(topic):
    """
    Retrieves internal links stored as a JSON string in the `articles` table.
    Returns JSON-formatted string or None if no links exist.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT internal_links FROM articles WHERE topic = ?", (topic,))
        row = cursor.fetchone()
        if row and row[0]:  # Ensure data exists
            return row[0]  # Return JSON string as-is (not converting to list)

        return None  # Return None if no links exist

    except Exception as e:
        print(f"Error retrieving links for '{topic}': {e}")
        return None  # Return None on failure

    finally:
        conn.close()


if __name__ == "__main__":
    create_tables()
    print("Database initialized at instance/app.db")
