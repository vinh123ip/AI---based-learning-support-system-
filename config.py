import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # OpenAI API Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///cs466_database.db')
    
    # JWT Secret Key
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    
    # Application Settings
    APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
    APP_PORT = int(os.getenv('APP_PORT', '8000'))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Upload Settings
    MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', '10485760'))  # 10MB
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'py,pl,txt,zip,pdf,docx').split(','))
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    
    # Code Execution Settings
    CODE_TIMEOUT = int(os.getenv('CODE_TIMEOUT', '5'))  # seconds
    MAX_CODE_LENGTH = int(os.getenv('MAX_CODE_LENGTH', '10000'))  # characters
    
    # Email Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'True').lower() == 'true'
    
    # Security Settings
    BCRYPT_ROUNDS = int(os.getenv('BCRYPT_ROUNDS', '12'))
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '3600'))  # seconds
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
    LOCKOUT_DURATION = int(os.getenv('LOCKOUT_DURATION', '900'))  # seconds
    
    # AI Settings
    AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
    AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', '1500'))
    AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', '0.7'))
    AI_TIMEOUT = int(os.getenv('AI_TIMEOUT', '30'))  # seconds
    
    # File Storage
    STATIC_FOLDER = os.getenv('STATIC_FOLDER', 'static')
    TEMPLATE_FOLDER = os.getenv('TEMPLATE_FOLDER', 'templates')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/cs466.log')
    LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', '1000'))
    
    # Database settings
    DATABASE_ECHO = DEBUG  # Echo SQL queries in debug mode
    
    @staticmethod
    def init_app(app):
        """Initialize app with config"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DATABASE_ECHO = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DATABASE_ECHO = False
    LOG_LEVEL = 'WARNING'
    
    # Override some security settings for production
    ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Shorter token expiry
    BCRYPT_ROUNDS = 14  # More secure hashing
    
    @staticmethod
    def init_app(app):
        """Production-specific initialization"""
        # Log to syslog in production
        import logging
        from logging.handlers import SysLogHandler
        
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'  # In-memory database for tests
    WTF_CSRF_ENABLED = False
    CODE_TIMEOUT = 1  # Faster timeout for tests

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    return config[os.getenv('FLASK_ENV', 'default')] 