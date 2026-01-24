import sys
import os

# Add the root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set environment variables
os.environ.setdefault('HOST', '0.0.0.0')
os.environ.setdefault('PORT', '8000')

# Import Flask app
from server import app

# Vercel serverless function handler
def handler(request):
    """
    Vercel serverless function handler
    """
    return app(request.environ, lambda status, headers: None)
