from typing import Callable


def combine_passes(event_callback: Callable[[dict], None]) -> Callable[[dict], None]:
    """Aggregate raw percentages from 2-pass tqdm output into 0-100."""
    in_pass2 = [False]
    pass1_complete = [False]
    last_aggregated = [-1]

    def handle_event(event: dict):
        e = event.get("event")
        if e != "progress":
            event_callback(event)
            return

        raw_percent = event.get("percent", 0)

        if raw_percent == 100:
            pass1_complete[0] = True
        elif pass1_complete[0] and raw_percent < 100:
            in_pass2[0] = True

        if in_pass2[0]:
            aggregated = 90 + int(raw_percent * 10 / 100)
        else:
            aggregated = int(raw_percent * 90 / 100)

        aggregated = min(100, aggregated)

        if aggregated != last_aggregated[0]:
            last_aggregated[0] = aggregated
            event_callback({"event": "progress", "percent": aggregated})

            if aggregated == 100:
                event_callback({"event": "separation_complete"})

    return handle_event


def batch_progress(
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
            stage_complete["separate"] = False
            stage_complete["combine"] = False
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
        task_progress_val = int(separate_percent[0])

        if file_index[0] == 0:
            output = {"stage": "Starting...", "batch_progress": 0, "task_progress": 0}
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
        output = {
            "stage": current_stage[0],
            "batch_progress": total_p,
            "task_progress": task_progress_val,
        }

        if last_emit[0] != output:
            last_emit[0] = output
            progress_callback(output)

    return handle_event
