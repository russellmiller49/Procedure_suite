import time
from typing import Any, Callable, Iterable, List

class LatencyTracker:
    def __init__(self):
        self.timings: List[float] = []

    def track(self, duration: float) -> None:
        self.timings.append(duration)

    @property
    def cold_start_ms(self) -> float:
        return self.timings[0] * 1000 if self.timings else 0.0

    def mean_ms(self) -> float:
        return (sum(self.timings) / len(self.timings)) * 1000 if self.timings else 0.0

    def p95_ms(self) -> float:
        if not self.timings:
            return 0.0
        sorted_times = sorted(self.timings)
        index = int(0.95 * len(sorted_times)) - 1
        index = max(index, 0)
        return sorted_times[index] * 1000

    def max_ms(self) -> float:
        return max(self.timings) * 1000 if self.timings else 0.0

def timed_run(notes: Iterable[Any], process_note: Callable[[Any], Any]):
    tracker = LatencyTracker()
    results = []
    for note in notes:
        start = time.perf_counter()
        result = process_note(note)
        duration = time.perf_counter() - start
        tracker.track(duration)
        results.append(result)
    metrics = {
        "cold_start_ms": tracker.cold_start_ms,
        "p95_ms": tracker.p95_ms(),
        "n": len(tracker.timings),
        "mean_ms": tracker.mean_ms(),
        "max_ms": tracker.max_ms(),
    }
    import json
    print(json.dumps({"latency_metrics": metrics}))
    return results
