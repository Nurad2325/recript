from flask import current_app as app
from flaskr.executor import executor
from flask import Blueprint, request, jsonify
from flaskr.services.slack import receive_command

bp = Blueprint('slack', __name__)

@bp.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.form
    app.logger.info(f'Request payload {data}')
    executor.submit(receive_command, data)
    return jsonify({
            "response_type": "ephemeral",
            "text": "Thinking..."
        }), 200 
    
    