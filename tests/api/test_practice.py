"""YOUR TURN: write one API test yourself (interview live-exercise practice).

Goal: prove that renaming a card's front through the API really changes it
in the database.

Steps (Arrange, Act, Assert):
  1. Arrange: use the `client`, `db` and `card` fixtures (see conftest.py)
  2. Act:     send PUT /api/cards/<id> with {"front": "New question"}
  3. Assert:  status code is 200
  4. Assert:  SELECT front FROM cards WHERE id = ?  returns "New question"

Delete the skip line when you start. Run with:  pytest tests/api/test_practice.py -v
"""
import pytest


@pytest.mark.skip(reason="Practice test - Vig writes this one")
def test_rename_card_front(client, db, card):
    ...
