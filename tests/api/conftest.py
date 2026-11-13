"""Shared fixtures for API tests.

Every test gets a brand-new SQLite file in a temp folder, so tests never
share data and never touch the real database.
"""
import sqlite3

import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.sqlite")})


@pytest.fixture
def client(app):
    """Sends HTTP requests to the app without starting a real server."""
    return app.test_client()


@pytest.fixture
def db(app):
    """A direct SQL connection to the same database the API writes to.

    Lets tests check what was REALLY stored, not just what the API said.
    """
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()


@pytest.fixture
def deck(client):
    """A deck that already exists, for tests that need one."""
    return client.post("/api/decks", json={"name": "About me"}).get_json()


@pytest.fixture
def card(client, deck):
    """A card that already exists inside `deck`."""
    return client.post(
        f"/api/decks/{deck['id']}/cards",
        json={"front": "Tell me about yourself", "back": "I'm a QA engineer..."},
    ).get_json()
