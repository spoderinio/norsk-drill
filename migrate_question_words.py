"""
Migration: Create question_words table

Run this ONCE to add QuestionWord support.
Your models already have 'level' field, so only creating question_words table.
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from pathlib import Path

# Database path
BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR}/data/norsk_drill.db"


async def migrate():
    """Create question_words table."""
    
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        print("🔄 Creating question_words table...")
        
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS question_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                norwegian VARCHAR(100) NOT NULL UNIQUE,
                translations JSON NOT NULL,
                example TEXT,
                notes TEXT
            )
        """))
        
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_question_words_norwegian ON question_words(norwegian)"))
        
        print("✅ Migration completed!")
    
    await engine.dispose()


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║  Migration: Add QuestionWord Table                        ║
║                                                            ║
║  This creates the question_words table.                    ║
║  Your models already have 'level' field!                   ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    response = input("Continue? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        asyncio.run(migrate())
        print("\n✅ Done! You can now use Question Words!")
    else:
        print("Migration cancelled.")
