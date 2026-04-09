"""Practice router - v3.0"""
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db, LEVELS, CustomCategory
from sqlalchemy import select
import app.crud as crud

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# ── HOME ─────────────────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    noun_count = await crud.count_nouns(db)
    # Custom categories with entry counts
    from app.db import CustomCategory, CustomEntry
    from sqlalchemy import func as sqlfunc
    cats_result = await db.execute(select(CustomCategory).order_by(CustomCategory.name))
    raw_cats = cats_result.scalars().all()
    custom_cats = []
    for cat in raw_cats:
        r = await db.execute(select(sqlfunc.count(CustomEntry.id)).where(CustomEntry.category_id == cat.id))
        cat.entry_count = r.scalar() or 0
        custom_cats.append(cat)
    verb_count = await crud.count_verbs(db)
    adj_count = await crud.count_adjectives(db)
    phrase_count = await crud.count_phrases(db)
    qw_count = await crud.count_question_words(db)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "noun_count": noun_count,
        "custom_cats": custom_cats,
        "verb_count": verb_count,
        "adj_count": adj_count,
        "phrase_count": phrase_count,
        "qw_count": qw_count,
        "levels": LEVELS,
    })


# ── NOUNS ─────────────────────────────────────────────────────────────────────

@router.get("/practice/nouns", response_class=HTMLResponse)
async def practice_nouns(request: Request, level: str = "all"):
    return templates.TemplateResponse("practice/nouns.html", {
        "request": request, "selected_level": level, "levels": LEVELS
    })


@router.post("/practice/nouns/next")
async def next_noun(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    exclude = data.get("seen_ids", [])
    level = data.get("level", "all")
    noun = await crud.get_random_noun(db, exclude, level)
    if not noun:
        return JSONResponse({"done": True})
    return JSONResponse({
        "done": False,
        "id": noun.id,
        "article": noun.article,
        "word": noun.word,
        "definite": noun.definite,
        "plural": noun.plural,
        "translations": noun.translations,
        "level": noun.level,
    })


@router.post("/practice/nouns/check")
async def check_noun(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    noun = await crud.get_noun(db, data["id"])
    if not noun:
        return JSONResponse({"error": True})
    correct = await crud.check_noun_answer(noun, data.get("answer", ""))
    return JSONResponse({
        "correct": correct,
        "article": noun.article,
        "word": noun.word,
        "translations": noun.translations,
        "level": noun.level,
    })


# ── VERBS ─────────────────────────────────────────────────────────────────────

@router.get("/practice/verbs", response_class=HTMLResponse)
async def practice_verbs(request: Request, level: str = "all"):
    return templates.TemplateResponse("practice/verbs.html", {
        "request": request, "selected_level": level, "levels": LEVELS
    })


@router.post("/practice/verbs/next")
async def next_verb(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    exclude = data.get("seen_ids", [])
    level = data.get("level", "all")
    verb = await crud.get_random_verb(db, exclude, level)
    if not verb:
        return JSONResponse({"done": True})
    return JSONResponse({
        "done": False,
        "id": verb.id,
        "infinitive": verb.infinitive,
        "presens": verb.present,
        "preteritum": verb.preteritum,
        "perfect": verb.perfect_participle,
        "translations": verb.translations,
        "group": verb.group,
        "group_description": verb.group_description,
        "level": verb.level,
    })


@router.post("/practice/verbs/check")
async def check_verb(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    verb = await crud.get_verb(db, data["id"])
    if not verb:
        return JSONResponse({"error": True})
    result = await crud.check_verb_answer(
        verb, data.get("presens", ""), data.get("preteritum", ""), data.get("perfect", "")
    )
    return JSONResponse({
        **result,
        "infinitive": verb.infinitive,
        "presens": verb.present,
        "preteritum": verb.preteritum,
        "perfect": verb.perfect_participle,
        "translations": verb.translations,
        "group": verb.group,
        "group_description": verb.group_description,
        "level": verb.level,
    })


# ── ADJECTIVES ────────────────────────────────────────────────────────────────

@router.get("/practice/adjectives", response_class=HTMLResponse)
async def practice_adjectives(request: Request, level: str = "all"):
    return templates.TemplateResponse("practice/adjectives.html", {
        "request": request, "selected_level": level, "levels": LEVELS
    })


@router.post("/practice/adjectives/next")
async def next_adjective(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    exclude = data.get("seen_ids", [])
    level = data.get("level", "all")
    adj = await crud.get_random_adjective(db, exclude, level)
    if not adj:
        return JSONResponse({"done": True})
    return JSONResponse({
        "done": False,
        "id": adj.id,
        "base": adj.base,
        "neuter": adj.neuter,
        "plural": adj.plural,
        "translations": adj.translations,
        "group": adj.group,
        "group_description": adj.group_description,
        "level": adj.level,
    })


@router.post("/practice/adjectives/check")
async def check_adjective(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    adj = await crud.get_adjective(db, data["id"])
    if not adj:
        return JSONResponse({"error": True})
    result = await crud.check_adjective_answer(
        adj, data.get("neuter", ""), data.get("plural", ""), data.get("translation", "")
    )
    return JSONResponse({
        **result,
        "base": adj.base,
        "neuter": adj.neuter,
        "plural": adj.plural,
        "translations": adj.translations,
        "group": adj.group,
        "group_description": adj.group_description,
        "level": adj.level,
    })


# ── PHRASES ───────────────────────────────────────────────────────────────────

@router.get("/practice/phrases", response_class=HTMLResponse)
async def practice_phrases(request: Request, level: str = "all"):
    return templates.TemplateResponse("practice/phrases.html", {
        "request": request, "selected_level": level, "levels": LEVELS
    })


@router.post("/practice/phrases/next")
async def next_phrase(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    exclude = data.get("seen_ids", [])
    level = data.get("level", "all")
    phrase = await crud.get_random_phrase(db, exclude, level)
    if not phrase:
        return JSONResponse({"done": True})
    return JSONResponse({
        "done": False,
        "id": phrase.id,
        "norwegian": phrase.norwegian,
        "translations": phrase.translations,
        "level": phrase.level,
    })


@router.post("/practice/phrases/check")
async def check_phrase(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    phrase = await crud.get_phrase(db, data["id"])
    if not phrase:
        return JSONResponse({"error": True})
    correct = await crud.check_phrase_answer(phrase, data.get("answer", ""))
    return JSONResponse({
        "correct": correct,
        "norwegian": phrase.norwegian,
        "translations": phrase.translations,
        "level": phrase.level,
    })


# ── QUESTION WORDS ────────────────────────────────────────────────────────────

@router.get("/practice/question-words", response_class=HTMLResponse)
async def practice_question_words(request: Request):
    return templates.TemplateResponse("practice/question_words.html", {"request": request})


@router.post("/practice/question-words/next")
async def next_question_word(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    exclude = data.get("seen_ids", [])
    qw = await crud.get_random_question_word(db, exclude)
    if not qw:
        return JSONResponse({"done": True})
    return JSONResponse({
        "done": False,
        "id": qw.id,
        "norwegian": qw.norwegian,
        "translations": qw.translations,
        "example_no": qw.example_no,
        "example_bg": qw.example_bg,
        "notes": qw.notes,
    })


@router.post("/practice/question-words/check")
async def check_question_word(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    qw = await crud.get_question_word(db, data["id"])
    if not qw:
        return JSONResponse({"error": True})
    reverse = data.get("reverse", False)
    if reverse:
        correct = crud._normalize(data.get("answer", "")) == crud._normalize(qw.norwegian or "")
    else:
        correct = await crud.check_question_word_answer(qw, data.get("answer", ""))
    return JSONResponse({
        "correct": correct,
        "norwegian": qw.norwegian,
        "translations": qw.translations,
        "example_no": qw.example_no,
        "example_bg": qw.example_bg,
        "notes": qw.notes,
    })


# ── SEARCH ────────────────────────────────────────────────────────────────────

@router.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: str = ""):
    return templates.TemplateResponse("search.html", {"request": request, "query": q, "results": []})


@router.get("/search/results")
async def search_results(q: str, db: AsyncSession = Depends(get_db)):
    if not q or len(q.strip()) < 2:
        return JSONResponse({"results": []})
    results = await crud.search_all(db, q.strip())
    return JSONResponse({"results": results})
