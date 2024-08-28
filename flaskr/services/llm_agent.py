import os
import requests

def enhance_with_llm(text):
    """
    Enhances the provided text using the OpenAI GPT-3.5 API.
    """
    # Retrieve the OpenAI API key from environment variables
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '<ERROR>')

    llm_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": f"Rephrase the following content into a brief answer of 5 lines: {text}"}
        ],
        "max_tokens": 150,
    }

    response = requests.post(llm_url, headers=headers, json=data)

    if response.status_code == 200:
        enhanced_text = response.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        return enhanced_text
    else:
        return f"Error enhancing content: {response.status_code}"

def test_openai_api():
    """
    Tests the OpenAI API connection and prints a response.
    """
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '<ERROR>')
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello to the world"}
        ],
        "max_tokens": 50,
    }
    
    response = requests.post(url, headers=headers, json=data)

    
