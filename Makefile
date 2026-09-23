ENTRY = pac_man.py
CONFIG = "config.json"
BACKEND = backend/

install:
	uv sync

run: install
	uv run python3 $(ENTRY) $(CONFIG)

debug: install
	uv run python3 pdb $(ENTRY) $(CONFIG)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

lint:
	uv run flake8 $(BACKEND) $(ENTRY)
	uv run mypy $(BACKEND) $(ENTRY)

lint-strict:
	uv run flake8 $(BACKEND) $(ENTRY)
	uv run mypy $(BACKEND) $(ENTRY) --strict
