ENTRY = pac_man.py
SRC = src/
ARGS = $(wordlist 2, $(words $(MAKECMDGOALS)), $(MAKECMDGOALS))

install:
	uv sync

run: install
	uv run python3 $(ENTRY) $(ARGS)

debug: install
	uv run python3 pdb $(ENTRY) $(ARGS)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

fclean: clean
	rm -rf .venv
	rm -rf uv.lock

lint:
	uv run flake8 $(SRC) $(ENTRY)
	uv run mypy $(SRC) $(ENTRY)

lint-strict:
	uv run flake8 $(SRC) $(ENTRY)
	uv run mypy $(SRC) $(ENTRY) --strict

%:
	@:
