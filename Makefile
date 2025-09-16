PY=python3
PIP=pip3
VENV?=.venv
ACTIVATE=. $(VENV)/bin/activate

.PHONY: help
help:
	@echo "Common targets:"
	@echo "  make venv        # Create virtual env"
	@echo "  make install     # Install deps"
	@echo "  make test        # Run tests"
	@echo "  make run         # Run app (uvicorn)"
	@echo "  make lint        # Run flake8"
	@echo "  make format      # Run black & isort"
	@echo "  make clean       # Remove caches"

venv:
	$(PY) -m venv $(VENV)
	$(ACTIVATE); $(PIP) install --upgrade pip

install:
	$(PIP) install -r requirements.txt

 test:
	pytest -q

run:
	uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

lint:
	flake8 src tests

format:
	black src tests
	isort src tests

clean:
	rm -rf .pytest_cache .mypy_cache __pycache__ */__pycache__ .coverage htmlcov
