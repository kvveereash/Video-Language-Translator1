from flask import Flask
from flask_cors import CORS
from celery import Celery
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    return app

def create_celery(app):
    # Configure Celery with old style config
    app.config.update(
        CELERY_BROKER_URL=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        CELERY_RESULT_BACKEND=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        CELERY_TASK_SERIALIZER='json',
        CELERY_RESULT_SERIALIZER='json',
        CELERY_ACCEPT_CONTENT=['json'],
        CELERY_TIMEZONE='UTC',
        CELERY_ENABLE_UTC=True,
        CELERY_IMPORTS=['app.tasks']
    )

    celery = Celery(
        app.name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND'],
        include=['app.tasks']
    )
    celery.conf.update(app.config)
    return celery

app = create_app()
celery = create_celery(app)

# Import routes after app is created to avoid circular imports
from app import routes 