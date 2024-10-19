# Script for running Flask in debug mode
CD Application

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
. .\venv\Scripts\Activate

# Set environment variables
#$env:FLASK_ENV="development"
#set FLASK_ENV=development
#set FLASK_APP=app

# Run the Flask application
flask --debug run