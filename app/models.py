import json
from datetime import datetime
from app import db  # Import the SQLAlchemy instance from your app/__init__.py

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(255), nullable=False, unique=True)
    full_text = db.Column(db.Text, nullable=False)
    internal_links = db.Column(db.Text, nullable=True)
    retrieved_at = db.Column(db.DateTime, default=datetime.utcnow)


    # Relationship to access summaries for this article
    summaries = db.relationship('Summary', backref='article', lazy=True)

    def __repr__(self):
        return f"<Article {self.topic}>"

    def set_internal_links(self, links):
        """Store internal links as a JSON string."""
        self.internal_links = json.dumps(links)

    def get_internal_links(self):
        """Retrieve internal links as a list."""
        if self.internal_links:
            return json.loads(self.internal_links)
        return []

class Summary(db.Model):
    __tablename__ = 'summary'
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(255), nullable=False)  # ✅ Ensure this exists
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    level = db.Column(db.String(20), nullable=False)  # ✅ Add this column
    content = db.Column(db.Text, nullable=False)  # ✅ Store summarized text
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Summary Topic:{self.topic}, Level:{self.level}>"



class LearningPath(db.Model):
    __tablename__ = "learning_paths"

    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String, unique=True, nullable=False)
    basic_links = db.Column(db.Text, nullable=True)  # JSON list of top 10 links
    intermediate_links = db.Column(db.Text, nullable=True)  # JSON list of top 20 links
    advanced_links = db.Column(db.Text, nullable=True)  # JSON list of top 30 links
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<LearningPath {self.topic}>"

    def to_dict(self):
        """Return a dictionary representation of the learning path."""
        return {
            "topic": self.topic,
            "basic_links": json.loads(self.basic_links) if self.basic_links else [],
            "intermediate_links": json.loads(self.intermediate_links) if self.intermediate_links else [],
            "advanced_links": json.loads(self.advanced_links) if self.advanced_links else [],
            "last_updated": self.last_updated.isoformat()
        }
class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(255), db.ForeignKey('articles.topic'), nullable=False)
    linked_topic = db.Column(db.String(255), nullable=False)  # ✅ The internal link
