"""Database models - v4.0"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from datetime import datetime
import app.settings as settings

DEFAULT_LEVEL = "A"
LEVELS = ["A", "B1.1", "B1.2", "B2.1", "B2.2"]


class Base(DeclarativeBase):
    pass


class Noun(Base):
    __tablename__ = "nouns"
    id          = Column(Integer, primary_key=True, index=True)
    article     = Column(String(10), nullable=False)
    word        = Column(String(200), nullable=False, index=True)
    translations = Column(JSON, nullable=False)
    definite    = Column(String(200), nullable=True)
    plural      = Column(String(200), nullable=True)
    example_no  = Column(String(500), nullable=True)
    example_bg  = Column(String(500), nullable=True)
    notes       = Column(Text, nullable=True)
    tags        = Column(String(500), nullable=True)
    group       = Column(String(200), nullable=True)
    group_description = Column(String(500), nullable=True)
    level       = Column(String(10), nullable=False, default=DEFAULT_LEVEL, server_default="A")


class Verb(Base):
    __tablename__ = "verbs"
    id          = Column(Integer, primary_key=True, index=True)
    infinitive  = Column(String(200), nullable=False, index=True)
    presens     = Column(String(200), nullable=True)
    preteritum  = Column(String(200), nullable=True)
    perfect_participle = Column(String(200), nullable=True)
    translations = Column(JSON, nullable=False)
    tags        = Column(String(500), nullable=True)
    group       = Column(String(200), nullable=True)
    group_description = Column(String(500), nullable=True)
    level       = Column(String(10), nullable=False, default=DEFAULT_LEVEL, server_default="A")


class Adjective(Base):
    __tablename__ = "adjectives"
    id          = Column(Integer, primary_key=True, index=True)
    base        = Column(String(200), nullable=False, index=True)
    neuter      = Column(String(200), nullable=True)
    plural      = Column(String(200), nullable=True)
    translations = Column(JSON, nullable=False)
    tags        = Column(String(500), nullable=True)
    group       = Column(String(200), nullable=True)
    group_description = Column(String(500), nullable=True)
    level       = Column(String(10), nullable=False, default=DEFAULT_LEVEL, server_default="A")


class Phrase(Base):
    __tablename__ = "phrases"
    id          = Column(Integer, primary_key=True, index=True)
    norwegian   = Column(String(500), nullable=False, index=True)
    translations = Column(JSON, nullable=False)
    category    = Column(String(200), nullable=True)
    notes       = Column(Text, nullable=True)
    level       = Column(String(10), nullable=False, default=DEFAULT_LEVEL, server_default="A")


class QuestionWord(Base):
    __tablename__ = "question_words"
    id          = Column(Integer, primary_key=True, index=True)
    norwegian   = Column(String(200), nullable=False, index=True)
    translations = Column(JSON, nullable=False)
    example_no  = Column(String(500), nullable=True)
    example_bg  = Column(String(500), nullable=True)
    notes       = Column(Text, nullable=True)


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


import json
engine = create_async_engine(settings.DATABASE_URL, echo=False, json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False))
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session_maker() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Migrations: add columns to existing tables if missing
        from sqlalchemy import text
        migrations = [
            # level column
            ("nouns",       "ALTER TABLE nouns ADD COLUMN level VARCHAR(10) NOT NULL DEFAULT 'A'"),
            ("verbs",       "ALTER TABLE verbs ADD COLUMN level VARCHAR(10) NOT NULL DEFAULT 'A'"),
            ("adjectives",  "ALTER TABLE adjectives ADD COLUMN level VARCHAR(10) NOT NULL DEFAULT 'A'"),
            ("phrases",     "ALTER TABLE phrases ADD COLUMN level VARCHAR(10) NOT NULL DEFAULT 'A'"),
            # group columns
            ("nouns",       "ALTER TABLE nouns ADD COLUMN group_description VARCHAR(500)"),
            ("verbs",       "ALTER TABLE verbs ADD COLUMN group_description VARCHAR(500)"),
            ("adjectives",  "ALTER TABLE adjectives ADD COLUMN group_description VARCHAR(500)"),
            # example columns on nouns
            ("nouns",       "ALTER TABLE nouns ADD COLUMN example_no VARCHAR(500)"),
            ("nouns",       "ALTER TABLE nouns ADD COLUMN example_bg VARCHAR(500)"),
        ]
        for _table, stmt in migrations:
            try:
                await conn.execute(text(stmt))
            except Exception:
                pass  # column already exists — safe to ignore
