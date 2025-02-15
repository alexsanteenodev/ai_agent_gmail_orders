.PHONY: venv install clean activate

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Create virtual environment
venv:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

# Helper message for activation (since 'make activate' cannot modify parent shell)
activate:
	@echo "To activate the virtual environment, run:"
	@echo "source $(VENV)/bin/activate"

# Install dependencies
install: venv
	$(PIP) install -r requirements.txt

start-mailer:
	PYTHONPATH=. python src/mailer.py

# Clean up virtual environment and cache
clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Rebuild everything from scratch
rebuild: clean install



.DEFAULT_GOAL := install 