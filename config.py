import os
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_NAME = os.environ.get('APP_NAME', 'Roma Lusso Travel')
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Mail Gmail SMTP
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = (
        os.environ.get('MAIL_SENDER_NAME', 'Roma Lusso Travel'),
        os.environ.get('MAIL_USERNAME', '')
    )

    # Amadeus API
    AMADEUS_API_KEY = os.environ.get('AMADEUS_API_KEY')
    AMADEUS_API_SECRET = os.environ.get('AMADEUS_API_SECRET')
    AMADEUS_ENV = os.environ.get('AMADEUS_ENV', 'test')

    # GetYourGuide API
    GETYOURGUIDE_API_KEY = os.environ.get('GETYOURGUIDE_API_KEY')
    GETYOURGUIDE_API_URL = 'https://api.getyourguide.com'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///agency.db'


class ProductionConfig(Config):
    DEBUG = False
    _uri = os.environ.get('DATABASE_URL', '')
    if _uri.startswith('postgres://'):
        _uri = _uri.replace('postgres://', 'postgresql://', 1)
    if _uri and 'sslmode=' not in _uri and 'postgresql' in _uri:
        _sep = '&' if '?' in _uri else '?'
        _uri += f'{_sep}sslmode=require'
    SQLALCHEMY_DATABASE_URI = _uri if _uri else 'sqlite:///agency.db'
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": NullPool,
        "connect_args": {
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        },
    }


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
