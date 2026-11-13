"""Deck endpoints: the API response AND what's actually in the database."""
import pytest


# ---------- create ----------

def test_create_deck_returns_201_and_saves_row(client, db):
    res = client.post("/api/decks", json={"name": "DevOps", "description": "CI/CD"})

    assert res.status_code == 201
    body = res.get_json()
    assert body["name"] == "DevOps"
    assert body["card_count"] == 0

    row = db.execute("SELECT name, description FROM decks WHERE id = ?", (body["id"],)).fetchone()
    assert row["name"] == "DevOps"
    assert row["description"] == "CI/CD"


def test_create_deck_trims_whitespace(client, db):
    body = client.post("/api/decks", json={"name": "  Behavioral  "}).get_json()
    row = db.execute("SELECT name FROM decks WHERE id = ?", (body["id"],)).fetchone()
    assert row["name"] == "Behavioral"


@pytest.mark.parametrize("payload", [
    {},                      # name missing
    {"name": ""},            # empty
    {"name": "   "},         # only spaces
    {"name": 123},           # wrong type
    {"name": "ok", "description": 5},
])
def test_create_deck_rejects_bad_input_and_writes_nothing(client, db, payload):
    res = client.post("/api/decks", json=payload)

    assert res.status_code == 400
    assert "error" in res.get_json()
    assert db.execute("SELECT COUNT(*) FROM decks").fetchone()[0] == 0


def test_create_deck_rejects_non_json_body(client):
    res = client.post("/api/decks", data="hello", content_type="text/plain")
    assert res.status_code == 400


# ---------- read ----------

def test_list_decks_empty(client):
    res = client.get("/api/decks")
    assert res.status_code == 200
    assert res.get_json() == []


def test_list_decks_counts_cards_like_sql_does(client, db, deck, card):
    listed = client.get("/api/decks").get_json()
    sql_count = db.execute(
        "SELECT COUNT(*) FROM cards WHERE deck_id = ?", (deck["id"],)
    ).fetchone()[0]
    assert listed[0]["card_count"] == sql_count == 1


def test_get_deck(client, deck):
    res = client.get(f"/api/decks/{deck['id']}")
    assert res.status_code == 200
    assert res.get_json()["name"] == "About me"


def test_get_missing_deck_returns_404(client):
    res = client.get("/api/decks/999")
    assert res.status_code == 404
    assert res.get_json() == {"error": "Deck not found"}


# ---------- update ----------

def test_update_deck_name_only_keeps_description(client, db):
    deck = client.post("/api/decks", json={"name": "QA", "description": "testing"}).get_json()

    res = client.put(f"/api/decks/{deck['id']}", json={"name": "QA & testing"})

    assert res.status_code == 200
    row = db.execute("SELECT name, description FROM decks WHERE id = ?", (deck["id"],)).fetchone()
    assert (row["name"], row["description"]) == ("QA & testing", "testing")


def test_update_deck_blank_name_is_rejected_and_unchanged(client, db, deck):
    res = client.put(f"/api/decks/{deck['id']}", json={"name": ""})

    assert res.status_code == 400
    row = db.execute("SELECT name FROM decks WHERE id = ?", (deck["id"],)).fetchone()
    assert row["name"] == "About me"


def test_update_missing_deck_returns_404(client):
    assert client.put("/api/decks/999", json={"name": "x"}).status_code == 404


# ---------- delete ----------

def test_delete_deck_returns_204_and_removes_row(client, db, deck):
    res = client.delete(f"/api/decks/{deck['id']}")

    assert res.status_code == 204
    assert res.data == b""
    assert db.execute("SELECT COUNT(*) FROM decks").fetchone()[0] == 0


def test_delete_deck_also_deletes_its_cards(client, db, deck, card):
    client.delete(f"/api/decks/{deck['id']}")

    remaining = db.execute("SELECT COUNT(*) FROM cards WHERE deck_id = ?", (deck["id"],)).fetchone()[0]
    assert remaining == 0


def test_delete_deck_leaves_other_decks_alone(client, db, deck, card):
    other = client.post("/api/decks", json={"name": "Keep me"}).get_json()
    client.post(f"/api/decks/{other['id']}/cards", json={"front": "q", "back": "a"})

    client.delete(f"/api/decks/{deck['id']}")

    assert db.execute("SELECT COUNT(*) FROM decks").fetchone()[0] == 1
    assert db.execute("SELECT COUNT(*) FROM cards WHERE deck_id = ?", (other["id"],)).fetchone()[0] == 1


def test_delete_missing_deck_returns_404(client):
    assert client.delete("/api/decks/999").status_code == 404
