"""Admin routes for managing vocabulary."""
from fastapi import APIRouter, Depends, Request as FastAPIRequest, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import csv
import io

from app.db import get_db
from app import crud

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def admin_home(request: FastAPIRequest, db: AsyncSession = Depends(get_db)):
    """Admin home page."""
    nouns = await crud.get_all_nouns(db)
    verbs = await crud.get_all_verbs(db)
    adjectives = await crud.get_all_adjectives(db)
    phrases = await crud.get_all_phrases(db)  # NEW
    
    return templates.TemplateResponse("admin/index.html", {
        "request": request,
        "title": "Admin Panel",
        "noun_count": len(nouns),
        "verb_count": len(verbs),
        "adjective_count": len(adjectives),
        "phrase_count": len(phrases)  # NEW
    })


# ========== NOUNS ==========

@router.get("/nouns", response_class=HTMLResponse)
async def admin_nouns(request: FastAPIRequest, db: AsyncSession = Depends(get_db)):
    """List all nouns."""
    nouns = await crud.get_all_nouns(db)
    return templates.TemplateResponse("admin/nouns.html", {
        "request": request,
        "title": "Manage Nouns",
        "nouns": nouns
    })


@router.post("/nouns/import-text")
async def import_nouns_text(
    text_data: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Import nouns from text format (en/ei/et word – translation1, translation2)."""
    lines = text_data.strip().split('\n')
    added = 0
    skipped = 0
    
    for line in lines:
        line = line.strip()
        if not line or '–' not in line:
            continue
        
        # Split on en-dash or regular dash
        parts = line.split('–') if '–' in line else line.split('-', 1)
        if len(parts) != 2:
            continue
        
        left = parts[0].strip()
        right = parts[1].strip()
        
        # Parse article and word
        left_parts = left.split(None, 1)
        if len(left_parts) != 2:
            continue
        
        article, word = left_parts
        if article not in ['en', 'ei', 'et']:
            continue
        
        # Parse translations
        translations = [t.strip() for t in right.split(',')]
        
        result = await crud.create_noun(db, article, word, translations)
        if result:
            added += 1
        else:
            skipped += 1
    
    return RedirectResponse(url="/admin/nouns", status_code=303)


@router.post("/nouns/import-csv")
async def import_nouns_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Import nouns from CSV."""
    content = await file.read()
    text = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(text))
    
    added = 0
    skipped = 0
    
    for row in reader:
        article = row.get('article', '').strip()
        word = row.get('word', '').strip()
        trans_str = row.get('translations', '').strip()
        definite = row.get('definite', '').strip() or None
        plural = row.get('plural', '').strip() or None
        
        if not article or not word or article not in ['en', 'ei', 'et']:
            continue
        
        if '|' in trans_str:
            translations = [t.strip() for t in trans_str.split('|')]
        else:
            translations = [t.strip() for t in trans_str.split(',')]
        
        result = await crud.create_noun(
            db, 
            article, 
            word, 
            translations,
            definite=definite,
            plural=plural
        )
        
        if result:
            added += 1
        else:
            skipped += 1
    
    return RedirectResponse(url="/admin/nouns", status_code=303)


@router.get("/nouns/{noun_id}/edit", response_class=HTMLResponse)
async def edit_noun_page(
    noun_id: int,
    request: FastAPIRequest,
    db: AsyncSession = Depends(get_db)
):
    """Edit noun page."""
    noun = await crud.get_noun(db, noun_id)
    if not noun:
        return RedirectResponse(url="/admin/nouns", status_code=303)
    
    return templates.TemplateResponse("admin/edit_noun.html", {
        "request": request,
        "title": "Edit Noun",
        "noun": noun
    })


@router.post("/nouns/{noun_id}/edit")
async def edit_noun(
    noun_id: int,
    article: str = Form(...),
    word: str = Form(...),
    definite: str = Form(""),
    plural: str = Form(""),
    translations: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Update a noun."""
    trans_list = [t.strip() for t in translations.split('|') if t.strip()]
    
    await crud.update_noun(
        db,
        noun_id,
        article=article.strip(),
        word=word.strip(),
        definite=definite.strip() or None,
        plural=plural.strip() or None,
        translations=trans_list
    )
    
    return RedirectResponse(url="/admin/nouns", status_code=303)


@router.post("/nouns/{noun_id}/delete")
async def delete_noun(noun_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a noun."""
    await crud.delete_noun(db, noun_id)
    return RedirectResponse(url="/admin/nouns", status_code=303)


# ========== VERBS ==========

@router.get("/verbs", response_class=HTMLResponse)
async def admin_verbs(request: FastAPIRequest, db: AsyncSession = Depends(get_db)):
    """List all verbs."""
    verbs = await crud.get_all_verbs(db)
    return templates.TemplateResponse("admin/verbs.html", {
        "request": request,
        "title": "Manage Verbs",
        "verbs": verbs
    })


@router.post("/verbs/import-csv")
async def import_verbs_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Import verbs from CSV."""
    content = await file.read()
    text = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(text))
    
    added = 0
    skipped = 0
    
    for row in reader:
        infinitive = row.get('infinitive', '').strip()
        presens = row.get('presens', '').strip() or None
        preteritum = row.get('preteritum', '').strip() or None
        perfect = row.get('perfect', '').strip() or None
        trans_str = row.get('translations', '').strip()
        group = row.get('group', '').strip() or None
        group_desc = row.get('group_description', '').strip() or None
        
        if not infinitive or not trans_str:
            continue
        
        if '|' in trans_str:
            translations = [t.strip() for t in trans_str.split('|')]
        else:
            translations = [t.strip() for t in trans_str.split(',')]
        
        result = await crud.create_verb(
            db,
            infinitive=infinitive,
            presens=presens,
            preteritum=preteritum,
            perfect_participle=perfect,
            translations=translations,
            group=group,
            group_description=group_desc
        )
        
        if result:
            added += 1
        else:
            skipped += 1
    
    return RedirectResponse(url="/admin/verbs", status_code=303)


@router.get("/verbs/{verb_id}/edit", response_class=HTMLResponse)
async def edit_verb_page(
    verb_id: int,
    request: FastAPIRequest,
    db: AsyncSession = Depends(get_db)
):
    """Edit verb page."""
    verb = await crud.get_verb(db, verb_id)
    if not verb:
        return RedirectResponse(url="/admin/verbs", status_code=303)
    
    return templates.TemplateResponse("admin/edit_verb.html", {
        "request": request,
        "title": "Edit Verb",
        "verb": verb
    })


@router.post("/verbs/{verb_id}/edit")
async def edit_verb(
    verb_id: int,
    infinitive: str = Form(...),
    presens: str = Form(""),
    preteritum: str = Form(""),
    perfect: str = Form(""),
    translations: str = Form(...),
    group: str = Form(""),
    group_description: str = Form(""),
    db: AsyncSession = Depends(get_db)
):
    """Update a verb."""
    trans_list = [t.strip() for t in translations.split('|') if t.strip()]
    
    await crud.update_verb(
        db,
        verb_id,
        infinitive=infinitive.strip(),
        presens=presens.strip() or None,
        preteritum=preteritum.strip() or None,
        perfect_participle=perfect.strip() or None,
        translations=trans_list,
        group=group.strip() or None,
        group_description=group_description.strip() or None
    )
    
    return RedirectResponse(url="/admin/verbs", status_code=303)


@router.post("/verbs/{verb_id}/delete")
async def delete_verb(verb_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a verb."""
    await crud.delete_verb(db, verb_id)
    return RedirectResponse(url="/admin/verbs", status_code=303)


# ========== ADJECTIVES ==========

@router.get("/adjectives", response_class=HTMLResponse)
async def admin_adjectives(request: FastAPIRequest, db: AsyncSession = Depends(get_db)):
    """List all adjectives."""
    adjectives = await crud.get_all_adjectives(db)
    return templates.TemplateResponse("admin/adjectives.html", {
        "request": request,
        "title": "Manage Adjectives",
        "adjectives": adjectives
    })


@router.post("/adjectives/import-csv")
async def import_adjectives_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Import adjectives from CSV."""
    content = await file.read()
    text = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(text))
    
    added = 0
    skipped = 0
    
    for row in reader:
        base = row.get('base', '').strip()
        neuter = row.get('neuter', '').strip() or None
        plural = row.get('plural', '').strip() or None
        trans_str = row.get('translations', '').strip()
        group = row.get('group', '').strip() or None
        group_desc = row.get('group_description', '').strip() or None
        
        if not base or not trans_str:
            continue
        
        if '|' in trans_str:
            translations = [t.strip() for t in trans_str.split('|')]
        else:
            translations = [t.strip() for t in trans_str.split(',')]
        
        result = await crud.create_adjective(
            db,
            base=base,
            neuter=neuter,
            plural=plural,
            translations=translations,
            group=group,
            group_description=group_desc
        )
        
        if result:
            added += 1
        else:
            skipped += 1
    
    return RedirectResponse(url="/admin/adjectives", status_code=303)


@router.get("/adjectives/{adjective_id}/edit", response_class=HTMLResponse)
async def edit_adjective_page(
    adjective_id: int,
    request: FastAPIRequest,
    db: AsyncSession = Depends(get_db)
):
    """Edit adjective page."""
    adj = await crud.get_adjective(db, adjective_id)
    if not adj:
        return RedirectResponse(url="/admin/adjectives", status_code=303)
    
    return templates.TemplateResponse("admin/edit_adjective.html", {
        "request": request,
        "title": "Edit Adjective",
        "adjective": adj
    })


@router.post("/adjectives/{adjective_id}/edit")
async def edit_adjective(
    adjective_id: int,
    base: str = Form(...),
    neuter: str = Form(""),
    plural: str = Form(""),
    translations: str = Form(...),
    group: str = Form(""),
    group_description: str = Form(""),
    db: AsyncSession = Depends(get_db)
):
    """Update an adjective."""
    trans_list = [t.strip() for t in translations.split('|') if t.strip()]
    
    await crud.update_adjective(
        db,
        adjective_id,
        base=base.strip(),
        neuter=neuter.strip() or None,
        plural=plural.strip() or None,
        translations=trans_list,
        group=group.strip() or None,
        group_description=group_description.strip() or None
    )
    
    return RedirectResponse(url="/admin/adjectives", status_code=303)


@router.post("/adjectives/{adjective_id}/delete")
async def delete_adjective(adjective_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an adjective."""
    await crud.delete_adjective(db, adjective_id)
    return RedirectResponse(url="/admin/adjectives", status_code=303)


# ========== PHRASES ==========

@router.get("/phrases", response_class=HTMLResponse)
async def admin_phrases(request: FastAPIRequest, db: AsyncSession = Depends(get_db)):
    """List all phrases."""
    phrases = await crud.get_all_phrases(db)
    return templates.TemplateResponse("admin/phrases.html", {
        "request": request,
        "title": "Manage Phrases",
        "phrases": phrases
    })


@router.post("/phrases/import-text")
async def import_phrases_text(
    text_data: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Import phrases from text format (norwegian phrase – bulgarian translation)."""
    lines = text_data.strip().split('\n')
    added = 0
    skipped = 0
    
    for line in lines:
        line = line.strip()
        if not line or '–' not in line:
            continue
        
        # Split on en-dash or regular dash
        parts = line.split('–') if '–' in line else line.split('-', 1)
        if len(parts) != 2:
            continue
        
        norwegian = parts[0].strip()
        right = parts[1].strip()
        
        if not norwegian:
            continue
        
        # Parse translations (comma-separated)
        translations = [t.strip() for t in right.split(',') if t.strip()]
        
        if not translations:
            continue
        
        result = await crud.create_phrase(
            db,
            norwegian=norwegian,
            translations=translations,
            category=None,  # Can be added later via Edit
            notes=None
        )
        
        if result:
            added += 1
        else:
            skipped += 1
    
    return RedirectResponse(url="/admin/phrases", status_code=303)


@router.post("/phrases/import-csv")
async def import_phrases_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Import phrases from CSV."""
    content = await file.read()
    text = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(text))
    
    added = 0
    skipped = 0
    
    for row in reader:
        norwegian = row.get('norwegian', '').strip()
        trans_str = row.get('translations', '').strip()
        category = row.get('category', '').strip() or None
        notes = row.get('notes', '').strip() or None
        
        if not norwegian or not trans_str:
            continue
        
        if '|' in trans_str:
            translations = [t.strip() for t in trans_str.split('|')]
        else:
            translations = [t.strip() for t in trans_str.split(',')]
        
        result = await crud.create_phrase(
            db,
            norwegian=norwegian,
            translations=translations,
            category=category,
            notes=notes
        )
        
        if result:
            added += 1
        else:
            skipped += 1
    
    return RedirectResponse(url="/admin/phrases", status_code=303)


@router.get("/phrases/{phrase_id}/edit", response_class=HTMLResponse)
async def edit_phrase_page(
    phrase_id: int,
    request: FastAPIRequest,
    db: AsyncSession = Depends(get_db)
):
    """Edit phrase page."""
    phrase = await crud.get_phrase(db, phrase_id)
    if not phrase:
        return RedirectResponse(url="/admin/phrases", status_code=303)
    
    return templates.TemplateResponse("admin/edit_phrase.html", {
        "request": request,
        "title": "Edit Phrase",
        "phrase": phrase
    })


@router.post("/phrases/{phrase_id}/edit")
async def edit_phrase(
    phrase_id: int,
    norwegian: str = Form(...),
    translations: str = Form(...),
    category: str = Form(""),
    notes: str = Form(""),
    db: AsyncSession = Depends(get_db)
):
    """Update a phrase."""
    trans_list = [t.strip() for t in translations.split('|') if t.strip()]
    
    await crud.update_phrase(
        db,
        phrase_id,
        norwegian=norwegian.strip(),
        translations=trans_list,
        category=category.strip() or None,
        notes=notes.strip() or None
    )
    
    return RedirectResponse(url="/admin/phrases", status_code=303)


@router.post("/phrases/{phrase_id}/delete")
async def delete_phrase(phrase_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a phrase."""
    await crud.delete_phrase(db, phrase_id)
    return RedirectResponse(url="/admin/phrases", status_code=303)
