import subprocess
from pathlib import Path


def extract_audio(
    video_path: str | Path, output_path: str | Path | None = None
) -> Path:
    """Extract audio from video using ffmpeg."""
    video_path = Path(video_path)
    if output_path is None:
        output_path = video_path.with_suffix(".wav")
    else:
        output_path = Path(output_path)

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "44100",
            "-ac",
            "2",
            str(output_path),
        ],
        check=True,
    )
    return output_path


def combine_dual_audio_video(
    video_path: str | Path,
    vocal_path: str | Path,
    instrumental_path: str | Path,
    output_path: str | Path | None = None,
) -> Path:
    """Combine video with dual audio tracks (vocal + instrumental)."""
    video_path = Path(video_path)
    vocal_path = Path(vocal_path)
    instrumental_path = Path(instrumental_path)

    if output_path is None:
        output_path = video_path.with_suffix(".mov")
    else:
        output_path = Path(output_path)

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-i",
            str(vocal_path),
            "-i",
            str(instrumental_path),
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-map",
            "2:a",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "180k",
            "-metadata:s:a:0",
            "title=Voice",
            "-metadata:s:a:1",
            "title=Ambient",
            "-write_tmcd",
            "0",
            str(output_path),
        ],
        check=True,
    )
    return output_path
