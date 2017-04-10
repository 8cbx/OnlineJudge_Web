#!/usr/bin/env bash

echo CELERY_BROKER_URL="amqp://guest:guest@$RABBITMQ_PORT_5672_TCP_ADDR:$RABBITMQ_PORT_5672_TCP_PORT//" >> /etc/profile

echo CELERY_BACKEND_URL="db+mysql://$MYSQL_USER:$MYSQL_PASS@$MYSQL_ADDR:$MYSQL_PORT/celery_backend" >> /etc/profile

source /etc/profile

celery -A celery_work worker --loglevel=info -f ./celery-$HOSTNAME.log -c 2 &

gunicorn -c guni.conf manage:app