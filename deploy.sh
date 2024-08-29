#!/bin/bash

# Navigate to the project directory
cd /home/ubuntu/proj1

# Pull the latest changes
git pull origin main

# Activate virtual environment
source /home/ubuntu/proj1/venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Deactivate virtual environment
deactivate

# Restart Gunicorn
sudo systemctl restart app.service

# Check the status
sudo systemctl status app.service

echo "Deployment completed."