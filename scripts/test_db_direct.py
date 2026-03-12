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
    print("Listing current tables in 'public' schema:")
    result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
    tables = [row[0] for row in result.fetchall()]
    print("Tables:", tables)

    if not tables:
        print("Creating a dummy table to test write access...")
        conn.execute(text("CREATE TABLE test_connection (id serial PRIMARY KEY, name varchar(50))"))
        conn.commit()
        print("Dummy table created.")
        
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        print("Tables after creation:", [row[0] for row in result.fetchall()])
        
        conn.execute(text("DROP TABLE test_connection"))
        conn.commit()
        print("Dummy table dropped.")
