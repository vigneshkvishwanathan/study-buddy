"""Study Buddy - Flask app factory."""
from pathlib import Path

from flask import Flask, jsonify, request

from . import db
from .pages import pages
from .routes import api


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=str(Path(app.instance_path) / "study_buddy.sqlite"),
    )
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    app.register_blueprint(api)
    app.register_blueprint(pages)

    # Create tables automatically the first time the app runs.
    if not Path(app.config["DATABASE"]).exists():
        with app.app_context():
            db.init_db()

    # API errors come back as JSON, never an HTML error page.
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith("/api/"):
            return jsonify(error="Not found"), 404
        return e

    @app.errorhandler(405)
    def method_not_allowed(e):
        if request.path.startswith("/api/"):
            return jsonify(error="Method not allowed"), 405
        return e

    return app
