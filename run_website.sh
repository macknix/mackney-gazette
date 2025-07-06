#!/bin/bash

# Activate the virtual environment
source mackney-gazette-venv/bin/activate

# Install requirements if needed
pip install -r requirements.txt

# Run the Flask application
cd app
export FLASK_APP=app.py
export FLASK_ENV=development
echo "Starting Mackney Gazette website at http://localhost:5000"
flask run --host=0.0.0.0 --port=5000
