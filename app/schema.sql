-- Study Buddy database schema (SQLite)
-- Two tables: a deck has many cards.

DROP TABLE IF EXISTS cards;
DROP TABLE IF EXISTS decks;

CREATE TABLE decks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    description TEXT    NOT NULL DEFAULT '',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE cards (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_id    INTEGER NOT NULL REFERENCES decks(id) ON DELETE CASCADE,
    front      TEXT    NOT NULL,
    back       TEXT    NOT NULL,
    card_type  TEXT    CHECK (card_type IN ('term_definition', 'question_answer', 'a_b')),
    status     TEXT    NOT NULL DEFAULT 'new'
                       CHECK (status IN ('new', 'got_it', 'missed')),
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_cards_deck_id ON cards(deck_id);
