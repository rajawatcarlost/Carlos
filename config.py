import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'carlos-promoter-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///carlos_promoter.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # App settings
    APP_NAME = 'Carlos Promoter'
    APP_VERSION = '1.0.0'
    
    # Telegram settings
    TELEGRAM_SESSION_DIR = 'telegram_sessions'
    CONFIG_FILE = 'config.json'
    
    # Upload folder
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
