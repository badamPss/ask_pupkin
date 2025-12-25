def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Dynamic Content Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .info { margin: 20px 0; padding: 15px; background: #e8f4f8; border-left: 4px solid #2196F3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Dynamic Content Test</h1>
            <div class="info">
                <p><strong>This is a dynamic WSGI application.</strong></p>
                <p>Current time: """ + str(__import__('datetime').datetime.now()) + """</p>
                <p>This content is generated dynamically for performance testing.</p>
            </div>
            <div class="info">
                <p>File size: approximately same as static sample.html</p>
                <p>This endpoint is used to compare performance between static and dynamic content delivery.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    start_response(status, headers)
    return [html.encode('utf-8')]

