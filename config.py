# config.py
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

# Basic configurations
SECRET_KEY = 'your-secret-key-here-change-in-production'
DEBUG = True

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017/athlete_platform"

# File upload configuration
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size

# Session configuration
PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

# Languages supported
LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'ta': 'Tamil',
    'te': 'Telugu',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'bn': 'Bengali',
    'mr': 'Marathi'
}