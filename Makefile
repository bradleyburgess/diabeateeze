dev:
	.venv/bin/python manage.py runserver

migrate:
	.venv/bin/python manage.py migrate

test:
	.venv/bin/pytest

check:
	.venv/bin/black src/
	.venv/bin/python manage.py check