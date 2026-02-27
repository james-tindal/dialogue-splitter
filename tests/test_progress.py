from dialogue_splitter.get_percentage import get_percentage
from dialogue_splitter.progress_tracker import batch_progress, combine_passes


def test_get_percentage_extracts_raw_percentages():
    """get_percentage should extract the percentage number directly from tqdm output."""
    events = []

    def capture(event):
        events.append(event)

    handler = get_percentage(capture)

    handler("  0%|          | 0/10 [00:00<, ?it/s]")
    handler(" 10%|#         | 1/10 [00:04<00:39, 4.35s/it]")
    handler(" 50%|#####     | 5/10 [00:22<00:21, 4.24s/it]")
    handler("100%|##########| 10/10 [00:45<00:00, 4.63s/it]")

    progress_events = [e for e in events if e.get("event") == "progress"]
    percents = [e.get("percent") for e in progress_events]

    assert percents == [0, 10, 50, 100]


def test_get_percentage_extracts_from_real_output():
    """get_percentage extracts percentages from actual audio-separator tqdm output."""
    events = []

    def capture(event):
        events.append(event)

    handler = get_percentage(capture)

    pass_1_lines = [
        "  0%|          | 0/10 [00:00<, ?it/s]",
        " 10%|#         | 1/10 [00:04<00:39, 4.35s/it]",
        " 20%|##        | 2/10 [00:10<00:42, 5.25s/it]",
        " 30%|###       | 3/10 [00:14<00:33, 4.86s/it]",
        " 40%|####      | 4/10 [00:18<00:26, 4.44s/it]",
        " 50%|#####     | 5/10 [00:22<00:21, 4.24s/it]",
        " 60%|######    | 6/10 [00:26<00:16, 4.12s/it]",
        " 70%|#######   | 7/10 [00:30<00:12, 4.18s/it]",
        " 80%|########  | 8/10 [00:35<00:08, 4.45s/it]",
        " 90%|######### | 9/10 [00:40<00:04, 4.54s/it]",
        "100%|##########| 10/10 [00:45<00:00, 4.63s/it]",
        "100%|##########| 10/10 [00:45<00:00, 4.51s/it]",
    ]

    pass_2_lines = [
        "  0%|          | 0/7 [00:00<, ?it/s]",
        " 14%|#4        | 1/7 [00:00<00:02, 2.68it/s]",
        " 29%|##8       | 2/7 [00:00<00:02, 2.44it/s]",
        " 43%|####2     | 3/7 [00:01<00:01, 2.56it/s]",
        " 57%|#####7    | 4/7 [00:01<00:01, 2.64it/s]",
        " 71%|#######1  | 5/7 [00:01<00:00, 2.77it/s]",
        " 86%|########5 | 6/7 [00:02<00:00, 2.93it/s]",
        "100%|##########| 7/7 [00:03<00:00, 3.09it/s]",
        "100%|##########| 7/7 [00:03<00:00, 2.85it/s]",
    ]

    for line in pass_1_lines:
        handler(line)

    for line in pass_2_lines:
        handler(line)

    progress_events = [e for e in events if e.get("event") == "progress"]
    raw_percents = [e.get("percent") for e in progress_events]

    expected_raw = [
        0,
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80,
        90,
        100,
        100,
        0,
        14,
        29,
        43,
        57,
        71,
        86,
        100,
        100,
    ]
    assert raw_percents == expected_raw, f"Expected {expected_raw}, got {raw_percents}"


def test_combine_passes_aggregates_two_passes():
    """combine_passes should aggregate raw percentages from 2 passes into 0-100."""
    raw_percents = [
        0,
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80,
        90,
        100,
        100,
        0,
        14,
        29,
        43,
        57,
        71,
        86,
        100,
        100,
    ]

    events = []

    def capture(event):
        events.append(event)

    callback = combine_passes(capture)

    for percent in raw_percents:
        callback({"event": "progress", "percent": percent})

    progress_events = [e for e in events if e.get("event") == "progress"]
    aggregated_percents = [e.get("percent") for e in progress_events]

    expected_aggregated = [
        0,
        9,
        18,
        27,
        36,
        45,
        54,
        63,
        72,
        81,
        90,
        91,
        92,
        94,
        95,
        97,
        98,
        100,
    ]
    assert aggregated_percents == expected_aggregated, (
        f"Expected {expected_aggregated}, got {aggregated_percents}"
    )


def test_batch_progress_emits_global():
    events = []

    def capture(event):
        events.append(event)

    tracker = batch_progress(2, capture)

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
    assert any(e.get("batch_progress", -1) > 0 for e in events if "batch_progress" in e)
