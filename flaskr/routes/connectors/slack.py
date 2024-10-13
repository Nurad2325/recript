from flask import current_app as app
from flask_executor import Executor
from flask import Blueprint, request, jsonify
from flaskr.services.slack import receive_command, send_slack_message
from flaskr.services.llm_agent import enhance_with_llm_rag, query_pinecone

bp = Blueprint('slack', __name__)

@bp.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.form
    app.logger.info(f'Request payload {data}')
    return jsonify({
            "response_type": "ephemeral",
            "text": "Processing your request..."
        }), 200 
    
    