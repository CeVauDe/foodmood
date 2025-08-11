#!/usr/bin/env bash

python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn --config ../gunicorn.conf.py foodmood.wsgi:application
