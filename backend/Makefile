run:
	python manage.py migrate
	python manage.py collectstatic
	python manage.py load_data
	cp -r /app/collected_static/. /backend_static/static/
	gunicorn --bind 0:8000 foodgram_backend.wsgi