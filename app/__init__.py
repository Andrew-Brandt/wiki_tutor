# app/__init__.py
from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
cache = Cache()  # Global cache instance


def create_app():
    app = Flask(__name__)

    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/app.db'  # Database location
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Performance optimization

    # Configure Flask-Caching with Redis
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_HOST'] = 'localhost'
    app.config['CACHE_REDIS_PORT'] = 6379
    app.config['CACHE_REDIS_DB'] = 0
    app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 86400

    cache.init_app(app)  # Ensure cache is initialized
    db.init_app(app)  # Ensure database is initialized

    register_blueprints(app)  # Import routes AFTER Flask is initialized

    return app

def register_blueprints(app):
    from app.routes import main  # Delayed import to avoid circular issue
    app.register_blueprint(main)
