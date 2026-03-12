import os
from sqlalchemy import create_engine, text, MetaData
from dotenv import load_dotenv

load_dotenv('.env.local')
db_url = os.environ.get('DATABASE_URL', '')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

print(f"Checking database at: {db_url}")
if db_url:
    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            # Check schemas
            res = conn.execute(text("SELECT schema_name FROM information_schema.schemata"))
            schemas = [r[0] for r in res.fetchall()]
            print("Accessible schemas:", schemas)

            # Check tables in public
            result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            tables = [row[0] for row in result.fetchall()]
            print("Tables in 'public':", tables)
            
            # Check tables via reflection
            metadata = MetaData()
            metadata.reflect(bind=engine)
            print("Reflected tables:", list(metadata.tables.keys()))
            
            if 'users' in tables or 'users' in metadata.tables:
                result = conn.execute(text("SELECT count(*) FROM users"))
                print("User count:", result.scalar())
            else:
                print("Table 'users' NOT FOUND.")
                
    except Exception as e:
        print(f"Error during check: {e}")
else:
    print("DATABASE_URL not found")

# Check for local dbs just in case
print("\nChecking for local SQLite databases:")
for f in os.listdir('.'):
    if f.endswith('.db'):
        print(f"- Found: {f}")
if os.path.exists('instance'):
    for f in os.listdir('instance'):
        if f.endswith('.db'):
            print(f"- Found in instance/: {f}")
