"""YOUR TURN: write one Playwright test yourself (interview live-exercise practice).

Goal: on the study page, clicking "Got it" increases the Got it counter.

Steps:
  1. Arrange: deck = seed(cards=[("Q1", "A1")])
  2. Act:     page.goto(f"/decks/{deck['id']}/study")
              page.get_by_test_id("got-it").click()
  3. Assert:  expect(page.get_by_test_id("got-count")).to_have_text("1")

Delete the skip line when you start. Run with:  pytest tests/ui/test_practice_ui.py -v --headed
"""
import pytest
from playwright.sync_api import expect  # noqa: F401  (you'll need this)


@pytest.mark.skip(reason="Practice test - Vig writes this one")
def test_got_it_counter_goes_up(page, seed):
    ...
