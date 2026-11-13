"""HTML pages. Each page is a plain template; its JavaScript talks to /api."""
from flask import Blueprint, abort, render_template

from .db import get_db

pages = Blueprint("pages", __name__)


def deck_or_404(deck_id):
    deck = get_db().execute("SELECT * FROM decks WHERE id = ?", (deck_id,)).fetchone()
    if deck is None:
        abort(404)
    return deck


@pages.get("/")
def home():
    return render_template("index.html")


@pages.get("/decks/<int:deck_id>")
def deck_page(deck_id):
    return render_template("deck.html", deck=deck_or_404(deck_id))


@pages.get("/decks/<int:deck_id>/study")
def study_page(deck_id):
    return render_template("study.html", deck=deck_or_404(deck_id))
