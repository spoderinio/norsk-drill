"""Database models - v3.0"""
from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app import settings

Base = declarative_base()

LEVELS = ["A", "B1.1", "B1.2", "B2.1", "B2.2"]
DEFAULT_LEVEL = "A"


class Noun(Base):
    __tablename__ = "nouns"
    id = Column(Integer, primary_key=True, index=True)
    article = Column(String(3), nullable=False)
    word = Column(String(200), nullable=False, index=True)
    translations = Column(JSON, nullable=False)
    definite = Column(String(200), nullable=True)
    plural = Column(String(200), nullable=True)
    tags = Column(String(500), nullable=True)
    group = Column(String(200), nullable=True)
    group_description = Column(String(500), nullable=True)
    level = Column(String(10), nullable=False, default=DEFAULT_LEVEL, server_default="A")


class Verb(Base):
    __tablename__ = "verbs"
    id = Column(Integer, primary_key=True, index=True)
    infinitive = Column(String(200), nullable=False, index=True)
    presens = Column(String(200), nullable=True)
    preteritum = Column(String(200), nullable=True)
    perfect_participle = Column(String(200), nullable=True)
    translations = Column(JSON, nullable=False)
    tags = Column(String(500), nullable=True)
    group = Column(String(200), nullable=True)
    group_description = Column(String(500), nullable=True)
    level = Column(String(10), nullable=False, default=DEFAULT_LEVEL, server_default="A")


class Adjective(Base):
    __tablename__ = "adjectives"
    id = Column(Integer, primary_key=True, index=True)
    base = Column(String(200), nullable=False, index=True)
    neuter = Column(String(200), nullable=True)
    plural = Column(String(200), nullable=True)
    translations = Column(JSON, nullable=False)
    tags = Column(String(500), nullable=True)
    group = Column(String(200), nullable=True)
    group_description = Column(String(500), nullable=True)
    level = Column(String(10), nullable=False, default=DEFAULT_LEVEL, server_default="A")


class Phrase(Base):
    __tablename__ = "phrases"
    id = Column(Integer, primary_key=True, index=True)
    norwegian = Column(String(500), nullable=False, index=True)
    translations = Column(JSON, nullable=False)
    category = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    level = Column(String(10), nullable=False, default=DEFAULT_LEVEL, server_default="A")


class QuestionWord(Base):
    __tablename__ = "question_words"
    id = Column(Integer, primary_key=True, index=True)
    norwegian = Column(String(200), nullable=False, index=True)
    translations = Column(JSON, nullable=False)
    example_no = Column(String(500), nullable=True)
    example_bg = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)

class CustomCategory(Base):
    __tablename__ = "custom_categories"
    id    = Column(Integer, primary_key=True, index=True)
    name  = Column(String(200), nullable=False, unique=True)
    slug  = Column(String(200), nullable=False, unique=True)
    icon  = Column(String(10),  nullable=False, default="📝")
    color = Column(String(20),  nullable=False, default="#4f8ef7")


class CustomEntry(Base):
    __tablename__ = "custom_entries"
    id          = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, nullable=False)
    norwegian   = Column(String(500), nullable=False, index=True)
    translations = Column(JSON, nullable=False)
    level       = Column(String(10), nullable=False, default="A", server_default="A")


engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session_maker() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Migration: add level column to existing tables if missing
        from sqlalchemy import text
        for table in ["nouns", "verbs", "adjectives", "phrases"]:
            try:
                await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN level VARCHAR(10) NOT NULL DEFAULT 'A'"))
            except Exception:
                pass  # Column already exists
        # Migration: add question_words table
        # Already handled by create_all above
