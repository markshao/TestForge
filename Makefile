.PHONY: install start-api start-web start-all test clean

install:
	uv sync
	cd web && npm install

start-api:
	uv run forge

start-web:
	cd web && npm run dev

# Use a tool like parallel or concurrently if you want to run both in one terminal
# For simple make, we can't easily background both and keep logs visible for both
# Recommendation: Open two terminals, run 'make start-api' in one and 'make start-web' in the other.

test:
	uv run pytest

# clean:
# 	rm -rf .venv
# 	rm -rf web/node_modules
# 	find . -type d -name "__pycache__" -exec rm -rf {} +
