# Study Buddy — context for Claude

## What this is
Flashcard web app (Flask + SQLite + plain HTML/JS). It's Vig's **portfolio project for QA + DevOps roles**:
the tests and CI pipeline are the showcase, the app stays simple. Vig also uses it to prep for his own interviews.

## How to work with Vig
- Claude does most of the building; Vig's goal is to **explain the project in an interview**.
- After any meaningful change, give a short plain-English walkthrough: what it does, how it connects,
  and why it was done this way vs alternatives. Use tables or diagrams; he's a visual learner.
- Keep it simple and step by step. Don't grow scope past v1 until v1 is done and green.

## V1 scope (done, don't add to it)
Decks CRUD, cards CRUD (front/back, optional card_type), study mode (flip/next/shuffle),
mark got_it/missed. Single user, no logins. Decks are organized by topic; a card belongs to one deck.

**Later only:** tags (many-to-many), logins, spaced repetition, CSV import, images, sharing, stats, Render deploy.

## Layout
- `app/` – `create_app()` factory, `routes.py` (REST API under /api), `pages.py` + `templates/` (UI), `schema.sql`
- `postman/` – collection (27 requests, 78 assertions), run by Newman in CI
- `tests/api/` – 51 pytest tests incl. direct SQL checks; `tests/ui/` – 14 Playwright tests
- `.github/workflows/ci.yml` – pytest, Newman, Playwright on chromium/firefox/webkit, "All tests passed" gate

## Commands
```bash
pip install -r requirements-dev.txt && python -m playwright install chromium firefox webkit
flask --app app run
pytest tests/api
pytest tests/ui --browser chromium   # or firefox / webkit, add --headed to watch
npx newman run postman/study-buddy.postman_collection.json
```

## Status / what's left
- [x] Push to GitHub, replace YOUR-USERNAME in the README badge, get CI green
- [x] Branch protection on `main` requiring the "All tests passed" check
- [ ] Vig writes `tests/api/test_practice.py` and `tests/ui/test_practice_ui.py` himself.
      **Coach him, don't write these for him.**
- [ ] Optional: deploy to Render

## Conventions
- Parameterized SQL (`?`) only. JSON errors for /api: 400 bad input, 404 missing, 405 wrong method.
- UI tests use `data-testid` selectors and seed data through the API.
- Every test starts from a fresh database.
