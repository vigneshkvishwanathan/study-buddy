"""Database-level rules, tested with plain SQL (no API involved).

The API validates input, but the database is the last line of defense.
These tests prove the schema itself refuses bad data.
"""
import sqlite3

import pytest


def insert_deck(db, name="Deck"):
    cur = db.execute("INSERT INTO decks (name) VALUES (?)", (name,))
    db.commit()
    return cur.lastrowid


def test_card_cannot_point_to_a_deck_that_does_not_exist(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO cards (deck_id, front, back) VALUES (999, 'q', 'a')")


def test_status_must_be_an_allowed_value(db):
    deck_id = insert_deck(db)
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO cards (deck_id, front, back, status) VALUES (?, 'q', 'a', 'maybe')",
            (deck_id,),
        )


def test_card_type_must_be_an_allowed_value(db):
    deck_id = insert_deck(db)
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO cards (deck_id, front, back, card_type) VALUES (?, 'q', 'a', 'essay')",
            (deck_id,),
        )


def test_front_and_back_are_required(db):
    deck_id = insert_deck(db)
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO cards (deck_id, front) VALUES (?, 'q')", (deck_id,))


def test_new_cards_default_to_status_new(db):
    deck_id = insert_deck(db)
    db.execute("INSERT INTO cards (deck_id, front, back) VALUES (?, 'q', 'a')", (deck_id,))
    assert db.execute("SELECT status FROM cards").fetchone()["status"] == "new"


def test_deleting_a_deck_in_sql_cascades_to_cards(db):
    deck_id = insert_deck(db)
    db.executemany(
        "INSERT INTO cards (deck_id, front, back) VALUES (?, ?, ?)",
        [(deck_id, f"q{i}", f"a{i}") for i in range(50)],
    )
    db.commit()

    db.execute("DELETE FROM decks WHERE id = ?", (deck_id,))
    db.commit()

    assert db.execute("SELECT COUNT(*) FROM cards").fetchone()[0] == 0


def test_sql_injection_attempt_is_stored_as_plain_text(client, db):
    """Parameterized queries (?) mean this is just a weird deck name."""
    evil = "x'); DROP TABLE decks; --"
    res = client.post("/api/decks", json={"name": evil})

    assert res.status_code == 201
    assert db.execute("SELECT name FROM decks").fetchone()["name"] == evil
    assert db.execute("SELECT COUNT(*) FROM sqlite_master WHERE name = 'decks'").fetchone()[0] == 1
