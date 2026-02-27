import re
from typing import Callable


def parse_logs(event_callback: Callable[[dict], None]) -> Callable[[str], None]:
    """Create a log handler that parses tqdm output and emits events."""
    progress_re = re.compile(r"\|\s*(\d+)/(\d+)\s*\[")
    start_re = re.compile(r"Starting separation process for audio_file_path:\s*(.+)")
    pass_count = [0]

    def handle_log(line: str):
        start_match = start_re.search(line)
        if start_match:
            event_callback(
                {
                    "event": "file_started",
                    "filename": start_match.group(1),
                }
            )
            pass_count[0] = 0
            return

        progress_match = progress_re.search(line)
        if progress_match:
            current = int(progress_match.group(1))
            total = int(progress_match.group(2))
            percent = int((current / total) * 100)
            event_callback(
                {
                    "event": "progress",
                    "percent": percent,
                }
            )
            if current == total:
                pass_count[0] += 1
                if pass_count[0] == 1:
                    event_callback({"event": "separation_complete"})

    return handle_log
