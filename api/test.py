def handler(request):
    """
    Simple test handler for Vercel
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': '''
<!DOCTYPE html>
<html>
<head>
    <title>BATYR BOL - Test</title>
</head>
<body>
    <h1>🇰🇿 BATYR BOL</h1>
    <p>Test page is working!</p>
    <p>If you see this, Vercel deployment is successful.</p>
    <a href="/game">Go to Game</a>
</body>
</html>
        '''
    }
