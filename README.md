# Study Buddy

![CI](https://github.com/vigneshkvishwanathan/study-buddy/actions/workflows/ci.yml/badge.svg)

A small flashcard web app (a free alternative to Quizlet) that I use to prep for my own interviews.
I built it as a **QA + DevOps portfolio project**: the app is deliberately simple, and the
**tests and CI pipeline are the point**.

| Layer | Tool | What it proves |
|---|---|---|
| App | Flask + SQLite + plain HTML/JS | REST API design, SQL schema design |
| API tests | **Postman** collection run by **Newman** | 27 requests, 78 assertions, chained with variables |
| API + DB tests | **pytest** + direct **SQL** queries | 52 tests checking responses *and* what's really stored |
| UI tests | **Playwright** (Python) | 14 user flows on **Chromium, Firefox and WebKit** |
| CI/CD | **GitHub Actions** | Every push runs everything; merges blocked on failure |

## How it fits together

```
push / pull request ─► GitHub Actions
   ├─ pytest (API + SQL) ─► Playwright: chromium | firefox | webkit  (in parallel)
   ├─ Postman (Newman, against a running server)
   └─ All tests passed  ─► green only if every job is green ─► merge allowed
```

```
Browser page ──fetch──► Flask /api routes ──SQL──► SQLite
 (HTML + JS)            (validate → 400/404)        decks 1──* cards
```

## Features (v1)
- Create, edit, delete **decks** (organized by topic, e.g. "About me", "DevOps")
- Create, edit, delete **cards** (front/back, optional type: question/answer, term/definition, A/B)
- **Study mode**: flip, next, shuffle, mark "got it" / "missed" (saved to the database)
- Single user, no logins (on purpose — see Roadmap)

## Run it locally
```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m playwright install chromium firefox webkit

flask --app app run            # open http://127.0.0.1:5000
```

## Run the tests
```bash
pytest tests/api                       # API + SQL tests (fast, no browser)
pytest tests/ui                        # Playwright, Chromium by default
pytest tests/ui --browser firefox      # or webkit
pytest tests/ui --headed               # watch the browser click through

# Postman: start the app, then
npx newman run postman/study-buddy.postman_collection.json
```
You can also import `postman/study-buddy.postman_collection.json` into the Postman app and click **Run**.

## Project layout
```
app/
  __init__.py        create_app() factory, JSON error handlers
  db.py              one SQLite connection per request
  schema.sql         tables, foreign key, CHECK rules
  routes.py          REST API (/api/...)
  pages.py           HTML pages
  templates/, static/
postman/             Postman collection (Newman runs it in CI)
tests/api/           pytest: endpoints + direct SQL checks + DB rules
tests/ui/            Playwright: create, edit, flip, next, shuffle, mark
.github/workflows/   CI pipeline
```

## API
All responses are JSON. Errors look like `{"error": "message"}`.

| Method | Path | What it does | Success |
|---|---|---|---|
| GET | `/api/health` | Is the server up? | 200 |
| GET | `/api/decks` | List decks (with `card_count`) | 200 |
| POST | `/api/decks` | Create a deck `{name, description?}` | 201 |
| GET | `/api/decks/<id>` | Get one deck | 200 |
| PUT | `/api/decks/<id>` | Edit a deck | 200 |
| DELETE | `/api/decks/<id>` | Delete a deck **and its cards** | 204 |
| GET | `/api/decks/<id>/cards` | List a deck's cards | 200 |
| POST | `/api/decks/<id>/cards` | Add a card `{front, back, card_type?}` | 201 |
| GET | `/api/cards/<id>` | Get one card | 200 |
| PUT | `/api/cards/<id>` | Edit a card | 200 |
| PATCH | `/api/cards/<id>/status` | Mark `{status: got_it \| missed \| new}` | 200 |
| DELETE | `/api/cards/<id>` | Delete a card | 204 |

Errors: **400** bad input · **404** not found · **405** wrong method.

## Testing approach
- **Test the API and the database.** pytest tests don't just trust the response; they query SQLite
  to confirm what was actually written (or that *nothing* was written on a 400).
- **Defense in depth.** Python validates input for friendly errors; the schema (`NOT NULL`, `CHECK`,
  foreign keys with `ON DELETE CASCADE`) blocks bad data even if validation is bypassed. Both are tested.
- **Isolated tests.** Every API test gets a fresh temp database; every UI test starts from an empty one.
- **Stable selectors.** UI tests find elements by `data-testid`, so styling changes don't break them.
- **Seed through the API, test through the UI.** UI tests create data with API calls, then click only
  the thing under test — faster and less flaky.
- **Security check.** A test proves a SQL-injection string is stored as harmless text
  (parameterized queries).

## CI: blocking merges
The workflow ends with one job, **All tests passed**, that is green only if every other job is green.
To block merges on failure (one-time setup on GitHub):

**Settings → Branches → Add branch protection rule** → branch `main` →
✅ *Require status checks to pass before merging* → add **All tests passed**.

## Roadmap (after v1)
Tags (one card in many decks), logins, spaced repetition, CSV/Quizlet import, images, sharing, stats,
deploy to Render.
