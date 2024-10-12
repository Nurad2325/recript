import os
import base64
from github import Auth, GithubIntegration
from flask import current_app

# Authentication setup for GitHub
def get_github_integration():
    GITHUB_APP_ID = os.getenv('GITHUB_APP_ID', '<ERROR>')
    GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID', '<ERROR>')
    GITHUB_PRIVATE_KEY_LOCATION = os.getenv('GITHUB_PRIVATE_KEY_LOCATION', '<ERROR>')

    try:
        with open(GITHUB_PRIVATE_KEY_LOCATION, 'rb') as pem_file:
            GITHUB_PRIVATE_KEY = pem_file.read()
        auth = Auth.AppAuth(GITHUB_CLIENT_ID, GITHUB_PRIVATE_KEY.decode("utf-8"))
        gi = GithubIntegration(auth=auth)
        return gi
    except Exception as e:
        current_app.logger.error(f"Error setting up GitHub integration: {e}")
        return None

# Fetch content from a specific file in a GitHub repository
def fetch_github_repo_file(repo_name, file_path):
    try:
        gi = get_github_integration()
        if gi is None:
            return "Error in GitHub integration"

        for installation in gi.get_installations():
            g = installation.get_github_for_installation()
            repo = g.get_repo(repo_name)

        file_content = repo.get_contents(file_path)
        decoded_content = base64.b64decode(file_content.raw_data["content"])
        return decoded_content

    except Exception as e:
        current_app.logger.error(f"Error fetching file from GitHub repo: {e}")
        return f"Error fetching file: {e}"

# Fetch all files from a GitHub repository recursively
def get_all_github_repo_files(repo_name):
    result = []
    try:
        gi = get_github_integration()
        if gi is None:
            return "Error in GitHub integration"
        
        for installation in gi.get_installations():
            g = installation.get_github_for_installation()
            repo = g.get_repo(repo_name)
        
        contents = repo.get_contents("")
        
        while contents:
            file_content = contents.pop(0)
            # Check if the file or directory is in the 'frontend' folder, and skip it if so
            if file_content.path.startswith("frontend/"):
                #current_app.logger.info(f"Skipping frontend folder: {file_content.path}")
                continue  # Skip this iteration if the file is in the frontend folder

            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                decoded_content = base64.b64decode(file_content.raw_data["content"])
                result.append(f"*{file_content.path}*\n{decoded_content}")

        current_app.logger.info(f"Downloaded {len(result)} files from GitHub repo {repo_name}")

    except Exception as e:
        current_app.logger.error(f"Error loading GitHub repo files: {e}")
        return f"Error loading files: {e}"

    return result
