.PHONY: check tests clean install uninstall build upload

PY=python3

check:
	$(PY) -m ruff check ./irhm

tests:
	$(PY) -m pytest -v ./tests

clean:
	make uninstall
	find ./irhm ./tests -type d -name __pycache__ -exec rm -rf {} +
	rm -rf build
	rm -rf dist
	rm -rf irhm.egg-info

install:
	$(PY) -m pip install .

uninstall:
	$(PY) -m pip uninstall irhm -y
	
build:
	make clean
	$(PY) setup.py build sdist

upload: dist
	$(PY) -m twine upload dist/*
