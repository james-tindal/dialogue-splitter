import sys
from pathlib import Path

from dialogue_splitter import process_batch


def main():
    files = sys.argv[1:]

    if not files:
        print("Usage: python -m gui file1.mov [file2.mov ...]")
        sys.exit(1)

    file_list = [Path(f) for f in files]

    def on_progress(event):
        stage = event.get("stage", "")
        progress = event.get("progress", 0)
        print(f"{stage}: {progress}%")

    process_batch(file_list, on_progress)

    print("Complete!")


if __name__ == "__main__":
    main()
