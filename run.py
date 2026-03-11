from app import create_app, db
from app.utils.seed import seed_admin

app = create_app('development')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_admin()
    app.run(debug=True, port=5400)
