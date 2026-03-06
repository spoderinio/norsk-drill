# Norsk Drill 🇳🇴

A self-hosted vocabulary practice app for learning Norwegian, built with FastAPI and SQLite. Runs on a Raspberry Pi and is accessible from any device on the local network.

## What it does

Norsk Drill lets you add Norwegian vocabulary and practice it through flashcard-style exercises. You type the translation from memory, and the app tells you if you're right. Words are organized by category and level so you can focus on what you're currently studying.

**Categories:**
- **Substantiv** (Nouns) — practice article + word → Bulgarian translation
- **Verb** — conjugate presens, preteritum, perfektum
- **Adjektiv** — inflect neuter, plural forms + translation
- **Fraser** (Phrases) — full phrase → translation
- **Spørreord** (Question words) — hvem, hva, hvor, når, hvorfor... with example sentences

**Levels:** Words are tagged A / B1.1 / B1.2 / B2.1 / B2.2. On the home page you select which level to practice — existing words default to A.

**Other features:**
- Text-to-speech pronunciation (Norwegian, browser-native)
- Bulk import via CSV or plain text (`en hus – hus` format)
- Search across all categories
- Skip button — shows the full correct answer so you see it multiple times
- Answer checking is case-insensitive and ignores trailing punctuation

## Tech stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, SQLAlchemy (async) |
| Database | SQLite via aiosqlite |
| Templates | Jinja2 |
| Frontend | Vanilla HTML/CSS/JS (no framework) |
| Server | Uvicorn, systemd service |
| Hardware | Raspberry Pi 4 |

## Project structure

```
norsk-drill/
├── app/
│   ├── db.py          # SQLAlchemy models (Noun, Verb, Adjective, Phrase, QuestionWord)
│   ├── crud.py        # Database queries and answer checking
│   ├── settings.py    # Config (DATABASE_URL etc.)
│   ├── routers/
│   │   ├── practice.py  # Practice endpoints for all categories
│   │   └── admin.py     # Admin CRUD endpoints
│   └── templates/
│       ├── home.html
│       ├── search.html
│       ├── practice/    # One template per category
│       └── admin/       # Admin pages + edit forms
├── main.py            # FastAPI app + router registration
├── data/
│   └── norsk_drill.db # SQLite database
└── static/            # Static assets
```

## How it works

1. **Adding words** — go to Admin, pick a category, add words one by one or paste a list. Each import batch gets assigned a level (A / B1.x / B2.x).
2. **Practicing** — select a level on the home page (saved in localStorage), pick a category. The app fetches a random unseen word from that level, you type the answer, press Enter or ✓. After finishing all words in a session you see your score.
3. **Answer matching** — both the stored translation and your input are lowercased and stripped of trailing punctuation before comparison. Multiple accepted translations are separated by commas.
4. **Database migration** — new columns (`level`, `group`, `group_description`) are added automatically on startup via `ALTER TABLE` if they don't exist, so existing databases are upgraded without data loss.
