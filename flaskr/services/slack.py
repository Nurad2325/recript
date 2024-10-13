import requests
from flaskr.services.llm_agent import enhance_with_llm_rag, query_pinecone
from flask import current_app

def receive_command(command, public_flag):
    response_url = command["response_url"]
    query = command["text"]
    current_app.logger.info(f"Processing request from {command['user_name']} with trigger id {command['trigger_id']}")
    pinecone_response = query_pinecone(query)
    enhanced_content = enhance_with_llm_rag(query, pinecone_response)
    send_slack_message(response_url=response_url, text=enhanced_content, public = public_flag)
    current_app.logger.info(f"Finished responding to {command['user_name']} with trigger id {command['trigger_id']}")

def send_slack_message(response_url, text, public = False):
    data = {
        'text': text,
        'response_type': 'in_channel' if public else 'ephemeral'  # Public or private message
    }
    requests.post(response_url, json=data)