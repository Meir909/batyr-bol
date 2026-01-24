import sys
import os

# Add the root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Simple Flask app for testing
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>BATYR BOL</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        .logo { font-size: 48px; margin-bottom: 20px; }
        .button { background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 10px; display: inline-block; }
    </style>
</head>
<body>
    <div class="logo">🇰🇿 BATYR BOL</div>
    <h1>Интерактивная образовательная платформа</h1>
    <p>Изучайте казахскую историю и язык с помощью игровых механик!</p>
    <a href="/game" class="button">🎮 Начать игру</a>
    <a href="/api/test" class="button">🧪 Тест API</a>
</body>
</html>
    '''

@app.route('/game')
def game():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>BATYR BOL - Игра</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f0f0f0; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        .button { background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 10px; display: inline-block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 BATYR BOL - Игра</h1>
        <p>Добро пожаловать в интерактивную игру по изучению казахской истории!</p>
        <a href="/" class="button">🏠 На главную</a>
    </div>
</body>
</html>
    '''

@app.route('/api/test')
def api_test():
    return jsonify({
        'status': 'success',
        'message': 'API работает корректно!',
        'version': '1.0.0'
    })

def handler(request):
    """
    Vercel serverless function handler
    """
    try:
        # Create a simple WSGI environ
        method = getattr(request, 'method', 'GET')
        path = getattr(request, 'path', '/')
        
        # Simulate Flask request
        with app.test_request_context(path=path, method=method):
            response = app.full_dispatch_request()
            
        return {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.get_data(as_text=True)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error</h1><p>{str(e)}</p>'
        }
