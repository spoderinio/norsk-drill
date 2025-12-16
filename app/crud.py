"""CRUD operations for database models."""
import random
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import Noun, Verb, Adjective, GrammarLesson


# Nouns
async def get_noun(db: AsyncSession, noun_id: int) -> Optional[Noun]:
    """Get a noun by ID."""
    result = await db.execute(select(Noun).where(Noun.id == noun_id))
    return result.scalar_one_or_none()


async def get_all_nouns(db: AsyncSession, tag: Optional[str] = None) -> List[Noun]:
    """Get all nouns, optionally filtered by tag."""
    query = select(Noun)
    if tag:
        query = query.where(Noun.tags.contains(tag))
    result = await db.execute(query)
    return result.scalars().all()


async def get_random_noun(
    db: AsyncSession, 
    exclude_ids: List[int] = None, 
    tag: Optional[str] = None
) -> Optional[Noun]:
    """Get a random noun, excluding specified IDs."""
    query = select(Noun)
    
    if tag:
        query = query.where(Noun.tags.contains(tag))
    
    if exclude_ids:
        query = query.where(~Noun.id.in_(exclude_ids))
    
    result = await db.execute(query)
    nouns = result.scalars().all()
    
    return random.choice(nouns) if nouns else None


async def find_noun_by_word(db: AsyncSession, article: str, word: str) -> Optional[Noun]:
    """Find a noun by article and word."""
    result = await db.execute(
        select(Noun).where(
            Noun.article == article,
            Noun.word == word
        )
    )
    return result.scalar_one_or_none()


async def create_noun(db: AsyncSession, article: str, word: str, translations: List[str], **kwargs) -> Optional[Noun]:
    """Create a new noun. Returns None if duplicate exists."""
    # Check for duplicate
    existing = await find_noun_by_word(db, article, word)
    if existing:
        return None  # Duplicate - skip
    
    noun = Noun(
        article=article,
        word=word,
        translations=translations,
        definite=kwargs.get('definite'),
        plural=kwargs.get('plural'),
        tags=kwargs.get('tags'),
        level=kwargs.get('level')
    )
    db.add(noun)
    await db.commit()
    await db.refresh(noun)
    return noun


async def delete_noun(db: AsyncSession, noun_id: int) -> bool:
    """Delete a noun."""
    noun = await get_noun(db, noun_id)
    if noun:
        await db.delete(noun)
        await db.commit()
        return True
    return False


# Verbs
async def get_verb(db: AsyncSession, verb_id: int) -> Optional[Verb]:
    """Get a verb by ID."""
    result = await db.execute(select(Verb).where(Verb.id == verb_id))
    return result.scalar_one_or_none()


async def get_all_verbs(db: AsyncSession, tag: Optional[str] = None) -> List[Verb]:
    """Get all verbs, optionally filtered by tag."""
    query = select(Verb)
    if tag:
        query = query.where(Verb.tags.contains(tag))
    result = await db.execute(query)
    return result.scalars().all()


async def get_random_verb(
    db: AsyncSession,
    exclude_ids: List[int] = None,
    tag: Optional[str] = None
) -> Optional[Verb]:
    """Get a random verb, excluding specified IDs."""
    query = select(Verb)
    
    if tag:
        query = query.where(Verb.tags.contains(tag))
    
    if exclude_ids:
        query = query.where(~Verb.id.in_(exclude_ids))
    
    result = await db.execute(query)
    verbs = result.scalars().all()
    
    return random.choice(verbs) if verbs else None


async def find_verb_by_infinitive(db: AsyncSession, infinitive: str) -> Optional[Verb]:
    """Find a verb by infinitive form."""
    result = await db.execute(
        select(Verb).where(Verb.infinitive == infinitive)
    )
    return result.scalar_one_or_none()


async def create_verb(db: AsyncSession, infinitive: str, translations: List[str], **kwargs) -> Optional[Verb]:
    """Create a new verb. Returns None if duplicate exists."""
    # Check for duplicate
    existing = await find_verb_by_infinitive(db, infinitive)
    if existing:
        return None  # Duplicate - skip
    
    verb = Verb(
        infinitive=infinitive,
        presens=kwargs.get('presens'),
        preteritum=kwargs.get('preteritum'),
        perfect_participle=kwargs.get('perfect_participle'),
        translations=translations,
        group=kwargs.get('group'),
        group_description=kwargs.get('group_description'),
        tags=kwargs.get('tags'),
        level=kwargs.get('level')
    )
    db.add(verb)
    await db.commit()
    await db.refresh(verb)
    return verb


async def delete_verb(db: AsyncSession, verb_id: int) -> bool:
    """Delete a verb."""
    verb = await get_verb(db, verb_id)
    if verb:
        await db.delete(verb)
        await db.commit()
        return True
    return False


# Adjectives
async def get_adjective(db: AsyncSession, adj_id: int) -> Optional[Adjective]:
    """Get an adjective by ID."""
    result = await db.execute(select(Adjective).where(Adjective.id == adj_id))
    return result.scalar_one_or_none()


async def get_all_adjectives(db: AsyncSession, tag: Optional[str] = None) -> List[Adjective]:
    """Get all adjectives, optionally filtered by tag."""
    query = select(Adjective)
    if tag:
        query = query.where(Adjective.tags.contains(tag))
    result = await db.execute(query)
    return result.scalars().all()


async def get_random_adjective(
    db: AsyncSession,
    exclude_ids: List[int] = None,
    tag: Optional[str] = None
) -> Optional[Adjective]:
    """Get a random adjective, excluding specified IDs."""
    query = select(Adjective)
    
    if tag:
        query = query.where(Adjective.tags.contains(tag))
    
    if exclude_ids:
        query = query.where(~Adjective.id.in_(exclude_ids))
    
    result = await db.execute(query)
    adjectives = result.scalars().all()
    
    return random.choice(adjectives) if adjectives else None


async def find_adjective_by_base(db: AsyncSession, base: str) -> Optional[Adjective]:
    """Find an adjective by base form."""
    result = await db.execute(
        select(Adjective).where(Adjective.base == base)
    )
    return result.scalar_one_or_none()


async def create_adjective(db: AsyncSession, base: str, translations: List[str], **kwargs) -> Optional[Adjective]:
    """Create a new adjective. Returns None if duplicate exists."""
    # Check for duplicate
    existing = await find_adjective_by_base(db, base)
    if existing:
        return None  # Duplicate - skip
    
    adjective = Adjective(
        base=base,
        neuter=kwargs.get('neuter'),
        plural=kwargs.get('plural'),
        comparative=kwargs.get('comparative'),
        superlative=kwargs.get('superlative'),
        translations=translations,
        group=kwargs.get('group'),
        group_description=kwargs.get('group_description'),
        tags=kwargs.get('tags'),
        level=kwargs.get('level')
    )
    db.add(adjective)
    await db.commit()
    await db.refresh(adjective)
    return adjective


async def delete_adjective(db: AsyncSession, adj_id: int) -> bool:
    """Delete an adjective."""
    adjective = await get_adjective(db, adj_id)
    if adjective:
        await db.delete(adjective)
        await db.commit()
        return True
    return False


# Grammar Lessons
async def get_grammar_lessons(db: AsyncSession, tag: Optional[str] = None) -> List[GrammarLesson]:
    """Get all grammar lessons."""
    query = select(GrammarLesson)
    if tag:
        query = query.where(GrammarLesson.tags.contains(tag))
    result = await db.execute(query)
    return result.scalars().all()


async def create_grammar_lesson(db: AsyncSession, title: str, content: str, **kwargs) -> GrammarLesson:
    """Create a new grammar lesson."""
    lesson = GrammarLesson(
        title=title,
        content=content,
        tags=kwargs.get('tags'),
        level=kwargs.get('level')
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    return lesson