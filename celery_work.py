#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from celery import Celery, platforms
from app import create_app


def make_celery(app):
    """Create the celery process."""

    # Init the celery object via app's configuration.
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL'])

    # Flask-Celery-Helper to auto-setup the config.
    celery.conf.update(app.config)
    TaskBase = celery.Task
    platforms.C_FORCE_ROOT = True

    class ContextTask(TaskBase):

        abstract = True

        def __call__(self, *args, **kwargs):
            """Will be execute when create the instance object of ContextTesk."""

            # Will context(Flask's Extends) of app object(Producer Sit)
            # be included in celery object(Consumer Site).
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    # Include the app_context into celery.Task.
    # Let other Flask extensions can be normal calls.
    celery.Task = ContextTask
    return celery

flask_app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# 1. Each celery process needs to create an instance of the Flask application.
# 2. Register the celery object into the app object.
celery = make_celery(flask_app)