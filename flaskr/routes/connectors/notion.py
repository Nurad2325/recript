from flask import current_app as app
from flask import Blueprint, request, jsonify
from flaskr.services.notion import fetch_notion_page_content
from flaskr.services.slack import send_slack_message
from flaskr.services.llm_agent import enhance_with_llm

bp = Blueprint('notion', __name__)

@bp.route('/slack/notion_events', methods=['POST'])
def slack_events():
    if request.content_type == 'application/x-www-form-urlencoded':
        data = request.form
    else:
        data = request.json

    # Handle URL verification challenge
    if 'challenge' in data:
        return jsonify({'challenge': data['challenge']})

    # Handle slash commands
    if 'command' in data:
        command = data['command']
        if command == '/read-notion':
            page_id = data.get('text', '59b0d589d4eb4fdaa4177d50b7e6e855')  # Default page ID or extract from command text
            page_content = fetch_notion_page_content(page_id)
            enhanced_content = enhance_with_llm(page_content)
            send_slack_message(data['response_url'], enhanced_content)
    
    # Handle message events
    if 'event' in data:
        event = data['event']
        if event['type'] == 'message' and 'read notion' in event['text'].lower():
            channel = event['channel']
            # Extract page ID from message or hardcode for demo
            page_id = '59b0d589d4eb4fdaa4177d50b7e6e855'  # Replace with your actual page ID
            page_content = fetch_notion_page_content(page_id)
            enhanced_content = enhance_with_llm(page_content)
            send_slack_message(channel, enhanced_content)

    return jsonify({'status': 'ok'})
