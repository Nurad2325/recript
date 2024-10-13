from flask import current_app as app
from flaskr.executor import executor
from flask import Blueprint, request, jsonify
from flaskr.services.slack import receive_command

bp = Blueprint('slack', __name__)

@bp.route('/slack/event/me', methods=['POST'])
def slack_events_me():
    data = request.form
    app.logger.info(f'Request payload {data}')
    executor.submit(receive_command, data, False)
    return jsonify({
            "response_type": "ephemeral",
            "text": "Thinking..."
        }), 200 

@bp.route('/slack/event/us', methods=['POST'])
def slack_events_us():
    data = request.form
    app.logger.info(f'Request payload {data}')
    executor.submit(receive_command, data, True)
    return jsonify({
            "response_type": "ephemeral",
            "text": "Thinking..."
        }), 200 
    