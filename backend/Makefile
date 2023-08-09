run:
	python manage.py migrate --noinput
	python manage.py collectstatic --noinput
	cp -r ./static/ /var/html/
	python manage.py load_data
	gunicorn --bind 0:8000 foodgram_backend.wsgi
	exec "$@"