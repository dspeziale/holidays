import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('.env.local')
db_url = os.environ.get('DATABASE_URL', '')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

print(f"Connecting to: {db_url}")
engine = create_engine(db_url)

with engine.connect() as conn:
    # Diagnostic info
    res = conn.execute(text("SELECT current_database(), current_schema(), current_user"))
    db, schema, user = res.fetchone()
    print(f"DB: {db}, Schema: {schema}, User: {user}")
    
    # Create and commit
    print("Creating persistence_test table...")
    conn.execute(text("CREATE TABLE IF NOT EXISTS persistence_test (id serial PRIMARY KEY, val text)"))
    # In SQLAlchemy 2.0, connection is in a transaction by default. Need to commit.
    conn.commit()
    print("Committed.")
    
    # Verify
    res = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
    print("Tables in public schema after commit:", [row[0] for row in res.fetchall()])

with engine.connect() as conn2:
    # Check in a NEW connection
    res = conn2.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
    print("Tables in public schema in NEW connection:", [row[0] for row in res.fetchall()])
    
    # Cleanup
    conn2.execute(text("DROP TABLE persistence_test"))
    conn2.commit()
    print("Cleanup done.")
