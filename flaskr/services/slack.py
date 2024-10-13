import asyncio
import requests

def receive_command(command):
    response_url = command["response_url"]
    query = command["text"]

    pass

def send_slack_message(response_url, text):
    data = {
        'text': text,
    }
    requests.post(response_url, json=data)