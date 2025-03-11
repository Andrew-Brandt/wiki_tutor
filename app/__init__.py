# app/__init__.py
from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

# Initialize Cache and SQLAlchemy (global instances)
cache = Cache()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Set caching configuration on the app instance
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_HOST'] = 'localhost'
    app.config['CACHE_REDIS_PORT'] = 6380  # Updated port for Redis
    app.config['CACHE_REDIS_DB'] = 0
    app.config['CACHE_REDIS_URL'] = 'redis://localhost:6380/0'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 0

    cache.init_app(app)

    # Configure SQLAlchemy for SQLite

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # Import and register the blueprint from routes.py
    from .routes import main
    app.register_blueprint(main)

    return app
