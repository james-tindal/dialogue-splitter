from typing import Callable


def track_progress(
    total_files: int, progress_callback: Callable[[dict], None]
) -> Callable[[dict], None]:
    """Create an event tracker that calculates global progress and emits to callback."""
    file_index = [0]
    current_stage = ["Starting..."]
    stage_weight = {"extract": 10, "separate": 80, "combine": 10}
    stage_complete: dict = {"extract": False, "separate": False, "combine": False}
    separate_percent = [0]
    last_emit: list[dict | None] = [None]

    def handle_event(event: dict):
        e = event.get("event")

        if e == "audio_extraction_started":
            current_stage[0] = "extracting"
            stage_complete["extract"] = False
            _emit()

        elif e == "audio_extraction_complete":
            stage_complete["extract"] = True
            _emit()

        elif e == "file_started":
            file_index[0] += 1
            current_stage[0] = f"Processing file {file_index[0]} of {total_files}"
            stage_complete.clear()
            stage_complete.update(
                {"extract": False, "separate": False, "combine": False}
            )
            separate_percent[0] = 0
            _emit()

        elif e == "progress":
            separate_percent[0] = event.get("percent", 0)
            current_stage[0] = f"Processing file {file_index[0]} of {total_files}"
            _emit()

        elif e == "separation_complete":
            stage_complete["separate"] = True
            separate_percent[0] = 100
            _emit()

        elif e == "video_combination_started":
            current_stage[0] = f"Processing file {file_index[0]} of {total_files}"
            stage_complete["combine"] = False
            _emit()

        elif e == "video_combination_complete":
            stage_complete["combine"] = True
            current_stage[0] = f"Processing file {file_index[0]} of {total_files}"
            _emit()

    def _emit():
        if file_index[0] == 0:
            output = {"stage": "Starting...", "progress": 0}
            if last_emit[0] != output:
                last_emit[0] = output
                progress_callback(output)
            return

        base = (file_index[0] - 1) * 100 / total_files if total_files > 0 else 0

        if not stage_complete["extract"] and not stage_complete["separate"]:
            stage_p = 0
        elif stage_complete["extract"] and not stage_complete["separate"]:
            stage_p = stage_weight["extract"] + (
                separate_percent[0] / 100 * stage_weight["separate"]
            )
        elif stage_complete["separate"] and not stage_complete["combine"]:
            stage_p = stage_weight["extract"] + stage_weight["separate"]
        elif stage_complete["combine"]:
            stage_p = (
                stage_weight["extract"]
                + stage_weight["separate"]
                + stage_weight["combine"]
            )
        else:
            stage_p = 0

        total_p = int(base + (stage_p / total_files))
        output = {"stage": current_stage[0], "progress": total_p}

        if last_emit[0] != output:
            last_emit[0] = output
            progress_callback(output)

    return handle_event
