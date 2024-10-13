import requests
from flaskr.services.llm_agent import enhance_with_llm_rag, query_pinecone
from flask import current_app

def receive_command(command):
    response_url = command["response_url"]
    query = command["text"]
    current_app.logger.info(f"Processing request from {command['user_name']} with trigger id {command['trigger_id']}")
    pinecone_response = query_pinecone(query)
    enhanced_content = enhance_with_llm_rag(query, pinecone_response)
    send_slack_message(response_url=response_url, text=enhanced_content)
    current_app.logger.info(f"Finished responding to {command['user_name']} with trigger id {command['trigger_id']}")

def send_slack_message(response_url, text):
    data = {
        'text': text,
    }
    requests.post(response_url, json=data)