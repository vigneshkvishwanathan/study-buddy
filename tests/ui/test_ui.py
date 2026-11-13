"""Playwright UI tests: what a real user does in a real browser."""
from playwright.sync_api import expect

CARDS = [
    ("Tell me about yourself", "QA engineer moving into DevOps"),
    ("Why this project?", "To prove testing and CI skills"),
    ("What is a 404?", "Resource not found"),
]


# ---------- decks ----------

def test_create_deck(page):
    page.goto("/")
    expect(page.get_by_test_id("no-decks")).to_be_visible()

    page.get_by_test_id("new-deck-name").fill("About me")
    page.get_by_test_id("create-deck").click()

    expect(page.get_by_test_id("deck-name")).to_have_text(["About me"])
    expect(page.get_by_test_id("deck-count")).to_have_text(["0 cards"])
    expect(page.get_by_test_id("no-decks")).to_be_hidden()


def test_blank_deck_name_shows_error(page):
    page.goto("/")
    page.get_by_test_id("create-deck").click()

    expect(page.get_by_test_id("deck-error")).to_have_text("'name' is required")
    expect(page.get_by_test_id("deck-item")).to_have_count(0)


def test_edit_deck_name(page, seed):
    seed("QA")
    page.goto("/")

    page.get_by_test_id("edit-deck").click()
    page.get_by_test_id("edit-deck-name").fill("QA & testing")
    page.get_by_test_id("save-deck").click()

    expect(page.get_by_test_id("deck-name")).to_have_text(["QA & testing"])


def test_delete_deck_after_confirming(page, seed):
    seed("Delete me")
    page.goto("/")

    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_test_id("delete-deck").click()

    expect(page.get_by_test_id("deck-item")).to_have_count(0)


# ---------- cards ----------

def test_create_card(page, seed):
    deck = seed("About me")
    page.goto(f"/decks/{deck['id']}")

    page.get_by_test_id("card-front").fill("Tell me about yourself")
    page.get_by_test_id("card-back").fill("QA engineer moving into DevOps")
    page.get_by_test_id("card-type").select_option("question_answer")
    page.get_by_test_id("add-card").click()

    expect(page.get_by_test_id("card-front-text")).to_have_text(["Tell me about yourself"])
    expect(page.get_by_test_id("card-status")).to_have_text(["new"])
    expect(page.get_by_test_id("card-front")).to_be_empty()   # form was reset


def test_card_needs_front_and_back(page, seed):
    deck = seed()
    page.goto(f"/decks/{deck['id']}")

    page.get_by_test_id("card-front").fill("Only a front")
    page.get_by_test_id("add-card").click()

    expect(page.get_by_test_id("card-error")).to_be_visible()
    expect(page.get_by_test_id("card-item")).to_have_count(0)


def test_edit_and_delete_card(page, seed):
    deck = seed(cards=CARDS[:1])
    page.goto(f"/decks/{deck['id']}")

    page.get_by_test_id("edit-card").click()
    page.get_by_test_id("edit-card-back").fill("A better answer")
    page.get_by_test_id("save-card").click()
    expect(page.get_by_test_id("card-back-text")).to_have_text(["A better answer"])

    page.get_by_test_id("delete-card").click()
    expect(page.get_by_test_id("no-cards")).to_be_visible()


# ---------- study mode ----------

def test_flip_card(page, seed):
    deck = seed(cards=CARDS[:1])
    page.goto(f"/decks/{deck['id']}/study")
    card = page.get_by_test_id("flashcard")

    expect(page.get_by_test_id("card-text")).to_have_text("Tell me about yourself")
    expect(card).to_have_attribute("data-side", "front")

    card.click()
    expect(page.get_by_test_id("card-text")).to_have_text("QA engineer moving into DevOps")
    expect(card).to_have_attribute("data-side", "back")

    page.get_by_test_id("flip").click()   # the button flips back too
    expect(card).to_have_attribute("data-side", "front")


def test_next_goes_through_cards_and_wraps(page, seed):
    deck = seed(cards=CARDS)
    page.goto(f"/decks/{deck['id']}/study")
    text, progress = page.get_by_test_id("card-text"), page.get_by_test_id("progress")

    expect(progress).to_have_text("Card 1 of 3")
    page.get_by_test_id("flashcard").click()          # flip to back...
    page.get_by_test_id("next").click()                 # ...next card starts on its front
    expect(text).to_have_text("Why this project?")
    expect(progress).to_have_text("Card 2 of 3")

    page.get_by_test_id("next").click()
    page.get_by_test_id("next").click()
    expect(text).to_have_text("Tell me about yourself")  # wrapped around
    expect(progress).to_have_text("Card 1 of 3")


def test_shuffle_keeps_every_card(page, seed):
    deck = seed(cards=CARDS)
    page.goto(f"/decks/{deck['id']}/study")
    expect(page.get_by_test_id("progress")).to_have_text("Card 1 of 3")

    page.get_by_test_id("shuffle").click()

    seen = set()
    for _ in CARDS:
        seen.add(page.get_by_test_id("card-text").inner_text())
        page.get_by_test_id("next").click()
    assert seen == {front for front, _ in CARDS}


def test_got_it_and_missed_are_saved(page, seed):
    deck = seed(cards=CARDS[:2])
    page.goto(f"/decks/{deck['id']}/study")

    page.get_by_test_id("got-it").click()
    expect(page.get_by_test_id("got-count")).to_have_text("1")
    page.get_by_test_id("missed").click()
    expect(page.get_by_test_id("missed-count")).to_have_text("1")

    # The UI said so - now check the API agrees.
    cards = page.request.get(f"/api/decks/{deck['id']}/cards").json()
    assert [c["status"] for c in cards] == ["got_it", "missed"]


def test_empty_deck_study_message(page, seed):
    deck = seed()
    page.goto(f"/decks/{deck['id']}/study")
    expect(page.get_by_test_id("study-empty")).to_be_visible()


def test_unknown_deck_page_is_404(page):
    response = page.goto("/decks/999")
    assert response.status == 404
