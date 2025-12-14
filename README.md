# 🇳🇴 Norsk Drill - Norwegian Vocabulary Practice

Personal language learning app for practicing Norwegian nouns, verbs, and adjectives with grammatical groups.

## Features

- ✅ **Practice Nouns** with articles (en/ei/et)
- ✅ **Practice Verbs** with all tenses (presens, preteritum, perfektum)
- ✅ **Practice Adjectives** with forms (neuter, plural)
- ✅ **Grammar Groups** - Learn the rules while practicing
- ✅ **Bulgarian Translations** - See what the word means
- ✅ **Smart Randomization** - Avoids recently seen words
- ✅ **Progress Tracking** - See your score
- ✅ **Dark/Light Theme** - Easy on the eyes
- ✅ **CSV Import** - Easy data management
- ✅ **Runs on Raspberry Pi** - Lightweight and efficient

## Quick Start

```bash
# Install dependencies
cd norsk-drill
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the app
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Access at http://localhost:8000
```

## Import Data

1. Go to `http://localhost:8000/admin/adjectives`
2. Upload `static/adjectives_with_groups_BG.csv`
3. Go to `http://localhost:8000/admin/verbs`
4. Upload `static/verbs_with_groups_BG.csv`

## Grammar Groups

Based on "På vei til norsk grammatikk", words are organized into groups:

### Adjectives
- **Group 1**: Regular adjectives (+t neuter, +e plural)
- **Group 2**: Unchanging adjectives
- **Group 3**: No neuter ending, +e plural
- **Group 4**: Ending in -å (+tt neuter only)

### Verbs
- **Group 1**: Short vowel + 2+ consonants (-et/-et)
- **Group 2**: Long vowel + single consonant (-te/-t)
- **Group 3**: Ending in v/g/gg or diphthong (-de/-d)
- **Group 4**: Ending in stressed vowel (-dde/-dd)
- **Irregular**: Common irregular verbs

## Tech Stack

- **Backend**: FastAPI + Python 3.11+
- **Database**: SQLite + SQLAlchemy (async)
- **Frontend**: Jinja2 templates + Vanilla JS
- **Styling**: CSS (dark/light theme)
- **Storage**: LocalStorage for preferences and progress

## Project Structure

```
norsk-drill/
├── app/
│   ├── main.py              # FastAPI app
│   ├── settings.py          # Config
│   ├── db.py                # Database models
│   ├── crud.py              # Database operations
│   ├── routers/
│   │   ├── practice.py      # Practice routes & API
│   │   └── admin.py         # Admin panel
│   └── templates/
│       ├── base.html
│       ├── home.html
│       ├── practice/        # Practice pages
│       └── admin/           # Admin pages
├── static/
│   ├── adjectives_with_groups_BG.csv
│   └── verbs_with_groups_BG.csv
├── data/
│   └── norsk_drill.db       # Created automatically
├── requirements.txt
└── README.md
```

## Development

```bash
# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Deployment (Raspberry Pi)

See [GIT_SETUP.md](GIT_SETUP.md) for full Git workflow.

```bash
# As systemd service
sudo systemctl enable norsk-drill
sudo systemctl start norsk-drill
```

## License

Personal use only.

## Credits

Grammar rules based on "På vei til norsk grammatikk" textbook.
