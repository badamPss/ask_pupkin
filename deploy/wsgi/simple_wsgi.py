def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    
    get_params = {}
    post_params = {}
    
    query_string = environ.get('QUERY_STRING', '')
    if query_string:
        for param in query_string.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                get_params[key] = value
    
    if environ.get('REQUEST_METHOD') == 'POST':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            request_body_size = 0
        
        if request_body_size > 0:
            request_body = environ['wsgi.input'].read(request_body_size)
            post_data = request_body.decode('utf-8')
            for param in post_data.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    post_params[key] = value
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Simple WSGI Application</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #333; }}
            .section {{ margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 5px; }}
            .params {{ margin: 10px 0; }}
            .param {{ padding: 5px; margin: 5px 0; background: white; border-left: 3px solid #007bff; }}
        </style>
    </head>
    <body>
        <h1>Simple WSGI Application</h1>
        <div class="section">
            <h2>GET Parameters:</h2>
            <div class="params">
    """
    
    if get_params:
        for key, value in get_params.items():
            html += f'<div class="param"><strong>{key}</strong>: {value}</div>'
    else:
        html += '<div class="param">No GET parameters</div>'
    
    html += """
            </div>
        </div>
        <div class="section">
            <h2>POST Parameters:</h2>
            <div class="params">
    """
    
    if post_params:
        for key, value in post_params.items():
            html += f'<div class="param"><strong>{key}</strong>: {value}</div>'
    else:
        html += '<div class="param">No POST parameters</div>'
    
    html += """
            </div>
        </div>
        <div class="section">
            <h2>Test Form:</h2>
            <form method="GET" action="">
                <label>GET Parameter: <input type="text" name="get_param" placeholder="Enter value"></label>
                <button type="submit">Send GET</button>
            </form>
            <form method="POST" action="">
                <label>POST Parameter: <input type="text" name="post_param" placeholder="Enter value"></label>
                <button type="submit">Send POST</button>
            </form>
        </div>
    </body>
    </html>
    """
    
    start_response(status, headers)
    return [html.encode('utf-8')]

