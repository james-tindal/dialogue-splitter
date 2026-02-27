import tempfile
from pathlib import Path
from typing import Callable

from .log_handler import parse_logs
from .progress_tracker import track_progress
from .splitter import SplitResult, split_audio
from .tqdm_interceptor import TqdmInterceptor
from .video import combine_dual_audio_video, extract_audio


def process_batch(
    video_paths: list[str | Path],
    on_progress: Callable[[dict], None],
) -> list[Path]:
    """Process multiple video files, reporting progress to callback."""
    total = len(video_paths)
    event_tracker = track_progress(total, on_progress)

    results = []
    for video_path in video_paths:
        video_path = Path(video_path)
        splits_dir = video_path.parent / "splits"
        splits_dir.mkdir(exist_ok=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            event_tracker({"event": "audio_extraction_started"})

            audio_path = extract_audio(
                video_path, temp_path / f"{video_path.stem}_audio.wav"
            )

            event_tracker({"event": "audio_extraction_complete"})

            log_handler = parse_logs(event_tracker)
            with TqdmInterceptor(log_handler):
                split_result = split_audio(audio_path)

            event_tracker({"event": "video_combination_started"})

            output_path = splits_dir / f"{video_path.stem}_dual_audio.mov"
            combine_dual_audio_video(
                video_path,
                split_result.vocals_path,
                split_result.instrumental_path,
                output_path,
            )

        event_tracker(
            {
                "event": "video_combination_complete",
                "output": str(output_path),
            }
        )

        results.append(output_path)

    return results


def process_video(
    video_path: str | Path,
    on_progress: Callable[[dict], None] | None = None,
) -> Path:
    """Process a single video file."""
    if on_progress is None:
        on_progress = lambda e: None
    results = process_batch([video_path], on_progress)
    return results[0]
