run:
	python manage.py migrate --noinput
	python manage.py collectstatic --noinput
	cp -r ./static_backend /backend_stastic
	python manage.py load_data
	gunicorn --bind 0:8000 foodgram_backend.wsgi
	exec "$@"