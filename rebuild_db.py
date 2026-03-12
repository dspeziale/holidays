import os
from app import create_app, db
from app.utils.seed import seed_admin
from app.models.user import User
from app.models.cliente import Cliente
from app.models.tour import Tour
from app.models.esperienza import Esperienza
from app.models.pacchetto import Pacchetto
from app.models.viaggio import Viaggio
from app.models.fornitore import Fornitore
from dotenv import load_dotenv
from flask_migrate import stamp

load_dotenv('.env.local')

app = create_app('production')

with app.app_context():
    print(f"Using database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Verify models are registered
    tables_to_create = list(db.metadata.tables.keys())
    print(f"Models to create: {tables_to_create}")
    
    print('Creating all tables...')
    # Use direct connection for schema creation to ensure commit in SA 2.0
    with db.engine.connect() as conn:
        db.metadata.create_all(conn)
        conn.commit()
    print('Tables created successfully')
    
    print('Seeding initial data...')
    seed_admin()
    db.session.commit() # Double check seeding commit
    print('Data seeded successfully')
    
    print('Stamping database with latest migration revision...')
    stamp(revision='123456789abc')
    # No manual commit needed for stamp usually but doesn't hurt to check
    print('Database stamped at 123456789abc')

print('Database rebuild and seed complete!')
