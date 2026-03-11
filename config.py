import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_NAME = os.environ.get('APP_NAME', 'Roma Lusso Travel')

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
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://'
    ) if os.environ.get('DATABASE_URL') else 'sqlite:///agency.db'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
