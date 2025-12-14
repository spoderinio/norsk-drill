"""Practice routes and API endpoints."""
from fastapi import APIRouter, Depends, Request as FastAPIRequest, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db import get_db
from app import crud

router = APIRouter(tags=["practice"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: FastAPIRequest):
    """Home page with menu."""
    return templates.TemplateResponse("home.html", {
        "request": request,
        "title": "Norsk Drill"
    })


# ========== NOUNS ==========
@router.get("/practice/nouns", response_class=HTMLResponse)
async def practice_nouns(request: FastAPIRequest, tag: Optional[str] = Query(None)):
    """Noun practice page."""
    return templates.TemplateResponse("practice/nouns.html", {
        "request": request,
        "title": "Practice Nouns",
        "tag": tag
    })


@router.get("/api/nouns/random")
async def get_random_noun_api(
    exclude_ids: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get a random noun."""
    exclude_list = []
    if exclude_ids:
        exclude_list = [int(x) for x in exclude_ids.split(',') if x.strip().isdigit()]
    
    noun = await crud.get_random_noun(db, exclude_ids=exclude_list, tag=tag)
    
    if not noun:
        return JSONResponse({"error": "No more items available"}, status_code=404)
    
    return {
        "id": noun.id,
        "article": noun.article,
        "word": noun.word,
        "translations": noun.translations if noun.translations else []
    }


@router.post("/api/nouns/{noun_id}/check")
async def check_noun_answer(
    noun_id: int,
    request: FastAPIRequest,
    db: AsyncSession = Depends(get_db)
):
    """Validate noun answer."""
    body = await request.json()
    
    noun = await crud.get_noun(db, noun_id)
    if not noun:
        return JSONResponse({"error": "Noun not found"}, status_code=404)
    
    translations = noun.translations if isinstance(noun.translations, list) else []
    
    result = {
        "article_correct": True,
        "translation_correct": True,
        "correct_article": noun.article,
        "correct_translations": translations,
        "matched_translation": None
    }
    
    # Check article if provided
    article = body.get('article')
    if article and article.strip():
        result["article_correct"] = article.lower().strip() == noun.article.lower()
    
    # Check translation
    translation = body.get('translation')
    if translation and translation.strip():
        user_trans = translation.lower().strip()
        for correct_trans in translations:
            if user_trans == correct_trans.lower().strip():
                result["translation_correct"] = True
                result["matched_translation"] = correct_trans
                break
        else:
            result["translation_correct"] = False
    
    result["all_correct"] = result["article_correct"] and result["translation_correct"]
    
    return result


# ========== VERBS ==========
@router.get("/practice/verbs", response_class=HTMLResponse)
async def practice_verbs(request: FastAPIRequest, tag: Optional[str] = Query(None)):
    """Verb practice page."""
    return templates.TemplateResponse("practice/verbs.html", {
        "request": request,
        "title": "Practice Verbs",
        "tag": tag
    })


@router.get("/api/verbs/random")
async def get_random_verb_api(
    exclude_ids: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get a random verb."""
    exclude_list = []
    if exclude_ids:
        exclude_list = [int(x) for x in exclude_ids.split(',') if x.strip().isdigit()]
    
    verb = await crud.get_random_verb(db, exclude_ids=exclude_list, tag=tag)
    
    if not verb:
        return JSONResponse({"error": "No more items available"}, status_code=404)
    
    return {
        "id": verb.id,
        "infinitive": verb.infinitive,
        "presens": verb.presens,
        "preteritum": verb.preteritum,
        "perfect_participle": verb.perfect_participle,
        "translations": verb.translations if verb.translations else [],
        "group": verb.group,  # NEW
        "group_description": verb.group_description  # NEW
    }


@router.post("/api/verbs/{verb_id}/check")
async def check_verb_answer(
    verb_id: int,
    request: FastAPIRequest,
    db: AsyncSession = Depends(get_db)
):
    """Validate verb answer."""
    body = await request.json()
    
    verb = await crud.get_verb(db, verb_id)
    if not verb:
        return JSONResponse({"error": "Verb not found"}, status_code=404)
    
    translations = verb.translations if isinstance(verb.translations, list) else []
    
    result = {
        "presens_correct": True,
        "preteritum_correct": True,
        "perfect_correct": True,
        "translation_correct": True,
        "correct_presens": verb.presens,
        "correct_preteritum": verb.preteritum,
        "correct_perfect": verb.perfect_participle,
        "correct_translations": translations
    }
    
    # Check each field if provided
    presens = body.get('presens')
    if presens and presens.strip() and verb.presens:
        result["presens_correct"] = presens.lower().strip() == verb.presens.lower().strip()
    
    preteritum = body.get('preteritum')
    if preteritum and preteritum.strip() and verb.preteritum:
        result["preteritum_correct"] = preteritum.lower().strip() == verb.preteritum.lower().strip()
    
    perfect = body.get('perfect_participle')
    if perfect and perfect.strip() and verb.perfect_participle:
        result["perfect_correct"] = perfect.lower().strip() == verb.perfect_participle.lower().strip()
    
    translation = body.get('translation')
    if translation and translation.strip():
        user_trans = translation.lower().strip()
        result["translation_correct"] = any(user_trans == t.lower().strip() for t in translations)
    
    result["all_correct"] = all([
        result["presens_correct"],
        result["preteritum_correct"],
        result["perfect_correct"],
        result["translation_correct"]
    ])
    
    return result


# ========== ADJECTIVES ==========
@router.get("/practice/adjectives", response_class=HTMLResponse)
async def practice_adjectives(request: FastAPIRequest, tag: Optional[str] = Query(None)):
    """Adjective practice page."""
    return templates.TemplateResponse("practice/adjectives.html", {
        "request": request,
        "title": "Practice Adjectives",
        "tag": tag
    })


@router.get("/api/adjectives/random")
async def get_random_adjective_api(
    exclude_ids: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get a random adjective."""
    exclude_list = []
    if exclude_ids:
        exclude_list = [int(x) for x in exclude_ids.split(',') if x.strip().isdigit()]
    
    adj = await crud.get_random_adjective(db, exclude_ids=exclude_list, tag=tag)
    
    if not adj:
        return JSONResponse({"error": "No more items available"}, status_code=404)
    
    return {
        "id": adj.id,
        "base": adj.base,
        "neuter": adj.neuter,
        "plural": adj.plural,
        "translations": adj.translations if adj.translations else [],
        "group": adj.group,  # NEW
        "group_description": adj.group_description  # NEW
    }


@router.post("/api/adjectives/{adjective_id}/check")
async def check_adjective_answer(
    adjective_id: int,
    request: FastAPIRequest,
    db: AsyncSession = Depends(get_db)
):
    """Validate adjective answer."""
    body = await request.json()
    
    adj = await crud.get_adjective(db, adjective_id)
    if not adj:
        return JSONResponse({"error": "Adjective not found"}, status_code=404)
    
    translations = adj.translations if isinstance(adj.translations, list) else []
    
    result = {
        "neuter_correct": True,
        "plural_correct": True,
        "translation_correct": True,
        "correct_neuter": adj.neuter,
        "correct_plural": adj.plural,
        "correct_translations": translations
    }
    
    neuter = body.get('neuter')
    if neuter and neuter.strip() and adj.neuter:
        result["neuter_correct"] = neuter.lower().strip() == adj.neuter.lower().strip()
    
    plural = body.get('plural')
    if plural and plural.strip() and adj.plural:
        result["plural_correct"] = plural.lower().strip() == adj.plural.lower().strip()
    
    translation = body.get('translation')
    if translation and translation.strip():
        user_trans = translation.lower().strip()
        result["translation_correct"] = any(user_trans == t.lower().strip() for t in translations)
    
    result["all_correct"] = all([
        result["neuter_correct"],
        result["plural_correct"],
        result["translation_correct"]
    ])
    
    return result
