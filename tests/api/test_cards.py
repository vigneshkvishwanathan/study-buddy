"""Card endpoints, including study-mode status marking."""
import pytest


# ---------- create ----------

def test_create_card_returns_201_and_saves_row(client, db, deck):
    res = client.post(
        f"/api/decks/{deck['id']}/cards",
        json={"front": "Why Flask?", "back": "Small and simple", "card_type": "question_answer"},
    )

    assert res.status_code == 201
    card = res.get_json()
    row = db.execute("SELECT * FROM cards WHERE id = ?", (card["id"],)).fetchone()
    assert row["deck_id"] == deck["id"]
    assert row["front"] == "Why Flask?"
    assert row["card_type"] == "question_answer"
    assert row["status"] == "new"          # default from the schema


def test_card_type_is_optional(client, deck):
    card = client.post(f"/api/decks/{deck['id']}/cards", json={"front": "a", "back": "b"}).get_json()
    assert card["card_type"] is None


@pytest.mark.parametrize("payload", [
    {"back": "no front"},
    {"front": "no back"},
    {"front": "  ", "back": "b"},
    {"front": "a", "back": "b", "card_type": "essay"},
])
def test_create_card_rejects_bad_input_and_writes_nothing(client, db, deck, payload):
    res = client.post(f"/api/decks/{deck['id']}/cards", json=payload)

    assert res.status_code == 400
    assert db.execute("SELECT COUNT(*) FROM cards").fetchone()[0] == 0


def test_create_card_in_missing_deck_returns_404(client, db):
    res = client.post("/api/decks/999/cards", json={"front": "a", "back": "b"})
    assert res.status_code == 404
    assert db.execute("SELECT COUNT(*) FROM cards").fetchone()[0] == 0


# ---------- read ----------

def test_list_cards_only_returns_that_decks_cards(client, deck, card):
    other = client.post("/api/decks", json={"name": "Other"}).get_json()
    client.post(f"/api/decks/{other['id']}/cards", json={"front": "x", "back": "y"})

    cards = client.get(f"/api/decks/{deck['id']}/cards").get_json()

    assert [c["id"] for c in cards] == [card["id"]]


def test_list_cards_for_missing_deck_returns_404(client):
    assert client.get("/api/decks/999/cards").status_code == 404


def test_get_card(client, card):
    res = client.get(f"/api/cards/{card['id']}")
    assert res.status_code == 200
    assert res.get_json()["front"] == "Tell me about yourself"


def test_get_missing_card_returns_404(client):
    assert client.get("/api/cards/999").status_code == 404


# ---------- update ----------

def test_update_card_back_only(client, db, card):
    res = client.put(f"/api/cards/{card['id']}", json={"back": "Better answer"})

    assert res.status_code == 200
    row = db.execute("SELECT front, back FROM cards WHERE id = ?", (card["id"],)).fetchone()
    assert (row["front"], row["back"]) == ("Tell me about yourself", "Better answer")


def test_update_card_rejects_blank_front(client, db, card):
    assert client.put(f"/api/cards/{card['id']}", json={"front": ""}).status_code == 400
    row = db.execute("SELECT front FROM cards WHERE id = ?", (card["id"],)).fetchone()
    assert row["front"] == "Tell me about yourself"


def test_update_missing_card_returns_404(client):
    assert client.put("/api/cards/999", json={"front": "x"}).status_code == 404


# ---------- study mode: mark got it / missed ----------

@pytest.mark.parametrize("status", ["got_it", "missed", "new"])
def test_mark_card_status(client, db, card, status):
    res = client.patch(f"/api/cards/{card['id']}/status", json={"status": status})

    assert res.status_code == 200
    row = db.execute("SELECT status FROM cards WHERE id = ?", (card["id"],)).fetchone()
    assert row["status"] == status


@pytest.mark.parametrize("payload", [{"status": "maybe"}, {"status": None}, {}])
def test_mark_card_rejects_invalid_status(client, db, card, payload):
    assert client.patch(f"/api/cards/{card['id']}/status", json=payload).status_code == 400
    row = db.execute("SELECT status FROM cards WHERE id = ?", (card["id"],)).fetchone()
    assert row["status"] == "new"


def test_mark_missing_card_returns_404(client):
    assert client.patch("/api/cards/999/status", json={"status": "got_it"}).status_code == 404


# ---------- delete ----------

def test_delete_card(client, db, card):
    res = client.delete(f"/api/cards/{card['id']}")
    assert res.status_code == 204
    assert db.execute("SELECT COUNT(*) FROM cards").fetchone()[0] == 0


def test_delete_missing_card_returns_404(client):
    assert client.delete("/api/cards/999").status_code == 404


# ---------- general ----------

def test_wrong_method_returns_json_405(client):
    res = client.patch("/api/decks")
    assert res.status_code == 405
    assert "error" in res.get_json()


def test_health(client):
    assert client.get("/api/health").get_json() == {"status": "ok"}
