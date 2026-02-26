from pathlib import Path
from unittest.mock import patch, MagicMock

from dialogue_splitter import SplitResult


def test_split_audio_returns_result():
    mock_output = [
        "/tmp/audio_(Vocals).flac",
        "/tmp/audio_(Instrumental).flac",
    ]

    with patch("audio_separator.separator.Separator") as MockSeparator:
        mock_instance = MagicMock()
        mock_instance.separate.return_value = mock_output
        MockSeparator.return_value = mock_instance

        from dialogue_splitter.splitter import split_audio

        result = split_audio("/tmp/audio.wav")

        assert isinstance(result, SplitResult)
        assert result.vocals_path == Path("/tmp/audio_(Vocals).flac")
        assert result.instrumental_path == Path("/tmp/audio_(Instrumental).flac")
