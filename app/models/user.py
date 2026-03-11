from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets
import string


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    ROLES = {
        'admin': 'Amministratore',
        'manager': 'Manager',
        'operatore': 'Operatore',
    }

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='operatore', nullable=False)
    attivo = db.Column(db.Boolean, default=True, nullable=False)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_exp = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def generate_password(length=12):
        chars = string.ascii_letters + string.digits + '!@#$%'
        return ''.join(secrets.choice(chars) for _ in range(length))

    def generate_reset_token(self):
        from datetime import timedelta
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_exp = datetime.utcnow() + timedelta(hours=2)
        return self.reset_token

    def is_admin(self):
        return self.role == 'admin'

    def is_manager_or_admin(self):
        return self.role in ('admin', 'manager')

    def role_label(self):
        return self.ROLES.get(self.role, self.role)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'role_label': self.role_label(),
            'attivo': self.attivo,
        }


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
