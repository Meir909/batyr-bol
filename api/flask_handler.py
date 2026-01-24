import sys
import os
import json

# Add the root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set environment variables
os.environ.setdefault('HOST', '0.0.0.0')
os.environ.setdefault('PORT', '8000')

# Import Flask app
from server import app

def handler(request):
    """
    Vercel serverless function handler for Flask app
    """
    try:
        # Convert Vercel request to WSGI format
        method = request.method
        path = request.path or '/'
        query_string = request.query or ''
        headers = dict(request.headers)
        
        # Build WSGI environ
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'QUERY_STRING': query_string,
            'SERVER_NAME': 'vercel.app',
            'SERVER_PORT': '443',
            'wsgi.version': (1, 0),
            'wsgi.input': request.body or '',
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'wsgi.url_scheme': 'https',
        }
        
        # Add headers
        for key, value in headers.items():
            key = key.upper().replace('-', '_')
            if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                key = f'HTTP_{key}'
            environ[key] = value
        
        # Capture response
        response_data = {}
        
        def start_response(status, response_headers):
            response_data['status'] = status
            response_data['headers'] = dict(response_headers)
        
        # Get Flask response
        response_iter = app(environ, start_response)
        response_body = b''.join(response_iter)
        
        # Convert to Vercel format
        status_code = int(response_data['status'].split()[0])
        
        return {
            'statusCode': status_code,
            'headers': response_data['headers'],
            'body': response_body.decode('utf-8')
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error</h1><p>{str(e)}</p>'
        }
