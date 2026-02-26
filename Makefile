test:
	.venv/bin/pytest tests/ -v

clean:
	rm -rf .pytest_cache .ruff_cache

typecheck:
	pyright src/
