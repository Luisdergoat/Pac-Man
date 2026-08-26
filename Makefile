# ============================================================
# Pac-Man Makefile
# ============================================================

VENV_NAME  := venv
BACKEND_DIR:= backend
PORT       := 5000
URL        := http://127.0.0.1:$(PORT)
VENV_PY    := $(BACKEND_DIR)/$(VENV_NAME)/bin/python

.PHONY: all install run debug lint lint-strict clean fclean re

# make ohne Argument macht dasselbe wie "make run"
all: run

# ------------------------------------------------------------
# install: legt das venv an (uv venv <name>) und installiert
# alle Requirements hinein.
# ------------------------------------------------------------
install:

	@osascript -e 'tell application "Terminal" to do script "cd $(CURDIR)/$(BACKEND_DIR) && rm -rf $(VENV_NAME) && uv venv $(VENV_NAME) --python 3.12 --seed && $(VENV_NAME)/bin/pip install -r requirements.txt && $(VENV_NAME)/bin/uvicorn server:app --reload --port $(PORT)"'



# ------------------------------------------------------------
# run: oeffnet ein neues Terminal-Fenster, aktiviert dort das
# venv, startet den FastAPI-Server per uvicorn und oeffnet
# danach automatisch Chrome auf localhost.
# ------------------------------------------------------------
run: install
	@sleep 10
	@open -a "Google Chrome" $(URL)

# ------------------------------------------------------------
# debug: startet den Server unter pdb (Python Debugger)
# ------------------------------------------------------------
debug:
	cd $(BACKEND_DIR) && $(VENV_PY) -m pdb -m uvicorn server:app --port $(PORT)

# ------------------------------------------------------------
# lint / lint-strict: exakt die vom Subject geforderten Befehle
# ------------------------------------------------------------
lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

# ------------------------------------------------------------
# clean: temporaere Dateien/Caches loeschen (venv bleibt erhalten)
# ------------------------------------------------------------
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# ------------------------------------------------------------
# fclean: clean + venv komplett entfernen
# ------------------------------------------------------------
fclean: clean
	rm -rf $(BACKEND_DIR)/$(VENV_NAME)

# ------------------------------------------------------------
# re: alles platt machen und neu aufsetzen
# ------------------------------------------------------------
re: fclean install run