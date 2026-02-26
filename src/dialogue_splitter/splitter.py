from dataclasses import dataclass
from pathlib import Path


@dataclass
class SplitResult:
    vocals_path: Path
    instrumental_path: Path


def split_audio(audio_path: str | Path) -> SplitResult:
    """Split audio into vocals and instrumental stems using audio-separator."""
    from audio_separator.separator import Separator  # type: ignore[import]

    audio_path = Path(audio_path)
    output_dir = audio_path.parent

    separator = Separator(output_dir=str(output_dir))
    separator.load_model(model_filename="UVR-MDX-NET-Inst_HQ_1.onnx")

    output_files = separator.separate(str(audio_path))

    vocals_path = None
    instrumental_path = None
    for f in output_files:
        if "Vocals" in f:
            vocals_path = output_dir / Path(f).name
        elif "Instrumental" in f:
            instrumental_path = output_dir / Path(f).name

    if vocals_path is None or instrumental_path is None:
        raise RuntimeError(f"Failed to find both stems in output: {output_files}")

    return SplitResult(vocals_path=vocals_path, instrumental_path=instrumental_path)
