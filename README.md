# Project Information  
## Setup instructions  
  
Start by creating a virtual environment.  
```python3 -m venv .venv```  
Activate the virtual environment.  
```source .venv/bin/activate```  
Install dependencies.  
```pip install -r requirements.txt```  
Create a local .env file with the following contents in the proj1 directory  
```
FLASK_APP=flaskr:create_app
FLASK_ENV=development
SECRET_KEY=your-secret-key
```
Run server locally for development  
```flask run```  
  
## Development  
Project is setup to use routes for API routes, and services for business logic. To add a new base route register the route in flaskr/__init__.py like how the health endpoint is registered