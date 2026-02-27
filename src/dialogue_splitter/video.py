import subprocess
from pathlib import Path
import sys
import os
import tkinter as tk
from tkinter import messagebox


def appendToPath(directory: str) -> None:
    current = os.environ.get('PATH', '')
    if not current:
        os.environ['PATH'] = directory
        return

    parts = current.split(os.pathsep)
    if directory not in parts:
        os.environ['PATH'] = current + os.pathsep + directory

def get_ffmpeg_path():
    root = tk.Tk()
    root.withdraw()

    if getattr(sys, "frozen", False):
        if sys.executable:
            contents_path = Path(sys.executable).parent.parent
            p = contents_path / "Frameworks" / "ffmpeg"
            messagebox.showinfo("Debug", f"pre get_ffmpeg_path: frozen, checking {p}")
            appendToPath(str(contents_path / "Frameworks"))
            messagebox.showinfo("Debug", f"post get_ffmpeg_path: frozen, checking {p}")
            if p.exists():
                root.destroy()
                return p

        root.destroy()
        return None
    else:
        messagebox.showinfo(
            "Debug", "get_ffmpeg_path: not frozen, returning /usr/local/bin/ffmpeg"
        )
        root.destroy()
        return Path("/usr/local/bin/ffmpeg")


ffmpeg_path = get_ffmpeg_path()


def extract_audio(
    video_path: str | Path, output_path: str | Path | None = None
) -> Path:
    """Extract audio from video using ffmpeg."""
    messagebox.showinfo("Debug", "extract_audio called")

    video_path = Path(video_path)
    if output_path is None:
        output_path = video_path.with_suffix(".wav")
    else:
        output_path = Path(output_path)

    try:
        subprocess.run(
            [
                str(ffmpeg_path),
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
    except Exception as e:
        messagebox.showerror("Error", str(e))
        raise
    return output_path


def combine_dual_audio_video(
    video_path: str | Path,
    vocal_path: str | Path,
    instrumental_path: str | Path,
    output_path: str | Path | None = None,
) -> Path:
    """Combine video with dual audio tracks (vocal + instrumental)."""
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Debug", "combine_dual_audio_video called")
    root.destroy()

    video_path = Path(video_path)
    vocal_path = Path(vocal_path)
    instrumental_path = Path(instrumental_path)

    if output_path is None:
        output_path = video_path.with_suffix(".mov")
    else:
        output_path = Path(output_path)

    subprocess.run(
        [
            str(ffmpeg_path),
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
