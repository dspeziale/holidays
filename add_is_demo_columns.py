import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('.env.local')

# Get the database URL
db_url = os.environ.get('DATABASE_URL', '')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

if db_url:
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # Add the is_demo column to missing tables
            tables = ['tours', 'viaggi', 'pacchetti']
            for table in tables:
                print(f"🔄 Processing table: {table}...")
                conn.execute(text(f'ALTER TABLE {table} ADD COLUMN IF NOT EXISTS is_demo BOOLEAN DEFAULT FALSE NOT NULL'))
                conn.commit()
                print(f'✅ Column is_demo added to {table}')

            # Verify the column exists in all tables
            for table in tables:
                result = conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' AND column_name = 'is_demo'"))
                if result.fetchone():
                    print(f'✅ Column is_demo verified in {table}')
                else:
                    print(f'❌ Column is_demo not found in {table} after addition')

    except Exception as e:
        print(f'❌ Error: {e}')
else:
    print('❌ DATABASE_URL not found in environment')
