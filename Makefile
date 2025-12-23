dev:
	python manage.py runserver

migrate:
	python manage.py migrate

test:
	pytest

check:
	black src/
	python manage.py check