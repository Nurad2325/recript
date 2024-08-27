import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    LOG_TO_STDOUT = os.getenv('LOG_TO_STDOUT')

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    LOG_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.log')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
