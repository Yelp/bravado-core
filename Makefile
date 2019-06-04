
.PHONY: all
all: test

.PHONY: build
build:
	./setup.py bdist_egg

.PHONY: dev
dev: clean
	./setup.py develop

.PHONY: docs
docs:
	tox -e docs

.PHONY: install
install:
	pip install .

.PHONY: test
test:
	tox

.PHONY: tests
tests: test
	@true

.PHONY: benchmark
benchmark:
	tox -e benchmark

.PHONY: install-hooks
install-hooks:
	tox -e pre-commit

.PHONY: clean
clean:
	@rm -rf .benchmarks .tox build dist docs/build *.egg-info
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
