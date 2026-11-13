"""Database helpers: open one SQLite connection per request, close it after."""
import sqlite3
from pathlib import Path

from flask import current_app, g

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_db():
    """Return this request's connection, creating it on first use."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row          # rows behave like dicts
        g.db.execute("PRAGMA foreign_keys = ON")  # SQLite needs this for CASCADE
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create (or reset) the tables from schema.sql."""
    db = get_db()
    db.executescript(SCHEMA_PATH.read_text())
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)

    @app.cli.command("init-db")
    def init_db_command():
        """flask --app app init-db  -> wipe and recreate the database."""
        init_db()
        print("Initialized the database.")
