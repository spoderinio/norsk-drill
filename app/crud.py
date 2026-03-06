"""CRUD operations - v3.0"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from app.db import Noun, Verb, Adjective, Phrase, QuestionWord
from typing import Optional


# ── LEVELS ──────────────────────────────────────────────────────────────────

LEVELS = ["A", "B1.1", "B1.2", "B2.1", "B2.2"]


def _normalize(s: str) -> str:
    import re
    return re.sub(r"\s*\(.*?\)\s*", "", s or "").strip().lower()


# ── NOUNS ────────────────────────────────────────────────────────────────────

async def get_nouns(db: AsyncSession, level: Optional[str] = None):
    q = select(Noun)
    if level and level != "all":
        q = q.where(Noun.level == level)
    result = await db.execute(q.order_by(Noun.word))
    return result.scalars().all()


async def get_noun(db: AsyncSession, noun_id: int):
    result = await db.execute(select(Noun).where(Noun.id == noun_id))
    return result.scalar_one_or_none()


async def get_random_noun(db: AsyncSession, exclude_ids: list, level: Optional[str] = None):
    from sqlalchemy import func
    q = select(Noun).where(Noun.id.notin_(exclude_ids))
    if level and level != "all":
        q = q.where(Noun.level == level)
    result = await db.execute(q.order_by(func.random()).limit(1))
    return result.scalar_one_or_none()


async def create_noun(db: AsyncSession, article: str, word: str, translations: list,
                      definite: str = None, plural: str = None, tags: str = None,
                      group: str = None, group_description: str = None, level: str = "A"):
    existing = await db.execute(select(Noun).where(Noun.word == word, Noun.article == article))
    if existing.scalar_one_or_none():
        return None
    noun = Noun(article=article, word=word, translations=translations,
                definite=definite, plural=plural, tags=tags,
                group=group, group_description=group_description, level=level or "A")
    db.add(noun)
    await db.commit()
    await db.refresh(noun)
    return noun


async def update_noun(db: AsyncSession, noun_id: int, **kwargs):
    noun = await get_noun(db, noun_id)
    if not noun:
        return None
    for k, v in kwargs.items():
        if hasattr(noun, k):
            setattr(noun, k, v)
    await db.commit()
    await db.refresh(noun)
    return noun


async def delete_noun(db: AsyncSession, noun_id: int):
    noun = await get_noun(db, noun_id)
    if noun:
        await db.delete(noun)
        await db.commit()
    return noun


async def check_noun_answer(noun: Noun, answer: str) -> bool:
    if not answer or not answer.strip():
        return False
    answer = _normalize(answer)
    for t in noun.translations:
        for part in t.split(","):
            if _normalize(part) == answer:
                return True
    return False


async def count_nouns(db: AsyncSession, level: Optional[str] = None):
    q = select(func.count(Noun.id))
    if level and level != "all":
        q = q.where(Noun.level == level)
    result = await db.execute(q)
    return result.scalar()


# ── VERBS ────────────────────────────────────────────────────────────────────

async def get_verbs(db: AsyncSession, level: Optional[str] = None):
    q = select(Verb)
    if level and level != "all":
        q = q.where(Verb.level == level)
    result = await db.execute(q.order_by(Verb.infinitive))
    return result.scalars().all()


async def get_verb(db: AsyncSession, verb_id: int):
    result = await db.execute(select(Verb).where(Verb.id == verb_id))
    return result.scalar_one_or_none()


async def get_random_verb(db: AsyncSession, exclude_ids: list, level: Optional[str] = None):
    q = select(Verb).where(Verb.id.notin_(exclude_ids))
    if level and level != "all":
        q = q.where(Verb.level == level)
    result = await db.execute(q.order_by(func.random()).limit(1))
    return result.scalar_one_or_none()


async def create_verb(db: AsyncSession, infinitive: str, presens: str = None,
                      preteritum: str = None, perfect_participle: str = None,
                      translations: list = None, tags: str = None,
                      group: str = None, group_description: str = None, level: str = "A"):
    existing = await db.execute(select(Verb).where(Verb.infinitive == infinitive))
    if existing.scalar_one_or_none():
        return None
    verb = Verb(infinitive=infinitive, presens=presens, preteritum=preteritum,
                perfect_participle=perfect_participle, translations=translations or [],
                tags=tags, group=group, group_description=group_description, level=level or "A")
    db.add(verb)
    await db.commit()
    await db.refresh(verb)
    return verb


async def update_verb(db: AsyncSession, verb_id: int, **kwargs):
    verb = await get_verb(db, verb_id)
    if not verb:
        return None
    for k, v in kwargs.items():
        if hasattr(verb, k):
            setattr(verb, k, v)
    await db.commit()
    await db.refresh(verb)
    return verb


async def delete_verb(db: AsyncSession, verb_id: int):
    verb = await get_verb(db, verb_id)
    if verb:
        await db.delete(verb)
        await db.commit()
    return verb


async def check_verb_answer(verb: Verb, presens_ans: str, preteritum_ans: str, perfect_ans: str) -> dict:
    def chk(expected, given):
        if not expected:
            return True
        if not given or not given.strip():
            return False
        return _normalize(given) == _normalize(expected)
    return {
        "presens": chk(verb.presens, presens_ans),
        "preteritum": chk(verb.preteritum, preteritum_ans),
        "perfect": chk(verb.perfect_participle, perfect_ans),
    }


async def count_verbs(db: AsyncSession, level: Optional[str] = None):
    q = select(func.count(Verb.id))
    if level and level != "all":
        q = q.where(Verb.level == level)
    result = await db.execute(q)
    return result.scalar()


# ── ADJECTIVES ───────────────────────────────────────────────────────────────

async def get_adjectives(db: AsyncSession, level: Optional[str] = None):
    q = select(Adjective)
    if level and level != "all":
        q = q.where(Adjective.level == level)
    result = await db.execute(q.order_by(Adjective.base))
    return result.scalars().all()


async def get_adjective(db: AsyncSession, adj_id: int):
    result = await db.execute(select(Adjective).where(Adjective.id == adj_id))
    return result.scalar_one_or_none()


async def get_random_adjective(db: AsyncSession, exclude_ids: list, level: Optional[str] = None):
    q = select(Adjective).where(Adjective.id.notin_(exclude_ids))
    if level and level != "all":
        q = q.where(Adjective.level == level)
    result = await db.execute(q.order_by(func.random()).limit(1))
    return result.scalar_one_or_none()


async def create_adjective(db: AsyncSession, base: str, neuter: str = None, plural: str = None,
                           translations: list = None, tags: str = None,
                           group: str = None, group_description: str = None, level: str = "A"):
    existing = await db.execute(select(Adjective).where(Adjective.base == base))
    if existing.scalar_one_or_none():
        return None
    adj = Adjective(base=base, neuter=neuter, plural=plural, translations=translations or [],
                    tags=tags, group=group, group_description=group_description, level=level or "A")
    db.add(adj)
    await db.commit()
    await db.refresh(adj)
    return adj


async def update_adjective(db: AsyncSession, adj_id: int, **kwargs):
    adj = await get_adjective(db, adj_id)
    if not adj:
        return None
    for k, v in kwargs.items():
        if hasattr(adj, k):
            setattr(adj, k, v)
    await db.commit()
    await db.refresh(adj)
    return adj


async def delete_adjective(db: AsyncSession, adj_id: int):
    adj = await get_adjective(db, adj_id)
    if adj:
        await db.delete(adj)
        await db.commit()
    return adj


async def check_adjective_answer(adj: Adjective, neuter_ans: str, plural_ans: str, translation_ans: str) -> dict:
    def chk(expected, given):
        if not expected:
            return True
        if not given or not given.strip():
            return False
        return _normalize(given) == _normalize(expected)
    def chk_translation(given):
        if not given or not given.strip():
            return False
        given_n = _normalize(given)
        for t in (adj.translations or []):
            for part in t.split(","):
                if _normalize(part) == given_n:
                    return True
        return False
    return {
        "neuter": chk(adj.neuter, neuter_ans),
        "plural": chk(adj.plural, plural_ans),
        "translation": chk_translation(translation_ans),
    }


async def count_adjectives(db: AsyncSession, level: Optional[str] = None):
    q = select(func.count(Adjective.id))
    if level and level != "all":
        q = q.where(Adjective.level == level)
    result = await db.execute(q)
    return result.scalar()


# ── PHRASES ──────────────────────────────────────────────────────────────────

async def get_phrases(db: AsyncSession, level: Optional[str] = None):
    q = select(Phrase)
    if level and level != "all":
        q = q.where(Phrase.level == level)
    result = await db.execute(q.order_by(Phrase.norwegian))
    return result.scalars().all()


async def get_phrase(db: AsyncSession, phrase_id: int):
    result = await db.execute(select(Phrase).where(Phrase.id == phrase_id))
    return result.scalar_one_or_none()


async def get_random_phrase(db: AsyncSession, exclude_ids: list, level: Optional[str] = None):
    q = select(Phrase).where(Phrase.id.notin_(exclude_ids))
    if level and level != "all":
        q = q.where(Phrase.level == level)
    result = await db.execute(q.order_by(func.random()).limit(1))
    return result.scalar_one_or_none()


async def create_phrase(db: AsyncSession, norwegian: str, translations: list,
                        category: str = None, notes: str = None, level: str = "A"):
    existing = await db.execute(select(Phrase).where(Phrase.norwegian == norwegian))
    if existing.scalar_one_or_none():
        return None
    phrase = Phrase(norwegian=norwegian, translations=translations,
                    category=category, notes=notes, level=level or "A")
    db.add(phrase)
    await db.commit()
    await db.refresh(phrase)
    return phrase


async def update_phrase(db: AsyncSession, phrase_id: int, **kwargs):
    phrase = await get_phrase(db, phrase_id)
    if not phrase:
        return None
    for k, v in kwargs.items():
        if hasattr(phrase, k):
            setattr(phrase, k, v)
    await db.commit()
    await db.refresh(phrase)
    return phrase


async def delete_phrase(db: AsyncSession, phrase_id: int):
    phrase = await get_phrase(db, phrase_id)
    if phrase:
        await db.delete(phrase)
        await db.commit()
    return phrase


async def check_phrase_answer(phrase: Phrase, answer: str) -> bool:
    if not answer or not answer.strip():
        return False
    answer = _normalize(answer)
    for t in phrase.translations:
        for part in t.split(","):
            if _normalize(part) == answer:
                return True
    return False


async def count_phrases(db: AsyncSession, level: Optional[str] = None):
    q = select(func.count(Phrase.id))
    if level and level != "all":
        q = q.where(Phrase.level == level)
    result = await db.execute(q)
    return result.scalar()


# ── QUESTION WORDS ───────────────────────────────────────────────────────────

async def get_question_words(db: AsyncSession):
    result = await db.execute(select(QuestionWord).order_by(QuestionWord.norwegian))
    return result.scalars().all()


async def get_question_word(db: AsyncSession, qw_id: int):
    result = await db.execute(select(QuestionWord).where(QuestionWord.id == qw_id))
    return result.scalar_one_or_none()


async def get_random_question_word(db: AsyncSession, exclude_ids: list):
    q = select(QuestionWord).where(QuestionWord.id.notin_(exclude_ids))
    result = await db.execute(q.order_by(func.random()).limit(1))
    return result.scalar_one_or_none()


async def create_question_word(db: AsyncSession, norwegian: str, translations: list,
                               example_no: str = None, example_bg: str = None, notes: str = None):
    existing = await db.execute(select(QuestionWord).where(QuestionWord.norwegian == norwegian))
    if existing.scalar_one_or_none():
        return None
    qw = QuestionWord(norwegian=norwegian, translations=translations,
                      example_no=example_no, example_bg=example_bg, notes=notes)
    db.add(qw)
    await db.commit()
    await db.refresh(qw)
    return qw


async def update_question_word(db: AsyncSession, qw_id: int, **kwargs):
    qw = await get_question_word(db, qw_id)
    if not qw:
        return None
    for k, v in kwargs.items():
        if hasattr(qw, k):
            setattr(qw, k, v)
    await db.commit()
    await db.refresh(qw)
    return qw


async def delete_question_word(db: AsyncSession, qw_id: int):
    qw = await get_question_word(db, qw_id)
    if qw:
        await db.delete(qw)
        await db.commit()
    return qw


async def check_question_word_answer(qw: QuestionWord, answer: str) -> bool:
    if not answer or not answer.strip():
        return False
    answer = _normalize(answer)
    for t in qw.translations:
        for part in t.split(","):
            if _normalize(part) == answer:
                return True
    return False


async def count_question_words(db: AsyncSession):
    result = await db.execute(select(func.count(QuestionWord.id)))
    return result.scalar()


# ── SEARCH ───────────────────────────────────────────────────────────────────

async def search_all(db: AsyncSession, query: str):
    q = f"%{query}%"
    results = []

    nouns = await db.execute(select(Noun).where(
        or_(Noun.word.ilike(q), Noun.translations.cast(String).ilike(q))
    ).limit(20))
    for n in nouns.scalars():
        results.append({"type": "noun", "norwegian": f"{n.article} {n.word}",
                         "translations": n.translations, "level": n.level, "id": n.id})

    verbs = await db.execute(select(Verb).where(
        or_(Verb.infinitive.ilike(q), Verb.translations.cast(String).ilike(q))
    ).limit(20))
    for v in verbs.scalars():
        results.append({"type": "verb", "norwegian": v.infinitive,
                         "translations": v.translations, "level": v.level, "id": v.id})

    adjs = await db.execute(select(Adjective).where(
        or_(Adjective.base.ilike(q), Adjective.translations.cast(String).ilike(q))
    ).limit(20))
    for a in adjs.scalars():
        results.append({"type": "adjective", "norwegian": a.base,
                         "translations": a.translations, "level": a.level, "id": a.id})

    phrases = await db.execute(select(Phrase).where(
        or_(Phrase.norwegian.ilike(q), Phrase.translations.cast(String).ilike(q))
    ).limit(20))
    for p in phrases.scalars():
        results.append({"type": "phrase", "norwegian": p.norwegian,
                         "translations": p.translations, "level": p.level, "id": p.id})

    qwords = await db.execute(select(QuestionWord).where(
        or_(QuestionWord.norwegian.ilike(q), QuestionWord.translations.cast(String).ilike(q))
    ).limit(10))
    for qw in qwords.scalars():
        results.append({"type": "question_word", "norwegian": qw.norwegian,
                         "translations": qw.translations, "level": "—", "id": qw.id})

    return results


from sqlalchemy import String
