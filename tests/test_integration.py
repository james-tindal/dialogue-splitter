import subprocess
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def test_video(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("video")
    video_path = tmp / "test_video.mov"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=blue:s=320x240:d=10",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=10",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-shortest",
            str(video_path),
        ],
        check=True,
        capture_output=True,
    )
    return video_path


def test_extract_audio(test_video):
    from dialogue_splitter import extract_audio

    audio_path = test_video.parent / "test_audio.wav"
    result = extract_audio(test_video, audio_path)

    assert result.exists()
    assert result.suffix == ".wav"


def test_process_video_end_to_end(test_video):
    from dialogue_splitter import process_video

    result = process_video(test_video)

    assert result.exists()
    assert result.suffix == ".mov"


def test_output_has_dual_audio_tracks(test_video):
    from dialogue_splitter import process_video

    result = process_video(test_video)

    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=index",
            "-of",
            "csv=p=0",
            str(result),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    audio_streams = probe.stdout.strip().split("\n")
    audio_count = len([s for s in audio_streams if s])

    assert audio_count == 2, f"Expected 2 audio tracks, got {audio_count}"
