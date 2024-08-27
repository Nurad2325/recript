import os
import sys
import logging
from flask import Flask
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from config import DevelopmentConfig, ProductionConfig

load_dotenv()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    env = os.getenv('ENV', 'development')
    if env == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    if test_config is not None:
        app.config.from_mapping(test_config)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    stream_handler.setLevel(logging.DEBUG if env == 'development' else logging.WARNING)
    app.logger.addHandler(stream_handler)

    app.logger.setLevel(logging.DEBUG if env == 'development' else logging.WARNING)
    app.logger.info('App starting...')

    from .routes import health
    from .routes.connectors import github
    from .routes.connectors import confluence

    app.register_blueprint(health.bp)
    app.register_blueprint(github.bp)
    app.register_blueprint(confluence.bp)
    app.logger.info('App started...')
    return app
