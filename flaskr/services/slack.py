import requests

def send_slack_message(response_url, text):
    data = {
        'text': text,
    }
    requests.post(response_url, json=data)