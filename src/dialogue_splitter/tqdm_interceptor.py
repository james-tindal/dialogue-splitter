import re
import sys
from typing import Callable


class TqdmInterceptor:
    def __init__(self, log_callback: Callable[[str], None]):
        self._log_callback = log_callback
        self._original_stderr = None

    def __enter__(self):
        import tqdm

        self._original_stderr = sys.stderr
        sys.stderr = TqdmWriter(self._original_stderr, self._log_callback)
        return self

    def __exit__(self, *args):
        if self._original_stderr is not None:
            sys.stderr = self._original_stderr


class TqdmWriter:
    def __init__(self, original, callback):
        self._original = original
        self._callback = callback

    def write(self, data):
        for line in data.splitlines():
            if line.strip():
                self._callback(line)
        return self._original.write(data)

    def flush(self):
        return self._original.flush()
