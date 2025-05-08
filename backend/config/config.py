import os
from dotenv import load_dotenv

# Loading settings from an .env file
load_dotenv()
print("Loaded DATABASE_URL from .env:", os.getenv('DATABASE_URL'))  # للتأكد من تحميل .env

class Config:
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', True)
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', False)
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    REMEMBER_COOKIE_DURATION = int(os.getenv('REMEMBER_COOKIE_DURATION', 86400))
