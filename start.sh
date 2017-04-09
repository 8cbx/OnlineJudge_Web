#!/usr/bin/env bash

celery -A celery_work worker --loglevel=info -f ./celery-$HOSTNAME.log -c 2 &

gunicorn -c guni.conf manage:app