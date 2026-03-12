import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('.env.local')
db_url = os.environ.get('DATABASE_URL', '')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

if db_url:
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            tables = ['clienti', 'tours', 'esperienze', 'fornitori', 'viaggi', 'pacchetti']
            for table in tables:
                res = conn.execute(text(f"SELECT COUNT(*) FROM {table} WHERE is_demo = TRUE")).scalar()
                total = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"Table {table}: {res}/{total} records are demo.")
            
            print("\nVerification complete.")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No DATABASE_URL found.")
