"""CRUD operations for database models."""
import random
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import Noun, Verb, Adjective, Phrase, GrammarLesson


# ========== NOUNS ==========

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


async def update_noun(db: AsyncSession, noun_id: int, **kwargs) -> Optional[Noun]:
    """Update a noun. Returns None if not found."""
    noun = await get_noun(db, noun_id)
    if not noun:
        return None
    
    # Update fields if provided
    if 'article' in kwargs:
        noun.article = kwargs['article']
    if 'word' in kwargs:
        noun.word = kwargs['word']
    if 'definite' in kwargs:
        noun.definite = kwargs['definite']
    if 'plural' in kwargs:
        noun.plural = kwargs['plural']
    if 'translations' in kwargs:
        noun.translations = kwargs['translations']
    if 'tags' in kwargs:
        noun.tags = kwargs['tags']
    if 'level' in kwargs:
        noun.level = kwargs['level']
    
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


# ========== VERBS ==========

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


async def update_verb(db: AsyncSession, verb_id: int, **kwargs) -> Optional[Verb]:
    """Update a verb. Returns None if not found."""
    verb = await get_verb(db, verb_id)
    if not verb:
        return None
    
    # Update fields if provided
    if 'infinitive' in kwargs:
        verb.infinitive = kwargs['infinitive']
    if 'presens' in kwargs:
        verb.presens = kwargs['presens']
    if 'preteritum' in kwargs:
        verb.preteritum = kwargs['preteritum']
    if 'perfect_participle' in kwargs:
        verb.perfect_participle = kwargs['perfect_participle']
    if 'translations' in kwargs:
        verb.translations = kwargs['translations']
    if 'group' in kwargs:
        verb.group = kwargs['group']
    if 'group_description' in kwargs:
        verb.group_description = kwargs['group_description']
    if 'tags' in kwargs:
        verb.tags = kwargs['tags']
    if 'level' in kwargs:
        verb.level = kwargs['level']
    
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


# ========== ADJECTIVES ==========

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


async def update_adjective(db: AsyncSession, adj_id: int, **kwargs) -> Optional[Adjective]:
    """Update an adjective. Returns None if not found."""
    adj = await get_adjective(db, adj_id)
    if not adj:
        return None
    
    # Update fields if provided
    if 'base' in kwargs:
        adj.base = kwargs['base']
    if 'neuter' in kwargs:
        adj.neuter = kwargs['neuter']
    if 'plural' in kwargs:
        adj.plural = kwargs['plural']
    if 'comparative' in kwargs:
        adj.comparative = kwargs['comparative']
    if 'superlative' in kwargs:
        adj.superlative = kwargs['superlative']
    if 'translations' in kwargs:
        adj.translations = kwargs['translations']
    if 'group' in kwargs:
        adj.group = kwargs['group']
    if 'group_description' in kwargs:
        adj.group_description = kwargs['group_description']
    if 'tags' in kwargs:
        adj.tags = kwargs['tags']
    if 'level' in kwargs:
        adj.level = kwargs['level']
    
    await db.commit()
    await db.refresh(adj)
    return adj


async def delete_adjective(db: AsyncSession, adj_id: int) -> bool:
    """Delete an adjective."""
    adjective = await get_adjective(db, adj_id)
    if adjective:
        await db.delete(adjective)
        await db.commit()
        return True
    return False


# ========== PHRASES ==========

async def get_phrase(db: AsyncSession, phrase_id: int) -> Optional[Phrase]:
    """Get a phrase by ID."""
    result = await db.execute(select(Phrase).where(Phrase.id == phrase_id))
    return result.scalar_one_or_none()


async def get_all_phrases(db: AsyncSession, category: Optional[str] = None) -> List[Phrase]:
    """Get all phrases, optionally filtered by category."""
    query = select(Phrase)
    if category:
        query = query.where(Phrase.category == category)
    result = await db.execute(query)
    return result.scalars().all()


async def get_random_phrase(
    db: AsyncSession,
    exclude_ids: List[int] = None,
    category: Optional[str] = None
) -> Optional[Phrase]:
    """Get a random phrase, excluding specified IDs."""
    query = select(Phrase)
    
    if category:
        query = query.where(Phrase.category == category)
    
    if exclude_ids:
        query = query.where(~Phrase.id.in_(exclude_ids))
    
    result = await db.execute(query)
    phrases = result.scalars().all()
    
    return random.choice(phrases) if phrases else None


async def find_phrase_by_norwegian(db: AsyncSession, norwegian: str) -> Optional[Phrase]:
    """Find a phrase by Norwegian text."""
    result = await db.execute(
        select(Phrase).where(Phrase.norwegian == norwegian)
    )
    return result.scalar_one_or_none()


async def create_phrase(db: AsyncSession, norwegian: str, translations: List[str], **kwargs) -> Optional[Phrase]:
    """Create a new phrase. Returns None if duplicate exists."""
    # Check for duplicate
    existing = await find_phrase_by_norwegian(db, norwegian)
    if existing:
        return None  # Duplicate - skip
    
    phrase = Phrase(
        norwegian=norwegian,
        translations=translations,
        category=kwargs.get('category'),
        notes=kwargs.get('notes'),
        tags=kwargs.get('tags'),
        level=kwargs.get('level')
    )
    db.add(phrase)
    await db.commit()
    await db.refresh(phrase)
    return phrase


async def update_phrase(db: AsyncSession, phrase_id: int, **kwargs) -> Optional[Phrase]:
    """Update a phrase. Returns None if not found."""
    phrase = await get_phrase(db, phrase_id)
    if not phrase:
        return None
    
    # Update fields if provided
    if 'norwegian' in kwargs:
        phrase.norwegian = kwargs['norwegian']
    if 'translations' in kwargs:
        phrase.translations = kwargs['translations']
    if 'category' in kwargs:
        phrase.category = kwargs['category']
    if 'notes' in kwargs:
        phrase.notes = kwargs['notes']
    if 'tags' in kwargs:
        phrase.tags = kwargs['tags']
    if 'level' in kwargs:
        phrase.level = kwargs['level']
    
    await db.commit()
    await db.refresh(phrase)
    return phrase


async def delete_phrase(db: AsyncSession, phrase_id: int) -> bool:
    """Delete a phrase."""
    phrase = await get_phrase(db, phrase_id)
    if phrase:
        await db.delete(phrase)
        await db.commit()
        return True
    return False


# ========== GRAMMAR LESSONS ==========

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
