import os

def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    
    wsgi_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(wsgi_dir))
    static_dir = os.path.join(base_dir, 'static')
    file_path = os.path.join(static_dir, 'sample.html')
    
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
    except FileNotFoundError:
        status = '404 Not Found'
        content = b'File not found'
    
    start_response(status, headers)
    return [content]

