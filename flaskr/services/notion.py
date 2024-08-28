import os
import requests
from flaskr.common.html_helpers import clean_html

def fetch_notion_page_content(page_id):
    NOTION_TOKEN = os.getenv('NOTION_TOKEN', '<ERROR>')
    NOTION_VERSION = os.getenv('NOTION_VERSION', '2022-06-28')
    
    url = f'https://api.notion.com/v1/pages/{page_id}'
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Notion-Version': NOTION_VERSION,
    }
    
    response = requests.get(url, headers=headers)
    response_json = response.json()
    # Log or print the raw response for debugging
    print(response_json)

    if response.status_code == 200:
        page = response.json()
        # Extract page title and content as needed
        title = page.get('properties', {}).get('title', {}).get('title', [{}])[0].get('text', {}).get('content', 'No Title')
        content = "Content from the page or specific properties"  # Customize this as needed

        # Optionally format content to remove HTML tags or limit length
        content = clean_html(content)
        content = content[:3000]  # Slack message limit

        return f"*{title}*\n{content}"
    else:
        return f"Error fetching page: {response.status_code}"
