# Project Information  

# Overview
The Onboarding Assistant agent tackles the challenges of inefficient onboarding by providing new hires with immediate access to critical information through Slack commands. By integrating knowledge sources like Confluence and GitHub, the assistant helps employees quickly locate answers from design documents or code snippets while also identifying gaps in documentation to facilitate a smoother onboarding experience for future hires.

Developed as a Retrieval-Augmented Generation (RAG) agent using the Llama Index, it interfaces with Slack to efficiently address employee queries. Relevant documents and code are uploaded to Pinecone, which serves as a vector datastore. For each query, the agent retrieves results from Pinecone, filters them based on Confluence and GitHub metadata, and curates responses using a Language Model (LLM). The final answer is then sent to the user in Slack.

## Development  
Project is setup to use routes for API routes, and services for business logic. To add a new base route register the route in flaskr/__init__.py like how the health endpoint is registered
### Setup instructions  
  
Start by creating a virtual environment.  
```python3 -m venv .venv```  
Activate the virtual environment.  
For mac:  
```source .venv/bin/activate```  
For windows:  
```.venv/Scripts/Activate```  
Install dependencies:  
```pip install -r requirements.txt```  
Create a local .env file with the following contents in the proj1 directory  
```
FLASK_APP=flaskr:create_app
FLASK_ENV=development
SECRET_KEY=your-secret-key
```
Run server locally for development  
```flask run```  
  
## Prod settings  
On the server the application uses nginx, and gunicorn. Certificate should already be setup.
The following deployment guide was followed: https://github.com/yeshwanthlm/YouTube/blob/main/flask-on-aws-ec2.md  
  
How to update server with latest main:  
* SSH into server
* from project directory run: ./deploy.sh
