import tkinter as tk
from tkinter import ttk


class MainWindow:
    def __init__(self, file_list):
        self.file_list = file_list
        self.cancelled = False

        self.root = tk.Tk()
        self.root.title("Dialogue Splitter")
        self.root.geometry("400x150")

        self.label = tk.Label(self.root, text="Starting...", font=("Arial", 12))
        self.label.pack(pady=20)

        self.progress = ttk.Progressbar(self.root, length=300, mode="determinate")
        self.progress["maximum"] = 100
        self.progress.pack(pady=10)

        self.cancel_btn = tk.Button(self.root, text="Cancel", command=self._cancel)
        self.cancel_btn.pack(pady=10)

    def _cancel(self):
        self.cancelled = True

    def update_progress(self, event):
        if self.cancelled:
            return

        stage = event.get("stage", "")
        progress = event.get("progress", 0)

        self.label.config(text=f"{stage}: {progress}%")
        self.progress["value"] = progress
        self.root.update_idletasks()

    def show_complete(self):
        self.label.config(text="Complete!")
        self.progress["value"] = 100
        self.cancel_btn.config(text="Close", command=self.root.destroy)
