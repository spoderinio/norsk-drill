"""Search routes and API endpoints."""
from fastapi import APIRouter, Depends, Request as FastAPIRequest, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional

from app.db import get_db, Noun, Verb, Adjective
from app import crud

router = APIRouter(tags=["search"])
templates = __import__('fastapi.templating', fromlist=['Jinja2Templates']).Jinja2Templates(directory="app/templates")


@router.get("/search", response_class=HTMLResponse)
async def search_page(request: FastAPIRequest):
    """Search page."""
    return templates.TemplateResponse("search.html", {
        "request": request,
        "title": "Search"
    })


@router.get("/api/search")
async def search_words(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db)
):
    """Search for words in Norwegian or Bulgarian."""
    query_lower = q.lower().strip()
    
    results = {
        "query": q,
        "nouns": [],
        "verbs": [],
        "adjectives": []
    }
    
    # Search nouns
    noun_query = select(Noun).where(
        or_(
            Noun.word.ilike(f"%{query_lower}%"),
            Noun.definite.ilike(f"%{query_lower}%"),
            Noun.plural.ilike(f"%{query_lower}%"),
            Noun.translations.contains(query_lower)  # JSON search
        )
    )
    noun_result = await db.execute(noun_query)
    nouns = noun_result.scalars().all()
    
    for noun in nouns:
        # Check if query matches any translation
        matched = False
        if noun.translations:
            for trans in noun.translations:
                if query_lower in trans.lower():
                    matched = True
                    break
        
        results["nouns"].append({
            "id": noun.id,
            "article": noun.article,
            "word": noun.word,
            "definite": noun.definite,
            "plural": noun.plural,
            "translations": noun.translations,
            "matched_translation": matched
        })
    
    # Search verbs
    verb_query = select(Verb).where(
        or_(
            Verb.infinitive.ilike(f"%{query_lower}%"),
            Verb.presens.ilike(f"%{query_lower}%"),
            Verb.preteritum.ilike(f"%{query_lower}%"),
            Verb.perfect_participle.ilike(f"%{query_lower}%"),
            Verb.translations.contains(query_lower)
        )
    )
    verb_result = await db.execute(verb_query)
    verbs = verb_result.scalars().all()
    
    for verb in verbs:
        matched = False
        if verb.translations:
            for trans in verb.translations:
                if query_lower in trans.lower():
                    matched = True
                    break
        
        results["verbs"].append({
            "id": verb.id,
            "infinitive": verb.infinitive,
            "presens": verb.presens,
            "preteritum": verb.preteritum,
            "perfect_participle": verb.perfect_participle,
            "translations": verb.translations,
            "group": verb.group,
            "group_description": verb.group_description,
            "matched_translation": matched
        })
    
    # Search adjectives
    adj_query = select(Adjective).where(
        or_(
            Adjective.base.ilike(f"%{query_lower}%"),
            Adjective.neuter.ilike(f"%{query_lower}%"),
            Adjective.plural.ilike(f"%{query_lower}%"),
            Adjective.translations.contains(query_lower)
        )
    )
    adj_result = await db.execute(adj_query)
    adjectives = adj_result.scalars().all()
    
    for adj in adjectives:
        matched = False
        if adj.translations:
            for trans in adj.translations:
                if query_lower in trans.lower():
                    matched = True
                    break
        
        results["adjectives"].append({
            "id": adj.id,
            "base": adj.base,
            "neuter": adj.neuter,
            "plural": adj.plural,
            "translations": adj.translations,
            "group": adj.group,
            "group_description": adj.group_description,
            "matched_translation": matched
        })
    
    return results
