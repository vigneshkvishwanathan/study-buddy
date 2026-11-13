"""Practice test: on the study page, clicking "Got it" increases the Got it counter."""
from playwright.sync_api import expect


def test_got_it_counter_goes_up(page, seed):
    deck = seed(cards=[("Q1", "A1")])
    page.goto(f"/decks/{deck['id']}/study")
    expect(page.get_by_test_id("got-count")).to_have_text("0")

    page.get_by_test_id("got-it").click()

    expect(page.get_by_test_id("got-count")).to_have_text("1")
