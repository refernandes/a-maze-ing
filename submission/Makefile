# Makefile for A-Maze-ing (École 42)

PYTHON = python3
CONFIG = config.txt

.PHONY: all install run debug clean lint lint-strict build

all: install run

install:
	$(PYTHON) -m pip install --upgrade build flake8 mypy

run:
	$(PYTHON) a_maze_ing.py $(CONFIG)

debug:
	$(PYTHON) -m pdb a_maze_ing.py $(CONFIG)

clean:
	rm -rf __pycache__ mazegen/__pycache__ .mypy_cache build dist *.egg-info

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

build:
	$(PYTHON) -m build --wheel --sdist --outdir .
