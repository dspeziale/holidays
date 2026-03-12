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
            # Add the is_demo column
            conn.execute(text('ALTER TABLE clienti ADD COLUMN IF NOT EXISTS is_demo BOOLEAN DEFAULT FALSE NOT NULL'))
            print('✅ Column is_demo added successfully to clienti table')

            # Verify the column exists
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'clienti' AND column_name = 'is_demo'"))
            if result.fetchone():
                print('✅ Column is_demo verified in database')
            else:
                print('❌ Column is_demo not found after addition')

    except Exception as e:
        print(f'❌ Error: {e}')
else:
    print('❌ DATABASE_URL not found in environment')