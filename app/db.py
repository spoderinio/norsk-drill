"""Database models."""
from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app import settings

Base = declarative_base()


class Noun(Base):
    """Norwegian noun model."""
    __tablename__ = "nouns"

    id = Column(Integer, primary_key=True, index=True)
    article = Column(String(3), nullable=False)  # en/ei/et
    word = Column(String(200), nullable=False, index=True)
    translations = Column(JSON, nullable=False)  # List of translation strings
    definite = Column(String(200), nullable=True)
    plural = Column(String(200), nullable=True)
    tags = Column(String(500), nullable=True)
    level = Column(String(10), nullable=True)  # A1, A2, B1, etc.


class Verb(Base):
    """Norwegian verb model."""
    __tablename__ = "verbs"

    id = Column(Integer, primary_key=True, index=True)
    infinitive = Column(String(200), nullable=False, index=True)
    presens = Column(String(200), nullable=True)
    preteritum = Column(String(200), nullable=True)
    perfect_participle = Column(String(200), nullable=True)
    translations = Column(JSON, nullable=False)
    group = Column(String(100), nullable=True)  # NEW: "1", "2а", "2б", "3", "4", "неправилни"
    group_description = Column(Text, nullable=True)  # NEW: Grammar explanation
    tags = Column(String(500), nullable=True)
    level = Column(String(10), nullable=True)


class Adjective(Base):
    """Norwegian adjective model."""
    __tablename__ = "adjectives"

    id = Column(Integer, primary_key=True, index=True)
    base = Column(String(200), nullable=False, index=True)
    neuter = Column(String(200), nullable=True)
    plural = Column(String(200), nullable=True)
    comparative = Column(String(200), nullable=True)
    superlative = Column(String(200), nullable=True)
    translations = Column(JSON, nullable=False)
    group = Column(String(100), nullable=True)  # NEW: "Група 1", "Група 2", etc.
    group_description = Column(Text, nullable=True)  # NEW: Grammar explanation
    tags = Column(String(500), nullable=True)
    level = Column(String(10), nullable=True)


class Phrase(Base):
    """Norwegian phrase/expression model."""
    __tablename__ = "phrases"

    id = Column(Integer, primary_key=True, index=True)
    norwegian = Column(String(500), nullable=False, index=True)  # The phrase in Norwegian
    translations = Column(JSON, nullable=False)  # List of Bulgarian translations
    category = Column(String(100), nullable=True)  # "time", "weather", "greetings", etc.
    notes = Column(Text, nullable=True)  # Additional notes/context
    tags = Column(String(500), nullable=True)
    level = Column(String(10), nullable=True)


class GrammarLesson(Base):
    """Grammar lesson model."""
    __tablename__ = "grammar_lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(String(500), nullable=True)
    level = Column(String(10), nullable=True)


# Database engine and session
engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """Get database session."""
    async with async_session_maker() as session:
        yield session


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
