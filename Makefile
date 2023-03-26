TESTS_PATH := $(PWD)/tests
WORKDIR_PATH := $(PWD)/workdir
WORKDIR_MODELS_PATH := $(WORKDIR_PATH)/models
WORKDIR_DATA_PATH := $(WORKDIR_PATH)/data
PROJECT_NAME := mlversion

build:
	bumpversion build
	pip install build
	python -m build
	$(MAKE) doc

release:
	bumpversion release --tag
	pip install build
	python -m build
	$(MAKE) doc

pypi:
	pip install twine
	python -m twine upload dist/*

release-up:
	bumpversion release

patch:
	bumpversion patch

test-build:
	pip install -e .
	$(MAKE) doc
	$(MAKE) clear

doc:
	bash scripts/build.sh

clear:
	rm -rf mlversion.egg-info
	rm -rf dist
	
uninstall:
	pip uninstall mlversion -y

env-create:
	conda env create -n mlversion --file environment.yml

env-clear:
	conda env remove -n mlversion

unit-test:
	if [ ! -d $(WORKDIR_PATH) ]; then rm -rf $(WORKDIR_PATH); fi
	mkdir -p $(WORKDIR_PATH);
	mkdir -p $(WORKDIR_MODELS_PATH);
	mkdir -p $(WORKDIR_DATA_PATH);
	pytest $(TESTS_PATH) -vvv  --cov=$(PROJECT_NAME) --cov-report=html --cov-report=term -s
	rm -rf $(WORKDIR_PATH)

flake:
	flake8 mlversion tests