"""
config.py - Configuration settings for Agri Smart Flask application
"""

import os

# Base directory of the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class."""

    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'agri-smart-secret-key-2024-change-in-production'

    # SQLite database URI stored in the instance folder
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:12345678@localhost:5432/agrismart_db'

    # Disable modification tracking to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload folder for product images and AI uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

    # Allowed file extensions for image uploads
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}

    # Maximum upload file size (16 MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # ML Models folder
    ML_MODELS_FOLDER = os.path.join(BASE_DIR, 'ml_models')

    # Weather API Key (used by Crop Recommendation weather autofill)
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY') or '467653f2056f444f9d803744261406'
    WEATHER_API_URL = 'https://api.weatherapi.com/v1/current.json'
