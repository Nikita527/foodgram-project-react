run:
	python manage.py migrate
	python manage.py collectstatic --noinput
	python manage.py load_data
	gunicorn --bind 0:8000 foodgram_backend.wsgi