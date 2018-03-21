APP_PATH=src/paw
MANAGE_CMD=python $(APP_PATH)/manage.py

clean:
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf
	@rm -rf build

install:
	python setup.py install

install-dev:
	pip install -r requirements-dev.txt

.env:
	cp contrib/env .env

run: .env clean
	$(MANAGE_CMD) runserver

migrate: .env
	$(MANAGE_CMD) migrate

migrations: .env
	$(MANAGE_CMD) makemigrations

superuser: .env
	$(MANAGE_CMD) createsuperuser
 
test: clean
	pytest

test-cov: clean
	pytest --cov-report term-missing --cov=paw