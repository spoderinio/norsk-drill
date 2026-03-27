"""
Run this on the Pi to add custom categories tables:
  cd ~/Projects/norsk-drill
  source venv/bin/activate
  python3 migrate_custom_categories.py
"""
import sqlite3, os

db_path = os.path.expanduser("~/Projects/norsk-drill/data/norsk_drill.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS custom_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL UNIQUE,
    slug VARCHAR(200) NOT NULL UNIQUE,
    icon VARCHAR(10) NOT NULL DEFAULT '📝',
    color VARCHAR(20) NOT NULL DEFAULT '#4f8ef7'
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS custom_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES custom_categories(id) ON DELETE CASCADE,
    norwegian VARCHAR(500) NOT NULL,
    translations JSON NOT NULL,
    level VARCHAR(10) NOT NULL DEFAULT 'A'
)
""")

conn.commit()
conn.close()
print("Done — custom_categories and custom_entries tables created.")
