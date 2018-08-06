.PHONY: docs

APP_PATH=src/pawapp
PROJECT_PATH=src/paw
MANAGE_CMD=python $(PROJECT_PATH)/manage.py
INITIAL_FIXTURE_FILE=$(APP_PATH)/fixtures/initial_data.json

clean:
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf
	@rm -rf build

install:
	pip install . && pip install -r requirements/prod.txt

install-dev:
	pip install -e . && pip install -r requirements/dev.txt

install-test:
	pip install -e . && pip install -r requirements/test.txt

install-docs:
	pip install . && pip install -r requirements/docs.txt

.env:
	cp contrib/env .env

run: .env clean
	$(MANAGE_CMD) runserver

worker: .env clean
	$(MANAGE_CMD) rqworker default

migrate: .env clean
	$(MANAGE_CMD) migrate

dump-initial-data:
	$(MANAGE_CMD) dumpdata --exclude auth.permission --exclude contenttypes > $(INITIAL_FIXTURE_FILE)

load-initial-data:
	$(MANAGE_CMD) loaddata $(INITIAL_FIXTURE_FILE)

migrations: .env clean
	$(MANAGE_CMD) makemigrations

superuser: .env
	$(MANAGE_CMD) createsuperuser

collectstatic: .env
	$(MANAGE_CMD) collectstatic
 
test: .env clean
	pytest

test-cov: .env clean
	pytest --cov-report term-missing --cov=paw

test-tox: .env clean
	tox -v

docs:
	cd docs && make html
