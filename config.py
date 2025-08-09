# config.py - Configuration settings
import os

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DATABASE = 'ai_consultant.db'
    
    # Stripe Configuration
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_your_stripe_key')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_your_stripe_key')
    
    # Email Configuration
    SMTP_SERVER = os.environ.get('SMTP_SERVER', "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', "your-email@gmail.com")
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', "your-app-password")
    
    # File paths
    REPORTS_DIR = 'reports'
    TEMPLATES_DIR = 'templates'
    SAAS_TOOLS_FILE = 'saas_tools_database.json'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
