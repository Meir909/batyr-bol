import sys
import os

# Add the root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import the Flask app
from server import app

# Vercel serverless function handler
def handler(environ, start_response):
    return app(environ, start_response)
