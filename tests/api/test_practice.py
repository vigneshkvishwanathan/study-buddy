"""Practice test: renaming a card's front through the API really changes it in the database.

Arrange, Act, Assert:
  Arrange - the `card` fixture already created a card (see conftest.py)
  Act     - PUT /api/cards/<id> with a new front
  Assert  - the API says 200 AND the database row really changed
"""


def test_rename_card_front(client, db, card):
    res = client.put(f"/api/cards/{card['id']}", json={"front": "New question"})

    assert res.status_code == 200
    assert res.get_json()["front"] == "New question"
    row = db.execute("SELECT front, back FROM cards WHERE id = ?", (card["id"],)).fetchone()
    assert row["front"] == "New question"
    assert row["back"] == card["back"]      # fields we didn't send stay the same
