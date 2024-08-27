from flask import current_app as app
from flask import Blueprint, request, jsonify
from flaskr.services.confluence import fetch_confluence_page_content
from flaskr.services.slack import send_slack_message

bp = Blueprint('confluence', __name__)

@bp.route('/slack/events', methods=['POST'])
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
        if command == '/read-wiki':
            page_id = data.get('text', '98307')  # Default page ID or extract from command text
            page_content = fetch_confluence_page_content(page_id)
            send_slack_message(data['response_url'], page_content)
    
    # Handle message events
    if 'event' in data:
        event = data['event']
        if event['type'] == 'message' and 'read wiki' in event['text'].lower():
            channel = event['channel']
            # Extract page ID from message or hardcode for demo
            page_id = '98307'  # Replace with your actual page ID
            page_content = fetch_confluence_page_content(page_id)
            send_slack_message(channel, page_content)

    return jsonify({'status': 'ok'})