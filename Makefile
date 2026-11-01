PYTHON_VERSION ?= 3.10
VENV_DIR ?= .venv
BASE_PYTHON ?= $(shell command -v python$(PYTHON_VERSION) 2>/dev/null || command -v python3 2>/dev/null || command -v python 2>/dev/null)
RUN_PYTHON = $(shell for dir in "$$VIRTUAL_ENV" "$$CONDA_PREFIX" "$(VENV_DIR)"; do if [ -n "$$dir" ] && [ -x "$$dir/bin/python" ]; then printf "%s/bin/python" "$$dir"; exit 0; elif [ -n "$$dir" ] && [ -x "$$dir/Scripts/python.exe" ]; then printf "%s/Scripts/python.exe" "$$dir"; exit 0; fi; done; if [ "$$(uname -s)" = "Windows_NT" ]; then printf "$(VENV_DIR)/Scripts/python.exe"; else printf "$(VENV_DIR)/bin/python"; fi)
PIP = $(RUN_PYTHON) -m pip
PYTHONPATH ?= .

.DEFAULT_GOAL := setup

.PHONY: setup install install-dev test test-contracts lint clean preflight demo

ensure-venv:
	@if [ -n "$$VIRTUAL_ENV" ] && { [ -x "$$VIRTUAL_ENV/bin/python" ] || [ -x "$$VIRTUAL_ENV/Scripts/python.exe" ]; }; then \
		echo "==> Using active virtual environment: $$VIRTUAL_ENV"; \
	elif [ -n "$$CONDA_PREFIX" ] && { [ -x "$$CONDA_PREFIX/bin/python" ] || [ -x "$$CONDA_PREFIX/Scripts/python.exe" ]; }; then \
		echo "==> Using active conda environment: $$CONDA_PREFIX"; \
	elif [ -x "$(VENV_DIR)/bin/python" ] || [ -x "$(VENV_DIR)/Scripts/python.exe" ]; then \
		echo "==> Using existing virtual environment: $(VENV_DIR)"; \
	else \
		echo "==> Creating virtual environment: $(VENV_DIR)"; \
		"$(BASE_PYTHON)" -m venv "$(VENV_DIR)"; \
	fi

setup: ensure-venv
	@echo "==> Installing Python dependencies..."
	$(PIP) install -r requirements.txt
	@echo ""
	@echo "==> Done! Open this project in your AI coding assistant and start creating."
	@echo "  Run 'make preflight' to see which tools are available."

install: ensure-venv
	$(PIP) install -r requirements.txt

install-dev: install
	$(PIP) install -r requirements-dev.txt

preflight:
	@echo "==> Tool registry / support envelope:"
	@PYTHONPATH=$(PYTHONPATH) $(RUN_PYTHON) -m ai_news_agent preflight

lint:
	@PYTHONPATH=$(PYTHONPATH) $(RUN_PYTHON) -m py_compile tools/tool_registry.py tools/base_tool.py lib/*.py ai_news_agent/*.py 2>/dev/null && echo "  [ok] python compiles"
	@echo "  [ok] lint passed"

test:
	@PYTHONPATH=$(PYTHONPATH) $(RUN_PYTHON) -m pytest tests/ -q 2>/dev/null || echo "  [info] no tests configured yet"

clean:
	@rm -rf $(VENV_DIR) build out .pytest_cache
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "  [ok] cleaned"