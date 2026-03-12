import os
from sqlalchemy import create_engine, text, MetaData
from dotenv import load_dotenv
from app import create_app, db
# Import all models to populate metadata
from app.models.user import User
from app.models.cliente import Cliente
from app.models.tour import Tour
from app.models.esperienza import Esperienza
from app.models.pacchetto import Pacchetto
from app.models.viaggio import Viaggio
from app.models.fornitore import Fornitore
from app.utils.seed import seed_admin
from flask_migrate import stamp

load_dotenv('.env.local')
db_url = os.environ.get('DATABASE_URL', '')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

print(f"Targeting: {db_url}")
engine = create_engine(db_url)

# 1. Create Tables
print("Step 1: Creating tables...")
db.metadata.create_all(engine)
with engine.connect() as conn:
    conn.commit()
    res = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
    print("Tables after create_all:", [r[0] for r in res.fetchall()])

# 2. Seed Data
print("Step 2: Scoping Flask app for seeding...")
app = create_app('production')
with app.app_context():
    # Use the same engine for the session
    print("Seeding admin and demo data...")
    seed_admin()
    db.session.commit()
    print("Seeding complete.")
    
    # 3. Stamp
    print("Step 3: Stamping revision...")
    stamp(revision='123456789abc')
    print("Stamped at 123456789abc")

print("All steps completed successfully!")
