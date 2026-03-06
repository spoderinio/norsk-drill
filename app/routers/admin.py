"""Admin router - v3.0"""
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db, LEVELS
import app.crud as crud
import csv, io, json

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")


def _parse_translations(s: str) -> list:
    return [t.strip() for t in s.replace("|", ",").split(",") if t.strip()]


# ── INDEX ─────────────────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
async def admin_index(request: Request, db: AsyncSession = Depends(get_db)):
    return templates.TemplateResponse("admin/index.html", {
        "request": request,
        "noun_count": await crud.count_nouns(db),
        "verb_count": await crud.count_verbs(db),
        "adj_count": await crud.count_adjectives(db),
        "phrase_count": await crud.count_phrases(db),
        "qw_count": await crud.count_question_words(db),
    })


# ── NOUNS ─────────────────────────────────────────────────────────────────────

@router.get("/nouns", response_class=HTMLResponse)
async def admin_nouns(request: Request, db: AsyncSession = Depends(get_db)):
    nouns = await crud.get_nouns(db)
    return templates.TemplateResponse("admin/nouns.html", {
        "request": request, "nouns": nouns, "levels": LEVELS
    })


@router.post("/nouns/add")
async def add_noun(request: Request, db: AsyncSession = Depends(get_db),
                   article: str = Form(...), word: str = Form(...),
                   translations: str = Form(...), definite: str = Form(""),
                   plural: str = Form(""), level: str = Form("A")):
    await crud.create_noun(db, article=article, word=word,
                           translations=_parse_translations(translations),
                           definite=definite or None, plural=plural or None,
                           level=level or "A")
    return RedirectResponse("/admin/nouns", status_code=303)


@router.post("/nouns/import-csv")
async def import_nouns_csv(request: Request, db: AsyncSession = Depends(get_db),
                            file: UploadFile = File(...), level: str = Form("A")):
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
    added = skipped = 0
    for row in reader:
        article = row.get("article", "").strip()
        word = row.get("word", "").strip()
        translations_raw = row.get("translations", "").strip()
        if not article or not word or not translations_raw:
            continue
        result = await crud.create_noun(db, article=article, word=word,
                                         translations=_parse_translations(translations_raw),
                                         definite=row.get("definite", "").strip() or None,
                                         plural=row.get("plural", "").strip() or None,
                                         level=level or "A")
        if result:
            added += 1
        else:
            skipped += 1
    return RedirectResponse(f"/admin/nouns?added={added}&skipped={skipped}", status_code=303)


@router.post("/nouns/import-text")
async def import_nouns_text(request: Request, db: AsyncSession = Depends(get_db),
                             text_data: str = Form(...), level: str = Form("A")):
    added = skipped = 0
    for line in text_data.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        sep = "–" if "–" in line else "-"
        parts = line.split(sep, 1)
        if len(parts) != 2:
            continue
        norwegian = parts[0].strip()
        translation = parts[1].strip()
        words = norwegian.split()
        if len(words) < 2:
            continue
        article = words[0]
        word = " ".join(words[1:])
        if article not in ["en", "ei", "et"]:
            continue
        result = await crud.create_noun(db, article=article, word=word,
                                         translations=_parse_translations(translation),
                                         level=level or "A")
        if result:
            added += 1
        else:
            skipped += 1
    return RedirectResponse(f"/admin/nouns?added={added}&skipped={skipped}", status_code=303)


@router.get("/nouns/edit/{noun_id}", response_class=HTMLResponse)
async def edit_noun_form(noun_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    noun = await crud.get_noun(db, noun_id)
    return templates.TemplateResponse("admin/edit_noun.html", {
        "request": request, "noun": noun, "levels": LEVELS
    })


@router.post("/nouns/edit/{noun_id}")
async def edit_noun_save(noun_id: int, request: Request, db: AsyncSession = Depends(get_db),
                          article: str = Form(...), word: str = Form(...),
                          translations: str = Form(...), definite: str = Form(""),
                          plural: str = Form(""), level: str = Form("A")):
    await crud.update_noun(db, noun_id, article=article, word=word,
                            translations=_parse_translations(translations),
                            definite=definite or None, plural=plural or None, level=level or "A")
    return RedirectResponse("/admin/nouns", status_code=303)


@router.post("/nouns/delete/{noun_id}")
async def delete_noun(noun_id: int, db: AsyncSession = Depends(get_db)):
    await crud.delete_noun(db, noun_id)
    return RedirectResponse("/admin/nouns", status_code=303)


# ── VERBS ─────────────────────────────────────────────────────────────────────

@router.get("/verbs", response_class=HTMLResponse)
async def admin_verbs(request: Request, db: AsyncSession = Depends(get_db)):
    verbs = await crud.get_verbs(db)
    return templates.TemplateResponse("admin/verbs.html", {
        "request": request, "verbs": verbs, "levels": LEVELS
    })


@router.post("/verbs/add")
async def add_verb(request: Request, db: AsyncSession = Depends(get_db),
                   infinitive: str = Form(...), presens: str = Form(""),
                   preteritum: str = Form(""), perfect_participle: str = Form(""),
                   translations: str = Form(...), level: str = Form("A"),
                   group: str = Form(""), group_description: str = Form("")):
    await crud.create_verb(db, infinitive=infinitive, presens=presens or None,
                            preteritum=preteritum or None,
                            perfect_participle=perfect_participle or None,
                            translations=_parse_translations(translations),
                            group=group or None, group_description=group_description or None,
                            level=level or "A")
    return RedirectResponse("/admin/verbs", status_code=303)


@router.post("/verbs/import-csv")
async def import_verbs_csv(request: Request, db: AsyncSession = Depends(get_db),
                            file: UploadFile = File(...), level: str = Form("A")):
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
    added = skipped = 0
    for row in reader:
        infinitive = row.get("infinitive", "").strip()
        translations_raw = row.get("translations", "").strip()
        if not infinitive or not translations_raw:
            continue
        result = await crud.create_verb(db,
            infinitive=infinitive,
            presens=row.get("presens", "").strip() or None,
            preteritum=row.get("preteritum", "").strip() or None,
            perfect_participle=row.get("perfect", "").strip() or None,
            translations=_parse_translations(translations_raw),
            group=row.get("group", "").strip() or None,
            group_description=row.get("group_description", "").strip() or None,
            level=level or "A")
        if result:
            added += 1
        else:
            skipped += 1
    return RedirectResponse(f"/admin/verbs?added={added}&skipped={skipped}", status_code=303)


@router.get("/verbs/edit/{verb_id}", response_class=HTMLResponse)
async def edit_verb_form(verb_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    verb = await crud.get_verb(db, verb_id)
    return templates.TemplateResponse("admin/edit_verb.html", {
        "request": request, "verb": verb, "levels": LEVELS
    })


@router.post("/verbs/edit/{verb_id}")
async def edit_verb_save(verb_id: int, request: Request, db: AsyncSession = Depends(get_db),
                          infinitive: str = Form(...), presens: str = Form(""),
                          preteritum: str = Form(""), perfect_participle: str = Form(""),
                          translations: str = Form(...), level: str = Form("A"),
                          group: str = Form(""), group_description: str = Form("")):
    await crud.update_verb(db, verb_id, infinitive=infinitive, presens=presens or None,
                            preteritum=preteritum or None, perfect_participle=perfect_participle or None,
                            translations=_parse_translations(translations),
                            group=group or None, group_description=group_description or None,
                            level=level or "A")
    return RedirectResponse("/admin/verbs", status_code=303)


@router.post("/verbs/delete/{verb_id}")
async def delete_verb(verb_id: int, db: AsyncSession = Depends(get_db)):
    await crud.delete_verb(db, verb_id)
    return RedirectResponse("/admin/verbs", status_code=303)


# ── ADJECTIVES ────────────────────────────────────────────────────────────────

@router.get("/adjectives", response_class=HTMLResponse)
async def admin_adjectives(request: Request, db: AsyncSession = Depends(get_db)):
    adjs = await crud.get_adjectives(db)
    return templates.TemplateResponse("admin/adjectives.html", {
        "request": request, "adjectives": adjs, "levels": LEVELS
    })


@router.post("/adjectives/add")
async def add_adjective(request: Request, db: AsyncSession = Depends(get_db),
                        base: str = Form(...), neuter: str = Form(""),
                        plural: str = Form(""), translations: str = Form(...),
                        level: str = Form("A"), group: str = Form(""),
                        group_description: str = Form("")):
    await crud.create_adjective(db, base=base, neuter=neuter or None,
                                 plural=plural or None,
                                 translations=_parse_translations(translations),
                                 group=group or None, group_description=group_description or None,
                                 level=level or "A")
    return RedirectResponse("/admin/adjectives", status_code=303)


@router.post("/adjectives/import-csv")
async def import_adjectives_csv(request: Request, db: AsyncSession = Depends(get_db),
                                 file: UploadFile = File(...), level: str = Form("A")):
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
    added = skipped = 0
    for row in reader:
        base = row.get("base", "").strip()
        translations_raw = row.get("translations", "").strip()
        if not base or not translations_raw:
            continue
        result = await crud.create_adjective(db,
            base=base,
            neuter=row.get("neuter", "").strip() or None,
            plural=row.get("plural", "").strip() or None,
            translations=_parse_translations(translations_raw),
            group=row.get("group", "").strip() or None,
            group_description=row.get("group_description", "").strip() or None,
            level=level or "A")
        if result:
            added += 1
        else:
            skipped += 1
    return RedirectResponse(f"/admin/adjectives?added={added}&skipped={skipped}", status_code=303)


@router.get("/adjectives/edit/{adj_id}", response_class=HTMLResponse)
async def edit_adjective_form(adj_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    adj = await crud.get_adjective(db, adj_id)
    return templates.TemplateResponse("admin/edit_adjective.html", {
        "request": request, "adjective": adj, "levels": LEVELS
    })


@router.post("/adjectives/edit/{adj_id}")
async def edit_adjective_save(adj_id: int, request: Request, db: AsyncSession = Depends(get_db),
                               base: str = Form(...), neuter: str = Form(""),
                               plural: str = Form(""), translations: str = Form(...),
                               level: str = Form("A"), group: str = Form(""),
                               group_description: str = Form("")):
    await crud.update_adjective(db, adj_id, base=base, neuter=neuter or None,
                                 plural=plural or None,
                                 translations=_parse_translations(translations),
                                 group=group or None, group_description=group_description or None,
                                 level=level or "A")
    return RedirectResponse("/admin/adjectives", status_code=303)


@router.post("/adjectives/delete/{adj_id}")
async def delete_adjective(adj_id: int, db: AsyncSession = Depends(get_db)):
    await crud.delete_adjective(db, adj_id)
    return RedirectResponse("/admin/adjectives", status_code=303)


# ── PHRASES ───────────────────────────────────────────────────────────────────

@router.get("/phrases", response_class=HTMLResponse)
async def admin_phrases(request: Request, db: AsyncSession = Depends(get_db)):
    phrases = await crud.get_phrases(db)
    return templates.TemplateResponse("admin/phrases.html", {
        "request": request, "phrases": phrases, "levels": LEVELS
    })


@router.post("/phrases/add")
async def add_phrase(request: Request, db: AsyncSession = Depends(get_db),
                     norwegian: str = Form(...), translations: str = Form(...),
                     category: str = Form(""), notes: str = Form(""), level: str = Form("A")):
    await crud.create_phrase(db, norwegian=norwegian,
                              translations=_parse_translations(translations),
                              category=category or None, notes=notes or None,
                              level=level or "A")
    return RedirectResponse("/admin/phrases", status_code=303)


@router.post("/phrases/import-text")
async def import_phrases_text(request: Request, db: AsyncSession = Depends(get_db),
                               text_data: str = Form(...), level: str = Form("A")):
    added = skipped = 0
    for line in text_data.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        sep = "–" if "–" in line else "-"
        parts = line.split(sep, 1)
        if len(parts) != 2:
            continue
        norwegian = parts[0].strip()
        translation = parts[1].strip()
        if not norwegian or not translation:
            continue
        result = await crud.create_phrase(db, norwegian=norwegian,
                                           translations=_parse_translations(translation),
                                           level=level or "A")
        if result:
            added += 1
        else:
            skipped += 1
    return RedirectResponse(f"/admin/phrases?added={added}&skipped={skipped}", status_code=303)


@router.post("/phrases/import-csv")
async def import_phrases_csv(request: Request, db: AsyncSession = Depends(get_db),
                              file: UploadFile = File(...), level: str = Form("A")):
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
    added = skipped = 0
    for row in reader:
        norwegian = row.get("norwegian", "").strip()
        translations_raw = row.get("translations", "").strip()
        if not norwegian or not translations_raw:
            continue
        result = await crud.create_phrase(db, norwegian=norwegian,
                                           translations=_parse_translations(translations_raw),
                                           category=row.get("category", "").strip() or None,
                                           notes=row.get("notes", "").strip() or None,
                                           level=level or "A")
        if result:
            added += 1
        else:
            skipped += 1
    return RedirectResponse(f"/admin/phrases?added={added}&skipped={skipped}", status_code=303)


@router.get("/phrases/edit/{phrase_id}", response_class=HTMLResponse)
async def edit_phrase_form(phrase_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    phrase = await crud.get_phrase(db, phrase_id)
    return templates.TemplateResponse("admin/edit_phrase.html", {
        "request": request, "phrase": phrase, "levels": LEVELS
    })


@router.post("/phrases/edit/{phrase_id}")
async def edit_phrase_save(phrase_id: int, request: Request, db: AsyncSession = Depends(get_db),
                            norwegian: str = Form(...), translations: str = Form(...),
                            category: str = Form(""), notes: str = Form(""), level: str = Form("A")):
    await crud.update_phrase(db, phrase_id, norwegian=norwegian,
                              translations=_parse_translations(translations),
                              category=category or None, notes=notes or None,
                              level=level or "A")
    return RedirectResponse("/admin/phrases", status_code=303)


@router.post("/phrases/delete/{phrase_id}")
async def delete_phrase(phrase_id: int, db: AsyncSession = Depends(get_db)):
    await crud.delete_phrase(db, phrase_id)
    return RedirectResponse("/admin/phrases", status_code=303)


# ── QUESTION WORDS ────────────────────────────────────────────────────────────

@router.get("/question-words", response_class=HTMLResponse)
async def admin_question_words(request: Request, db: AsyncSession = Depends(get_db)):
    qwords = await crud.get_question_words(db)
    return templates.TemplateResponse("admin/question_words.html", {
        "request": request, "question_words": qwords
    })


@router.post("/question-words/add")
async def add_question_word(request: Request, db: AsyncSession = Depends(get_db),
                             norwegian: str = Form(...), translations: str = Form(...),
                             example_no: str = Form(""), example_bg: str = Form(""),
                             notes: str = Form("")):
    await crud.create_question_word(db, norwegian=norwegian,
                                     translations=_parse_translations(translations),
                                     example_no=example_no or None,
                                     example_bg=example_bg or None,
                                     notes=notes or None)
    return RedirectResponse("/admin/question-words", status_code=303)


@router.post("/question-words/import-text")
async def import_question_words_text(request: Request, db: AsyncSession = Depends(get_db),
                                      text_data: str = Form(...)):
    added = skipped = 0
    for line in text_data.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        sep = "–" if "–" in line else "-"
        parts = line.split(sep, 1)
        if len(parts) != 2:
            continue
        norwegian = parts[0].strip()
        translation = parts[1].strip()
        if not norwegian or not translation:
            continue
        result = await crud.create_question_word(db, norwegian=norwegian,
                                                  translations=_parse_translations(translation))
        if result:
            added += 1
        else:
            skipped += 1
    return RedirectResponse(f"/admin/question-words?added={added}&skipped={skipped}", status_code=303)


@router.get("/question-words/edit/{qw_id}", response_class=HTMLResponse)
async def edit_qw_form(qw_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    qw = await crud.get_question_word(db, qw_id)
    return templates.TemplateResponse("admin/edit_question_word.html", {
        "request": request, "qw": qw
    })


@router.post("/question-words/edit/{qw_id}")
async def edit_qw_save(qw_id: int, request: Request, db: AsyncSession = Depends(get_db),
                        norwegian: str = Form(...), translations: str = Form(...),
                        example_no: str = Form(""), example_bg: str = Form(""),
                        notes: str = Form("")):
    await crud.update_question_word(db, qw_id, norwegian=norwegian,
                                     translations=_parse_translations(translations),
                                     example_no=example_no or None,
                                     example_bg=example_bg or None,
                                     notes=notes or None)
    return RedirectResponse("/admin/question-words", status_code=303)


@router.post("/question-words/delete/{qw_id}")
async def delete_qw(qw_id: int, db: AsyncSession = Depends(get_db)):
    await crud.delete_question_word(db, qw_id)
    return RedirectResponse("/admin/question-words", status_code=303)
