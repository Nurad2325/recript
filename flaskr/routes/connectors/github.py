import os
import requests
from flask import current_app as app
from flask import Blueprint, request, jsonify
from flaskr.services.llm_agent import enhance_with_llm

bp = Blueprint('github', __name__)

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', 'your-default-token-here')

@bp.route('/slack/repo-info', methods=['POST'])
def repo_info():
    app.logger.info("/slack/repo-info called")
    text = request.form.get('text')  # Text after /repo-info command

    if not text:
        return jsonify({'text': '[DJ] Please provide a repository in the format owner/repo.'})

    repo = text.strip()

    # Fetch repo info from GitHub
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    github_url = f'https://api.github.com/repos/{repo}'
    response = requests.get(github_url, headers=headers)

    if response.status_code == 200:
        repo_data = response.json()
        repo_name = repo_data.get('name')
        repo_description = repo_data.get('description')
        repo_url = repo_data.get('html_url')

        # Combine repository information into a single text block
        repo_info_text = f'*Repository:* {repo_name}\n*Description:* {repo_description}\n*URL:* {repo_url}'

        # Enhance the repository information with LLM
        enhanced_content = enhance_with_llm(repo_info_text)

        return jsonify({
            'response_type': 'in_channel',  # Make response visible to all in the channel
            'text': enhanced_content
        })
    else:
        return jsonify({'text': 'Repository not found. Please check the owner/repo format.'})
