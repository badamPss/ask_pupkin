import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WSGI_DIR = os.path.join(BASE_DIR, "deploy", "wsgi")
sys.path.insert(0, WSGI_DIR)

bind = "127.0.0.1:8001"
workers = 2
wsgi_app = "static_wsgi:application"
pythonpath = WSGI_DIR
accesslog = os.path.join(BASE_DIR, "deploy", "logs", "gunicorn_static_access.log")
errorlog = os.path.join(BASE_DIR, "deploy", "logs", "gunicorn_static_error.log")
loglevel = "info"

