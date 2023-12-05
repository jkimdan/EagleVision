web: python manage.py makemigrations && python manage.py migrate && gunicorn EagleVision.wsgi
worker: python manage.py process_tasks