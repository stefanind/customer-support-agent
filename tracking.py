import json
from contextlib import contextmanager
from pathlib import Path
from time import perf_counter


RUNS_FILE = Path(__file__).parent / "data" / "runs.jsonl"


@contextmanager
def track_step(timings_ms: dict[str, float], name: str):
    """Measure one pipeline step in milliseconds."""

    started = perf_counter()
    try:
        yield
    finally:
        timings_ms[name] = round((perf_counter() - started) * 1000, 2)


def save_run(run: dict, path: Path = RUNS_FILE) -> None:
    """Append one run record to a local JSONL file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(run, ensure_ascii=False) + "\n")
