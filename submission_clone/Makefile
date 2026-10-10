PYTHON = python3
CONFIG = config.txt

.PHONY: install run debug clean lint build

install:
	$(PYTHON) -m pip install --upgrade build flake8 mypy

run:
	$(PYTHON) a_maze_ing.py $(CONFIG)

debug:
	$(PYTHON) -m pdb a_maze_ing.py $(CONFIG)

clean:
	rm -rf __pycache__ mazegen/__pycache__ *.pyc .mypy_cache build dist *.egg-info

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

build:
	$(PYTHON) -m build --wheel --sdist --outdir .
