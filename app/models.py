# app/models.py
from datetime import datetime
from app import db  # Import the SQLAlchemy instance from your app/__init__.py

class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(255), nullable=False, unique=True)
    full_text = db.Column(db.Text, nullable=False)
    retrieved_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to access summaries for this article
    summaries = db.relationship('Summary', backref='article', lazy=True)

    def __repr__(self):
        return f"<Article {self.topic}>"

class Summary(db.Model):
    __tablename__ = 'summary'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)  # e.g., 'easy', 'medium', 'hard'
    summary_text = db.Column(db.Text, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Summary ArticleID:{self.article_id} ({self.difficulty})>"
