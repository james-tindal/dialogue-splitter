test:
    .venv/bin/pytest tests/ -v

run *FILES:
    .venv/bin/dialogue-splitter "{{FILES}}"

run-cli VIDEO:
    .venv/bin/python -c "from dialogue_splitter import process_video; import sys; process_video(sys.argv[1], lambda e: print('callback:', e))" {{ VIDEO }}

build:
    [ -d "dist" ] && xattr -rc dist && sync && rm -rf dist
    .venv/bin/pyinstaller app.spec

clean:
    rm -rf .pytest_cache .ruff_cache

typecheck:
    pyright src/
