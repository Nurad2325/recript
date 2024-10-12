from flask import Blueprint, current_app

bp = Blueprint('health', __name__)

@bp.route('/health')
def health_check():
    current_app.logger.info('Health checkpoint is reachable!') 
    return "Server is running!"
