import os
import requests
from flaskr.common.html_helpers import clean_html
from flask import current_app

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
        content = clean_html(content)
        return f"*{title}*\n{content}"
    else:
        return f"Error fetching page: {response.status_code}"
    
def get_all_confluence_pages():
    result = []
    try: 
        CONFLUENCE_BASE_URL = os.getenv('CONFLUENCE_BASE_URL', '<ERROR>')
        CONFLUENCE_USERNAME = os.getenv('CONFLUENCE_USERNAME', '<ERROR>')
        CONFLUENCE_API_TOKEN = os.getenv('CONFLUENCE_API_TOKEN', '<ERROR>')
        get_all_pages_url = f'{CONFLUENCE_BASE_URL}/rest/api/content?type=page&start=0&limit=99999'
        all_pages_response = requests.get(get_all_pages_url, auth=(CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN))
        if all_pages_response.status_code != 200:
            current_app.logger.error('Error loading all confluence pages!') 
        all_pages = all_pages_response.json()['results']
        for page in all_pages:
            page_id = page['id']
            page_content = fetch_confluence_page_content(page_id)
            result.append(page_content)
        current_app.logger.info(f'Downloaded: {len(result)} pages from confluence')
    except Exception as error:
        current_app.logger.error(f'Error loading confluence data: {error}') 
    return result