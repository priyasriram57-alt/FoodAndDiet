import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///food_recommendation.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Model paths
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/food_recommender.h5')
    SCALER_PATH = os.getenv('SCALER_PATH', 'models/scaler.pkl')
    ENCODER_PATH = os.getenv('ENCODER_PATH', 'models/label_encoders.pkl')
    
    # Application settings
    APP_NAME = os.getenv('APP_NAME', 'FoodAI')
    MAX_RECOMMENDATIONS = int(os.getenv('MAX_RECOMMENDATIONS', 20))
    MEAL_PLAN_DAYS = int(os.getenv('MEAL_PLAN_DAYS', 7))
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Session settings
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # Cache settings
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_food_recommendation.db'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    # Use PostgreSQL in production
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])