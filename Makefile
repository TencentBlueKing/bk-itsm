# Usage: export VIRTUAL_ENV=/data/env/itsm/
#        make help

SHELL := /bin/sh

# SET THIS! Directory containing wsgi.py
PROJECT := 'itsm'
BK_ENV := 'development'

# VIRTUAL_ENV = ${$(shell which python)%/bin*}
# VIRTUAL_ENV := /data/env/itsm

LOCALPATH := .
PYTHONPATH := $(VIRTUAL_ENV)/bin
PYTHON_BIN := $(PYTHONPATH)/python

SETTINGS := settings
DJANGO_SETTINGS_MODULE = $(SETTINGS)
DJANGO_POSTFIX := --settings=$(DJANGO_SETTINGS_MODULE) --pythonpath=$(PYTHONPATH)

TEST_SETTINGS := settings
DJANGO_TEST_SETTINGS_MODULE = $(TEST_SETTINGS)
DJANGO_POSTFIX := --settings=$(DJANGO_SETTINGS_MODULE) --pythonpath=$(PYTHONPATH)
DJANGO_TEST_POSTFIX := --settings=$(DJANGO_TEST_SETTINGS_MODULE) --pythonpath=$(PYTHONPATH)

.PHONY: clean showenv coverage test pip virtualenv virtual_env_set

showenv:
	@echo 'Environment:'
	@echo '-----------------------'
	@$(PYTHON_BIN) -c "import sys; print 'sys.path:', sys.path"
	@echo 'PYTHONPATH:' $(PYTHONPATH)
	@echo 'PROJECT:' $(PROJECT)
	@echo 'DJANGO_SETTINGS_MODULE:' $(DJANGO_SETTINGS_MODULE)
	@echo 'DJANGO_TEST_SETTINGS_MODULE:' $(DJANGO_TEST_SETTINGS_MODULE)

pip: virtual_env_set
	pip install -r requirements.txt

virtualenv:
	virtualenv --no-site-packages $(VIRTUAL_ENV)
	echo $(VIRTUAL_ENV)

djangohelp: virtual_env_set
	$(PYTHON_BIN) manage.py help $(DJANGO_POSTFIX)

migrate: virtual_env_set
	$(PYTHON_BIN) manage.py migrate $(DJANGO_POSTFIX)
	$(PYTHON_BIN) manage.py createcachetable django_cache

collectstatic: virtual_env_set
	-mkdir -p .$(LOCALPATH)/static
	$(PYTHON_BIN) manage.py collectstatic -c --noinput $(DJANGO_POSTFIX)

runserver: virtual_env_set
	$(PYTHON_BIN) manage.py runserver $(DJANGO_POSTFIX)

start_celery: virtual_env_set
	$(PYTHON_BIN) manage.py celery worker $(DJANGO_POSTFIX)

clean_task: virtual_env_set
	$(PYTHON_BIN) manage.py celery purge -f $(DJANGO_POSTFIX)

dbshell: virtual_env_set
	$(PYTHON_BIN) manage.py dbshell $(DJANGO_POSTFIX)

shell_plus: virtual_env_set
	$(PYTHON_BIN) manage.py shell_plus $(DJANGO_POSTFIX)

reset_db: virtual_env_set
	$(PYTHON_BIN) manage.py reset_db --noinput $(DJANGO_POSTFIX)

icheck:
	isort -rc -ac -df .

isort:
	isort -rc -ac .

rsync:
	rsync -avz --checksum --exclude-from .gitignore --exclude-from .rsyncignore . ${REMOTE_URI}

compare:
	rsync -avz --checksum --dry-run --exclude-from .gitignore --exclude-from .rsyncignore . ${REMOTE_URI}

clean:
	# find . -name "*.pyc" -print0 | xargs -0 rm -rf
	find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
	-rm -rf htmlcov
	-rm -rf .coverage
	-rm -rf build
	-rm -rf dist
	-rm -rf src/*.egg-info
	-rm -rf ../templates_module
	-rm -rf .cache

git_clean: clean
	git clean -fdx -e .idea -e config -e static/assets

test: clean virtual_env_set
	-$(PYTHON_PATH)/coverage run $(PYTHON_BIN) manage.py test $(APP) $(DJANGO_TEST_POSTFIX)

coverage: virtual_env_set
	$(PYTHON_PATH)/coverage html --include="$(LOCALPATH)/*" --omit="*/admin.py,*/test*"

all: collectstatic

