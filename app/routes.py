"""REST API routes for decks and cards. Everything lives under /api."""
from flask import Blueprint, jsonify, request

from .db import get_db

api = Blueprint("api", __name__, url_prefix="/api")

CARD_TYPES = {"term_definition", "question_answer", "a_b"}
STATUSES = {"new", "got_it", "missed"}


# ---------- helpers ----------

def error(message, code):
    return jsonify(error=message), code


def get_json_body():
    """Return the request body as a dict, or None if it isn't a JSON object."""
    body = request.get_json(silent=True)
    return body if isinstance(body, dict) else None


def clean_text(value):
    """Return stripped text, or None if missing / not a string / blank."""
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip()


def find_deck(deck_id):
    return get_db().execute("SELECT * FROM decks WHERE id = ?", (deck_id,)).fetchone()


def find_card(card_id):
    return get_db().execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()


def deck_json(row):
    count = get_db().execute(
        "SELECT COUNT(*) FROM cards WHERE deck_id = ?", (row["id"],)
    ).fetchone()[0]
    return {**dict(row), "card_count": count}


# ---------- health ----------

@api.get("/health")
def health():
    return jsonify(status="ok")


# ---------- decks ----------

@api.get("/decks")
def list_decks():
    rows = get_db().execute("SELECT * FROM decks ORDER BY id").fetchall()
    return jsonify([deck_json(r) for r in rows])


@api.post("/decks")
def create_deck():
    body = get_json_body()
    if body is None:
        return error("Request body must be a JSON object", 400)
    name = clean_text(body.get("name"))
    if name is None:
        return error("'name' is required", 400)
    description = body.get("description", "")
    if not isinstance(description, str):
        return error("'description' must be text", 400)

    db = get_db()
    cur = db.execute(
        "INSERT INTO decks (name, description) VALUES (?, ?)",
        (name, description.strip()),
    )
    db.commit()
    return jsonify(deck_json(find_deck(cur.lastrowid))), 201


@api.get("/decks/<int:deck_id>")
def get_deck(deck_id):
    deck = find_deck(deck_id)
    if deck is None:
        return error("Deck not found", 404)
    return jsonify(deck_json(deck))


@api.put("/decks/<int:deck_id>")
def update_deck(deck_id):
    deck = find_deck(deck_id)
    if deck is None:
        return error("Deck not found", 404)
    body = get_json_body()
    if body is None:
        return error("Request body must be a JSON object", 400)

    name = deck["name"]
    description = deck["description"]
    if "name" in body:
        name = clean_text(body["name"])
        if name is None:
            return error("'name' cannot be blank", 400)
    if "description" in body:
        if not isinstance(body["description"], str):
            return error("'description' must be text", 400)
        description = body["description"].strip()

    db = get_db()
    db.execute(
        "UPDATE decks SET name = ?, description = ? WHERE id = ?",
        (name, description, deck_id),
    )
    db.commit()
    return jsonify(deck_json(find_deck(deck_id)))


@api.delete("/decks/<int:deck_id>")
def delete_deck(deck_id):
    if find_deck(deck_id) is None:
        return error("Deck not found", 404)
    db = get_db()
    db.execute("DELETE FROM decks WHERE id = ?", (deck_id,))  # cards cascade
    db.commit()
    return "", 204


# ---------- cards ----------

@api.get("/decks/<int:deck_id>/cards")
def list_cards(deck_id):
    if find_deck(deck_id) is None:
        return error("Deck not found", 404)
    rows = get_db().execute(
        "SELECT * FROM cards WHERE deck_id = ? ORDER BY id", (deck_id,)
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@api.post("/decks/<int:deck_id>/cards")
def create_card(deck_id):
    if find_deck(deck_id) is None:
        return error("Deck not found", 404)
    body = get_json_body()
    if body is None:
        return error("Request body must be a JSON object", 400)

    front = clean_text(body.get("front"))
    back = clean_text(body.get("back"))
    if front is None or back is None:
        return error("'front' and 'back' are required", 400)
    card_type = body.get("card_type")
    if card_type is not None and card_type not in CARD_TYPES:
        return error(f"'card_type' must be one of {sorted(CARD_TYPES)}", 400)

    db = get_db()
    cur = db.execute(
        "INSERT INTO cards (deck_id, front, back, card_type) VALUES (?, ?, ?, ?)",
        (deck_id, front, back, card_type),
    )
    db.commit()
    return jsonify(dict(find_card(cur.lastrowid))), 201


@api.get("/cards/<int:card_id>")
def get_card(card_id):
    card = find_card(card_id)
    if card is None:
        return error("Card not found", 404)
    return jsonify(dict(card))


@api.put("/cards/<int:card_id>")
def update_card(card_id):
    card = find_card(card_id)
    if card is None:
        return error("Card not found", 404)
    body = get_json_body()
    if body is None:
        return error("Request body must be a JSON object", 400)

    front, back, card_type = card["front"], card["back"], card["card_type"]
    if "front" in body:
        front = clean_text(body["front"])
        if front is None:
            return error("'front' cannot be blank", 400)
    if "back" in body:
        back = clean_text(body["back"])
        if back is None:
            return error("'back' cannot be blank", 400)
    if "card_type" in body:
        card_type = body["card_type"]
        if card_type is not None and card_type not in CARD_TYPES:
            return error(f"'card_type' must be one of {sorted(CARD_TYPES)}", 400)

    db = get_db()
    db.execute(
        "UPDATE cards SET front = ?, back = ?, card_type = ? WHERE id = ?",
        (front, back, card_type, card_id),
    )
    db.commit()
    return jsonify(dict(find_card(card_id)))


@api.patch("/cards/<int:card_id>/status")
def mark_card(card_id):
    """Study mode: mark a card 'got_it' or 'missed' (or reset to 'new')."""
    if find_card(card_id) is None:
        return error("Card not found", 404)
    body = get_json_body()
    status = body.get("status") if body else None
    if status not in STATUSES:
        return error(f"'status' must be one of {sorted(STATUSES)}", 400)

    db = get_db()
    db.execute("UPDATE cards SET status = ? WHERE id = ?", (status, card_id))
    db.commit()
    return jsonify(dict(find_card(card_id)))


@api.delete("/cards/<int:card_id>")
def delete_card(card_id):
    if find_card(card_id) is None:
        return error("Card not found", 404)
    db = get_db()
    db.execute("DELETE FROM cards WHERE id = ?", (card_id,))
    db.commit()
    return "", 204
