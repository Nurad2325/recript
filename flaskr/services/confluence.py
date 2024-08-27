import os
import requests
from flaskr.common.html_helpers import clean_html

def fetch_confluence_page_content(page_id):
    CONFLUENCE_BASE_URL = os.getenv('CONFLUENCE_BASE_URL', '<ERROR>')
    CONFLUENCE_USERNAME = os.getenv('CONFLUENCE_USERNAME', '<ERROR>')
    CONFLUENCE_API_TOKEN = os.getenv('CONFLUENCE_API_TOKEN', '<ERROR>')
    # TODO: Move configs to db at some point
    url = f'{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}?expand=body.storage'
    response = requests.get(url, auth=(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN))
    
    if response.status_code == 200:
        page = response.json()
        title = page['title']
        content = page['body']['storage']['value']

        # Optionally format content to remove HTML tags or limit length
        content = clean_html(content)
        content = content[:3000]  # Slack message limit

        return f"*{title}*\n{content}"
    else:
        return f"Error fetching page: {response.status_code}"