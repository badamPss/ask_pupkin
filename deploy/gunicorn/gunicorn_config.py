import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

bind = "127.0.0.1:8000"
workers = 2
wsgi_app = "ask_pupkin.wsgi:application"
pythonpath = BASE_DIR
accesslog = os.path.join(BASE_DIR, "deploy", "logs", "gunicorn_access.log")
errorlog = os.path.join(BASE_DIR, "deploy", "logs", "gunicorn_error.log")
loglevel = "info"

