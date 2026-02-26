import tempfile
from pathlib import Path

from .splitter import SplitResult, split_audio
from .video import combine_dual_audio_video, extract_audio


def process_video(video_path: str | Path) -> Path:
    """Process a video: extract audio, split stems, combine with original video."""
    video_path = Path(video_path)
    splits_dir = video_path.parent / "splits"
    splits_dir.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        audio_path = extract_audio(
            video_path, temp_path / f"{video_path.stem}_audio.wav"
        )

        split_result = split_audio(audio_path)

        output_path = splits_dir / f"{video_path.stem}_dual_audio.mov"
        return combine_dual_audio_video(
            video_path,
            split_result.vocals_path,
            split_result.instrumental_path,
            output_path,
        )


__all__ = [
    "SplitResult",
    "split_audio",
    "extract_audio",
    "combine_dual_audio_video",
    "process_video",
]
