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
            # Tag all existing data as demo (since we just reset and seeded with demo data)
            tables = ['clienti', 'tours', 'esperienze', 'fornitori', 'viaggi', 'pacchetti']
            for table in tables:
                print(f"Tagging records in {table} as demo...")
                conn.execute(text(f'UPDATE {table} SET is_demo = TRUE'))
                conn.commit()
            print("Successfully tagged all existing records as demo.")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No DATABASE_URL found.")
