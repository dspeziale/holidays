import os
from sqlalchemy import create_engine, text, MetaData
from dotenv import load_dotenv

load_dotenv('.env.local')

# Get the database URL
db_url = os.environ.get('DATABASE_URL', '')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

if db_url:
    try:
        engine = create_engine(db_url)

        # Get all table names
        with engine.connect() as conn:
            print('🔄 Getting list of existing tables...')
            result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            tables = [row[0] for row in result.fetchall()]

            if tables:
                print(f'🗑️  Dropping {len(tables)} existing tables...')
                # Disable foreign key checks temporarily
                conn.execute(text('SET CONSTRAINTS ALL DEFERRED'))

                # Drop all tables
                metadata = MetaData()
                metadata.reflect(bind=engine)
                metadata.drop_all(bind=engine)

                print('✅ All tables dropped successfully')
            else:
                print('ℹ️  No tables found to drop')

        print('🎯 Database reset complete. Ready for fresh schema creation.')

    except Exception as e:
        print(f'❌ Error during database reset: {e}')
else:
    print('❌ DATABASE_URL not found in environment')