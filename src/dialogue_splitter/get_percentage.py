import re
from typing import Callable


def get_percentage(event_callback: Callable[[dict], None]) -> Callable[[str], None]:
    """Create a log handler that parses tqdm output and emits raw percentage events."""
    percent_re = re.compile(r"(\d+)%")
    start_re = re.compile(r"Starting separation process for audio_file_path:\s*(.+)")

    def handle_log(line: str):
        start_match = start_re.search(line)
        if start_match:
            event_callback(
                {
                    "event": "file_started",
                    "filename": start_match.group(1),
                }
            )
            return

        percent_match = percent_re.search(line)
        if percent_match:
            percent = int(percent_match.group(1))
            event_callback(
                {
                    "event": "progress",
                    "percent": percent,
                }
            )

    return handle_log
