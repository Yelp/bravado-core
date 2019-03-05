.PHONY: all install test tests clean docs benchmark

all: test

build:
	./setup.py bdist_egg

dev: clean
	./setup.py develop

docs:
	tox -e docs

install:
	pip install .

test:
	tox -- tests --ignore tests/profiling

tests: test

benchmark: install-hooks
	tox -e benchmark

.PHONY: install-hooks
install-hooks:
	tox -e pre-commit

clean:
	@rm -rf .benchmarks .tox build dist docs/build *.egg-info
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
