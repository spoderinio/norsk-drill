"""Practice routes and API endpoints."""
from fastapi import APIRouter, Depends, Request as FastAPIRequest, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import re

from app.db import get_db
from app import crud

router = APIRouter(tags=["practice"])
templates = Jinja2Templates(directory="app/templates")


def normalize_translation(text: str) -> str:
    """
    Normalize translation by removing text in parentheses and cleaning up.
    
    Example: "време (навън)" -> "време"
    """
    # Remove text in parentheses
    text = re.sub(r'\s*\([^)]*\)', '', text)
    # Clean up extra spaces
    text = ' '.join(text.split())
    return text.lower().strip()


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
    
    # Check translation (with normalization to ignore parentheses)
    translation = body.get('translation')
    if translation and translation.strip():
        user_trans = normalize_translation(translation)
        for correct_trans in translations:
            if user_trans == normalize_translation(correct_trans):
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
        "group": verb.group,
        "group_description": verb.group_description
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
        "presens_correct": False,  # FIXED: Default False
        "preteritum_correct": False,  # FIXED: Default False
        "perfect_correct": False,  # FIXED: Default False
        "translation_correct": False,  # FIXED: Default False
        "correct_presens": verb.presens,
        "correct_preteritum": verb.preteritum,
        "correct_perfect": verb.perfect_participle,
        "correct_translations": translations
    }
    
    # Check each field if provided
    presens = body.get('presens')
    if presens and presens.strip():
        if verb.presens:
            result["presens_correct"] = presens.lower().strip() == verb.presens.lower().strip()
        else:
            # If no correct answer exists, mark as correct if empty
            result["presens_correct"] = False
    else:
        # Empty input - incorrect
        result["presens_correct"] = False
    
    preteritum = body.get('preteritum')
    if preteritum and preteritum.strip():
        if verb.preteritum:
            result["preteritum_correct"] = preteritum.lower().strip() == verb.preteritum.lower().strip()
        else:
            result["preteritum_correct"] = False
    else:
        result["preteritum_correct"] = False
    
    perfect = body.get('perfect_participle')
    if perfect and perfect.strip():
        if verb.perfect_participle:
            result["perfect_correct"] = perfect.lower().strip() == verb.perfect_participle.lower().strip()
        else:
            result["perfect_correct"] = False
    else:
        result["perfect_correct"] = False
    
    # Check translation (with normalization to ignore parentheses)
    translation = body.get('translation')
    if translation and translation.strip():
        user_trans = normalize_translation(translation)
        result["translation_correct"] = any(
            user_trans == normalize_translation(t) for t in translations
        )
    else:
        result["translation_correct"] = False
    
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
        "group": adj.group,
        "group_description": adj.group_description
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
        "neuter_correct": False,  # FIXED: Default False
        "plural_correct": False,  # FIXED: Default False
        "translation_correct": False,  # FIXED: Default False
        "correct_neuter": adj.neuter,
        "correct_plural": adj.plural,
        "correct_translations": translations
    }
    
    neuter = body.get('neuter')
    if neuter and neuter.strip():
        if adj.neuter:
            result["neuter_correct"] = neuter.lower().strip() == adj.neuter.lower().strip()
        else:
            result["neuter_correct"] = False
    else:
        result["neuter_correct"] = False
    
    plural = body.get('plural')
    if plural and plural.strip():
        if adj.plural:
            result["plural_correct"] = plural.lower().strip() == adj.plural.lower().strip()
        else:
            result["plural_correct"] = False
    else:
        result["plural_correct"] = False
    
    # Check translation (with normalization to ignore parentheses)
    translation = body.get('translation')
    if translation and translation.strip():
        user_trans = normalize_translation(translation)
        result["translation_correct"] = any(
            user_trans == normalize_translation(t) for t in translations
        )
    else:
        result["translation_correct"] = False
    
    result["all_correct"] = all([
        result["neuter_correct"],
        result["plural_correct"],
        result["translation_correct"]
    ])
    
    return result


# ========== PHRASES ==========
@router.get("/practice/phrases", response_class=HTMLResponse)
async def practice_phrases(request: FastAPIRequest, category: Optional[str] = Query(None)):
    """Phrase practice page."""
    return templates.TemplateResponse("practice/phrases.html", {
        "request": request,
        "title": "Practice Phrases",
        "category": category
    })


@router.get("/api/phrases/random")
async def get_random_phrase_api(
    exclude_ids: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get a random phrase."""
    exclude_list = []
    if exclude_ids:
        exclude_list = [int(x) for x in exclude_ids.split(',') if x.strip().isdigit()]
    
    phrase = await crud.get_random_phrase(db, exclude_ids=exclude_list, category=category)
    
    if not phrase:
        return JSONResponse({"error": "No more items available"}, status_code=404)
    
    return {
        "id": phrase.id,
        "norwegian": phrase.norwegian,
        "translations": phrase.translations if phrase.translations else [],
        "category": phrase.category,
        "notes": phrase.notes
    }


@router.post("/api/phrases/{phrase_id}/check")
async def check_phrase_answer(
    phrase_id: int,
    request: FastAPIRequest,
    db: AsyncSession = Depends(get_db)
):
    """Validate phrase answer."""
    body = await request.json()
    
    phrase = await crud.get_phrase(db, phrase_id)
    if not phrase:
        return JSONResponse({"error": "Phrase not found"}, status_code=404)
    
    translations = phrase.translations if isinstance(phrase.translations, list) else []
    
    result = {
        "translation_correct": False,
        "correct_translations": translations
    }
    
    # Check translation (with normalization to ignore parentheses)
    translation = body.get('translation')
    if translation and translation.strip():
        user_trans = normalize_translation(translation)
        result["translation_correct"] = any(
            user_trans == normalize_translation(t) for t in translations
        )
    else:
        result["translation_correct"] = False
    
    result["all_correct"] = result["translation_correct"]
    
    return result
