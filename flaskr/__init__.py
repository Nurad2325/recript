import os
import sys
import logging
from flask import Flask
from dotenv import load_dotenv
from config import DevelopmentConfig, ProductionConfig
from flaskr.db import init_db
from flaskr.services.startup import load_database

load_dotenv()

def perform_pre_boot_actions(app):
    app.logger.info("Preboot actions...")
    load_database()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    env = os.getenv('ENV', 'development')
    if env == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    if test_config is not None:
        app.config.from_mapping(test_config)

    app.logger.setLevel(logging.INFO if env == 'development' else logging.WARNING)
    app.logger.info('App starting...')

    with app.app_context():
        init_db()
        perform_pre_boot_actions(app)

    from .routes import health
    from .routes.connectors import slack

    app.register_blueprint(health.bp)
    app.register_blueprint(slack.bp)
    app.logger.info('App started...')
    return app
