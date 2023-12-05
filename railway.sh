#!/usr/bin/env bash
python manage.py process_tasks &
gunicorn EagleVision.wsgi