import os
from dotenv import load_dotenv

load_dotenv()  
class Config:
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True') == 'True'
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    REMEMBER_COOKIE_DURATION = int(os.getenv('REMEMBER_COOKIE_DURATION', 86400))
    TOKEN_EXPIRATION_DAYS = int(os.getenv('TOKEN_EXPIRATION_DAYS', 1))

# mahmoud elqalini
# mahmoud ramadan
# habiba abdelmalik