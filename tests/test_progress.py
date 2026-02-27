from dialogue_splitter.log_handler import parse_logs
from dialogue_splitter.progress_tracker import track_progress


def test_parse_logs_emits_progress_events():
    events = []

    def capture(event):
        events.append(event)

    handler = parse_logs(capture)

    handler("  0%|          | 0/2 [00:00<, ?it/s]")
    handler(" 50%|█████     | 1/2 [00:04<00:04,  4.40s/it]")
    handler("100%|██████████| 2/2 [00:09<00:00,  4.98s/it]")

    assert events == [
        {"event": "progress", "percent": 0},
        {"event": "progress", "percent": 50},
        {"event": "progress", "percent": 100},
        {"event": "separation_complete"},
    ]


def test_parse_logs_emits_file_started():
    events = []

    def capture(event):
        events.append(event)

    handler = parse_logs(capture)

    handler(
        "2026-02-27 00:03:55,705 - INFO - separator - Starting separation process for audio_file_path: /tmp/test.wav"
    )

    assert events == [
        {"event": "file_started", "filename": "/tmp/test.wav"},
    ]


def test_track_progress_emits_global():
    events = []

    def capture(event):
        events.append(event)

    tracker = track_progress(2, capture)

    tracker({"event": "audio_extraction_started"})
    tracker({"event": "audio_extraction_complete"})
    tracker({"event": "file_started"})
    tracker({"event": "progress", "percent": 50})
    tracker({"event": "separation_complete"})
    tracker({"event": "video_combination_started"})
    tracker({"event": "video_combination_complete", "output": "/tmp/out.mov"})

    assert any(
        e.get("stage", "").startswith("Processing file") for e in events if "stage" in e
    )
    assert any(e.get("progress", -1) > 0 for e in events if "progress" in e)
