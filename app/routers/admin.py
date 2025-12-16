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
    
    return templates.TemplateResponse("admin/index.html", {
        "request": request,
        "title": "Admin Panel",
        "noun_count": len(nouns),
        "verb_count": len(verbs),
        "adjective_count": len(adjectives)
    })


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
    count = 0
    
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
        
        await crud.create_noun(db, article, word, translations)
        count += 1
    
    return RedirectResponse(url="/admin/nouns", status_code=303)



@router.post("/nouns/import-csv")
async def import_nouns_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Import nouns from CSV (article,word,translations)."""
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
        
        # Parse translations (can be separated by | or ,)
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


@router.post("/verbs/import-text")
async def import_verbs_text(
    text_data: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Import verbs from text format."""
    lines = text_data.strip().split('\n')
    count = 0
    
    for line in lines:
        line = line.strip()
        if not line or '–' not in line:
            continue
        
        # Split on en-dash or regular dash
        parts = line.split('–') if '–' in line else line.split('-', 1)
        if len(parts) != 2:
            continue
        
        left = parts[0].strip()  # verb forms
        right = parts[1].strip()  # translations
        
        # Parse verb forms: "infinitive, presens, preteritum, perfect"
        verb_parts = [p.strip() for p in left.split(',')]
        if len(verb_parts) < 1:
            continue
        
        infinitive = verb_parts[0]
        presens = verb_parts[1] if len(verb_parts) > 1 else None
        preteritum = verb_parts[2] if len(verb_parts) > 2 else None
        perfect = verb_parts[3] if len(verb_parts) > 3 else None
        
        # Parse translations
        translations = [t.strip() for t in right.split(',')]
        
        await crud.create_verb(
            db, 
            infinitive=infinitive,
            presens=presens,
            preteritum=preteritum,
            perfect_participle=perfect,
            translations=translations
        )
        count += 1
    
    return RedirectResponse(url="/admin/verbs", status_code=303)


@router.post("/verbs/import-csv")
async def import_verbs_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Import verbs from CSV with groups."""
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
        trans_str = row.get('translation', '').strip()
        group = row.get('group', '').strip() or None
        group_desc = row.get('group_description', '').strip() or None
        
        if not infinitive or not trans_str:
            continue
        
        # Parse translations (can be separated by | or ,)
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


@router.post("/adjectives/import-text")
async def import_adjectives_text(
    text_data: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Import adjectives from text format."""
    lines = text_data.strip().split('\n')
    count = 0
    
    for line in lines:
        line = line.strip()
        if not line or '–' not in line:
            continue
        
        # Split on en-dash or regular dash
        parts = line.split('–') if '–' in line else line.split('-', 1)
        if len(parts) != 2:
            continue
        
        left = parts[0].strip()  # adjective forms
        right = parts[1].strip()  # translations
        
        # Parse adjective forms: "base, neuter, plural"
        adj_parts = [p.strip() for p in left.split(',')]
        if len(adj_parts) < 1:
            continue
        
        base = adj_parts[0]
        neuter = adj_parts[1] if len(adj_parts) > 1 else None
        plural = adj_parts[2] if len(adj_parts) > 2 else None
        
        # Parse translations
        translations = [t.strip() for t in right.split(',')]
        
        await crud.create_adjective(
            db,
            base=base,
            neuter=neuter,
            plural=plural,
            translations=translations
        )
        count += 1
    
    return RedirectResponse(url="/admin/adjectives", status_code=303)


@router.post("/adjectives/import-csv")
async def import_adjectives_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Import adjectives from CSV with groups."""
    content = await file.read()
    text = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(text))
    
    added = 0
    skipped = 0
    
    for row in reader:
        base = row.get('base', '').strip()
        neuter = row.get('neuter', '').strip() or None
        plural = row.get('plural', '').strip() or None
        trans_str = row.get('translation', '').strip()
        group = row.get('group', '').strip() or None
        group_desc = row.get('group_description', '').strip() or None
        
        if not base or not trans_str:
            continue
        
        # Parse translations (can be separated by | or ,)
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


@router.post("/adjectives/{adjective_id}/delete")
async def delete_adjective(adjective_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an adjective."""
    await crud.delete_adjective(db, adjective_id)
    return RedirectResponse(url="/admin/adjectives", status_code=303)
