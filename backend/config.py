import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'opspilot-secret-key-dev')
    
    # Database configuration with automatic fallback to local SQLite if postgres isn't running
    DB_USER = os.getenv('POSTGRES_USER', 'opspilot')
    DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'opspilot')
    DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    DB_PORT = os.getenv('POSTGRES_PORT', '5432')
    DB_NAME = os.getenv('POSTGRES_DB', 'opspilot')
    
    DEFAULT_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///opspilot.db' if not os.getenv('POSTGRES_HOST') else DEFAULT_DATABASE_URL)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google Gemini API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
