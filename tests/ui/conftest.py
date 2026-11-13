"""Fixtures for Playwright UI tests.

- One real Flask server runs for the whole test session (in a background thread).
- The database is wiped before every test, so tests never depend on each other.
- Pick the browser with:  pytest tests/ui --browser firefox   (chromium | firefox | webkit)
"""
import threading

import pytest
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

from app import create_app
from app.db import init_db


@pytest.fixture(scope="session")
def flask_app(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("ui") / "ui.sqlite"
    return create_app({"TESTING": True, "DATABASE": str(db_path)})


@pytest.fixture(scope="session")
def base_url(flask_app):
    server = make_server("127.0.0.1", 0, flask_app)   # port 0 = pick any free port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture(autouse=True)
def clean_db(flask_app):
    with flask_app.app_context():
        init_db()


@pytest.fixture(scope="session")
def browser(request):
    with sync_playwright() as p:
        browser_type = getattr(p, request.config.getoption("--browser"))
        browser = browser_type.launch(headless=not request.config.getoption("--headed"))
        yield browser
        browser.close()


@pytest.fixture
def page(browser, base_url):
    context = browser.new_context(base_url=base_url)
    page = context.new_page()
    page.set_default_timeout(5000)
    yield page
    context.close()


@pytest.fixture
def seed(page):
    """Create test data through the API (faster than clicking through the UI)."""
    def make_deck(name="Interview prep", cards=()):
        deck = page.request.post("/api/decks", data={"name": name}).json()
        for front, back in cards:
            page.request.post(f"/api/decks/{deck['id']}/cards", data={"front": front, "back": back})
        return deck
    return make_deck
