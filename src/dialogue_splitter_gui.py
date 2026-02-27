import os
import sys
import threading
from pathlib import Path
from typing import cast

import tkinter as tk
from tkinter import ttk, filedialog

from dialogue_splitter import process_batch


def get_resource_path(filename: str) -> Path:
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)  # type: ignore[attr-defined] / "resources"
    else:
        base_path = Path(__file__).parent.parent / "resources"
    return base_path / filename


def load_icon(window: tk.Tk) -> None:
    icon_path = get_resource_path("logo.png")
    if icon_path.exists():
        try:
            icon = tk.PhotoImage(file=str(icon_path))
            window.tk.call("wm", "iconphoto", window._w, icon)  # type: ignore[attr-defined]
        except Exception:
            pass


def get_file_paths() -> list[str]:
    paths = []
    for arg in sys.argv[1:]:
        if os.path.isfile(arg):
            paths.append(arg)
    return paths


class MainWindow:
    def __init__(self):
        self.file_paths: list[str] = []
        self.output_paths: list[str] = []
        self.cancelled = False

        self.root = tk.Tk()
        self.root.title("Dialogue Splitter")
        self.root.geometry("600x500")

        load_icon(self.root)

        self.setup_ui()

        self.file_paths = get_file_paths()

        if self.file_paths:
            self.show_files()
            self.root.after(100, self.start_processing)
        else:
            self.prompt_for_files()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.title_label = ttk.Label(
            main_frame, text="Dialogue Splitter", font=("Helvetica", 14, "bold")
        )
        self.title_label.pack(pady=(0, 10))

        self.files_frame = ttk.LabelFrame(main_frame, text="Input Files", padding="5")
        self.files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.files_listbox = tk.Listbox(self.files_frame, font=("Monospace", 10))
        self.files_listbox.pack(fill=tk.BOTH, expand=True)

        self.progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="5")
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))

        self.progress_label = ttk.Label(
            self.progress_frame, text="Ready", font=("Arial", 11)
        )
        self.progress_label.pack()

        self.progress_bar = ttk.Progressbar(
            self.progress_frame, length=500, mode="determinate"
        )
        self.progress_bar["maximum"] = 100
        self.progress_bar.pack(pady=5)

        self.results_frame = ttk.LabelFrame(
            main_frame, text="Output Files", padding="5"
        )
        self.results_frame.pack(fill=tk.BOTH, expand=True)

        self.results_listbox = tk.Listbox(self.results_frame, font=("Monospace", 10))
        self.results_listbox.pack(fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        self.select_btn = ttk.Button(
            button_frame, text="Select Files", command=self.prompt_for_files
        )
        self.select_btn.pack(side=tk.LEFT, padx=5)

        self.cancel_btn = ttk.Button(
            button_frame, text="Cancel", command=self._cancel, state=tk.DISABLED
        )
        self.cancel_btn.pack(side=tk.RIGHT, padx=5)

        self.status_label = ttk.Label(main_frame, text="", foreground="gray")
        self.status_label.pack(pady=(5, 0))

    def prompt_for_files(self):
        files = filedialog.askopenfilenames(
            title="Select Video Files",
            filetypes=[
                ("Video files", "*.mp4 *.mov *.avi *.mkv"),
                ("All files", "*.*"),
            ],
        )
        if files:
            self.file_paths = list(files)
            self.show_files()
            self.start_processing()

    def show_files(self):
        self.files_listbox.delete(0, tk.END)
        for path in self.file_paths:
            self.files_listbox.insert(tk.END, path)
        self.status_label.config(text=f"{len(self.file_paths)} file(s) to process")

    def start_processing(self):
        self.select_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)

        thread = threading.Thread(target=self.process_files, daemon=True)
        thread.start()

    def process_files(self):
        try:
            process_batch(cast(list[str | Path], self.file_paths), self.on_progress)
            self.root.after(0, self.on_complete)
        except Exception as e:
            self.root.after(0, lambda: self.on_error(str(e)))

    def on_progress(self, event: dict):
        if self.cancelled:
            return

        stage = event.get("stage", "")
        progress = event.get("progress", 0)

        self.root.after(0, lambda s=stage, p=progress: self.update_progress(s, p))

    def update_progress(self, stage: str, progress: int):
        self.progress_label.config(text=f"{stage}: {progress}%")
        self.progress_bar["value"] = progress
        self.root.update_idletasks()

    def on_complete(self):
        self.progress_label.config(text="Complete!")
        self.progress_bar["value"] = 100
        self.status_label.config(text="Processing complete!", foreground="green")

        for path in self.file_paths:
            stem = Path(path).stem
            output_dir = Path(path).parent / "splits"
            output_file = output_dir / f"{stem}_dual_audio.mov"
            self.results_listbox.insert(tk.END, str(output_file))

        self.cancel_btn.config(text="Close", command=self.root.destroy)

    def on_error(self, error_msg: str):
        self.progress_label.config(text=f"Error: {error_msg}")
        self.status_label.config(text="Processing failed", foreground="red")
        self.cancel_btn.config(text="Close", command=self.root.destroy)

    def _cancel(self):
        self.cancelled = True
        self.root.destroy()


def main():
    MainWindow().root.mainloop()


if __name__ == "__main__":
    main()
