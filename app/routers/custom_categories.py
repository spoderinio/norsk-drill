"""app/routers/custom_categories.py  —  add to main.py: app.include_router(custom_categories.router)"""
import json, re
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, text
from app.db import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

LEVELS = ["A", "B1.1", "B1.2", "B2.1", "B2.2"]

# ── helpers ──────────────────────────────────────────────────────────────────

def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

def _parse_translations(raw: str) -> list:
    return [t.strip() for t in raw.replace(";", ",").split(",") if t.strip()]

def _normalize(s: str) -> str:
    return s.lower().rstrip(".!?,;:")

async def _get_cat(db: AsyncSession, slug: str):
    from app.db import CustomCategory
    result = await db.execute(select(CustomCategory).where(CustomCategory.slug == slug))
    return result.scalar_one_or_none()

async def _all_cats(db: AsyncSession):
    from app.db import CustomCategory
    result = await db.execute(select(CustomCategory).order_by(CustomCategory.name))
    return result.scalars().all()

async def _get_levels(db: AsyncSession):
    return LEVELS

# ── Admin: list categories ────────────────────────────────────────────────────

@router.get("/admin/custom-categories", response_class=HTMLResponse)
async def admin_custom_categories(request: Request, db: AsyncSession = Depends(get_db)):
    from app.db import CustomCategory, CustomEntry
    cats = await _all_cats(db)
    counts = {}
    for cat in cats:
        r = await db.execute(select(func.count()).where(
            text(f"category_id = {cat.id}")).select_from(text("custom_entries")))
        counts[cat.id] = r.scalar() or 0
    return templates.TemplateResponse("admin/custom_categories.html", {
        "request": request, "categories": cats, "counts": counts
    })

# ── Admin: create category ────────────────────────────────────────────────────

@router.post("/admin/custom-categories/create")
async def create_custom_category(
    request: Request, db: AsyncSession = Depends(get_db),
    name: str = Form(...), icon: str = Form("📝"), color: str = Form("#4f8ef7")
):
    from app.db import CustomCategory
    slug = _slugify(name)
    try:
        cat = CustomCategory(name=name.strip(), slug=slug, icon=icon.strip(), color=color.strip())
        db.add(cat)
        await db.commit()
    except Exception:
        await db.rollback()
    return RedirectResponse("/admin/custom-categories", status_code=303)

# ── Admin: delete category ────────────────────────────────────────────────────

@router.post("/admin/custom-categories/delete/{cat_id}")
async def delete_custom_category(cat_id: int, db: AsyncSession = Depends(get_db)):
    from app.db import CustomCategory, CustomEntry
    await db.execute(delete(CustomEntry).where(CustomEntry.category_id == cat_id))
    from sqlalchemy import delete as sa_delete
    await db.execute(sa_delete(CustomCategory).where(CustomCategory.id == cat_id))
    await db.commit()
    return RedirectResponse("/admin/custom-categories", status_code=303)

# ── Admin: manage entries in a category ──────────────────────────────────────

@router.get("/admin/custom-categories/{slug}", response_class=HTMLResponse)
async def admin_custom_entries(request: Request, slug: str, db: AsyncSession = Depends(get_db),
                                added: int = 0, skipped: int = 0):
    from app.db import CustomEntry
    cat = await _get_cat(db, slug)
    if not cat:
        return RedirectResponse("/admin/custom-categories", status_code=303)
    result = await db.execute(
        select(CustomEntry).where(CustomEntry.category_id == cat.id).order_by(CustomEntry.id.desc()))
    entries = result.scalars().all()
    return templates.TemplateResponse("admin/custom_entries.html", {
        "request": request, "cat": cat, "entries": entries,
        "levels": LEVELS, "added": added, "skipped": skipped
    })

# ── Admin: add single entry ───────────────────────────────────────────────────

@router.post("/admin/custom-categories/{slug}/add")
async def add_custom_entry(slug: str, db: AsyncSession = Depends(get_db),
                            norwegian: str = Form(...), translations: str = Form(...),
                            level: str = Form("A")):
    from app.db import CustomEntry
    cat = await _get_cat(db, slug)
    if not cat:
        return RedirectResponse("/admin/custom-categories", status_code=303)
    trans = _parse_translations(translations)
    if norwegian.strip() and trans:
        # duplicate check
        existing = await db.execute(
            select(CustomEntry).where(
                CustomEntry.category_id == cat.id,
                CustomEntry.norwegian == norwegian.strip()))
        if not existing.scalar_one_or_none():
            db.add(CustomEntry(category_id=cat.id, norwegian=norwegian.strip(),
                               translations=trans, level=level or "A"))
            await db.commit()
    return RedirectResponse(f"/admin/custom-categories/{slug}", status_code=303)

# ── Admin: import text ────────────────────────────────────────────────────────

@router.post("/admin/custom-categories/{slug}/import-text")
async def import_custom_text(slug: str, db: AsyncSession = Depends(get_db),
                              text_data: str = Form(...), level: str = Form("A")):
    from app.db import CustomEntry
    cat = await _get_cat(db, slug)
    if not cat:
        return RedirectResponse("/admin/custom-categories", status_code=303)
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
        existing = await db.execute(
            select(CustomEntry).where(
                CustomEntry.category_id == cat.id,
                CustomEntry.norwegian == norwegian))
        if existing.scalar_one_or_none():
            skipped += 1
            continue
        db.add(CustomEntry(category_id=cat.id, norwegian=norwegian,
                           translations=_parse_translations(translation), level=level or "A"))
        added += 1
    await db.commit()
    return RedirectResponse(f"/admin/custom-categories/{slug}?added={added}&skipped={skipped}", status_code=303)

# ── Admin: delete entry ───────────────────────────────────────────────────────

@router.post("/admin/custom-categories/{slug}/delete/{entry_id}")
async def delete_custom_entry(slug: str, entry_id: int, db: AsyncSession = Depends(get_db)):
    from app.db import CustomEntry
    from sqlalchemy import delete as sa_delete
    await db.execute(sa_delete(CustomEntry).where(CustomEntry.id == entry_id))
    await db.commit()
    return RedirectResponse(f"/admin/custom-categories/{slug}", status_code=303)

# ── Practice: page ────────────────────────────────────────────────────────────

@router.get("/practice/custom/{slug}", response_class=HTMLResponse)
async def practice_custom(request: Request, slug: str, db: AsyncSession = Depends(get_db),
                           level: str = "all"):
    from app.db import CustomEntry
    cat = await _get_cat(db, slug)
    if not cat:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("practice/custom.html", {
        "request": request, "cat": cat, "levels": LEVELS, "selected_level": level
    })

# ── Practice: next ────────────────────────────────────────────────────────────

@router.post("/practice/custom/{slug}/next")
async def next_custom_entry(slug: str, request: Request, db: AsyncSession = Depends(get_db)):
    from app.db import CustomEntry
    cat = await _get_cat(db, slug)
    if not cat:
        return JSONResponse({"done": True})
    data = await request.json()
    seen = data.get("seen_ids", [])
    level = data.get("level", "all")

    q = select(CustomEntry).where(CustomEntry.category_id == cat.id)
    if level and level != "all":
        q = q.where(CustomEntry.level == level)
    if seen:
        q = q.where(CustomEntry.id.notin_(seen))
    from sqlalchemy import func as sqlfunc
    q = q.order_by(sqlfunc.random()).limit(1)
    result = await db.execute(q)
    entry = result.scalar_one_or_none()
    if not entry:
        return JSONResponse({"done": True})
    return JSONResponse({
        "id": entry.id,
        "norwegian": entry.norwegian,
        "translations": entry.translations,
        "level": entry.level,
    })

# ── Practice: check ───────────────────────────────────────────────────────────

@router.post("/practice/custom/{slug}/check")
async def check_custom_entry(slug: str, request: Request, db: AsyncSession = Depends(get_db)):
    from app.db import CustomEntry
    data = await request.json()
    entry_id = data.get("id")
    answer = data.get("answer", "")
    reverse = data.get("reverse", False)

    result = await db.execute(select(CustomEntry).where(CustomEntry.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        return JSONResponse({"correct": False})

    ua = _normalize(answer)
    if reverse:
        correct = ua == _normalize(entry.norwegian)
    else:
        correct = any(ua == _normalize(t) for part in entry.translations for t in part.split(","))

    return JSONResponse({
        "correct": correct,
        "norwegian": entry.norwegian,
        "translations": entry.translations,
    })
