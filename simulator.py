"""Simulator: generate sample RFID events and group repeated observations."""

from __future__ import annotations

import datetime
from collections import defaultdict

from models import RfidEvent

UTC = datetime.timezone.utc


def generate_sample_events() -> list[RfidEvent]:
    """Return a small deterministic batch of simulated RFID events.

    The batch deliberately includes repeated reads of certain tags so that
    ``find_repeated_reads`` has something to find.
    """
    base = datetime.datetime(2026, 10, 20, 12, 0, 0, tzinfo=UTC)

    def _ts(seconds: int) -> datetime.datetime:
        return base + datetime.timedelta(seconds=seconds)

    return [
        RfidEvent.create("TAG-001", "READER-A", _ts(0)),
        RfidEvent.create("TAG-002", "READER-A", _ts(1)),
        RfidEvent.create("TAG-001", "READER-B", _ts(2)),   # repeated: TAG-001
        RfidEvent.create("TAG-003", "READER-A", _ts(3)),
        RfidEvent.create("TAG-002", "READER-B", _ts(4)),   # repeated: TAG-002
        RfidEvent.create("TAG-001", "READER-A", _ts(5)),   # repeated: TAG-001 (3rd)
        RfidEvent.create("TAG-004", "READER-C", _ts(6)),   # single read
        RfidEvent.create("TAG-002", "READER-A", _ts(7)),   # repeated: TAG-002 (3rd)
    ]


def find_repeated_reads(
    events: list[RfidEvent],
) -> dict[str, list[RfidEvent]]:
    """Group observations by ``tag_id`` and return tags seen more than once.

    * Every observation is preserved — no deduplication.
    * The input *events* list is **never mutated**.
    * Tags with only a single observation are excluded from the result.

    Returns:
        A dict mapping each repeated ``tag_id`` to the list of its
        observations, in the same order they appear in *events*.
    """
    groups: dict[str, list[RfidEvent]] = defaultdict(list)
    for event in events:
        groups[event.tag_id].append(event)

    return {
        tag_id: observations
        for tag_id, observations in groups.items()
        if len(observations) >= 2
    }


# ---------------------------------------------------------------------------
# Quick demo when run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    events = generate_sample_events()

    print("=== All events ===")
    for e in events:
        print(f"  {e.tag_id:8s}  {e.reader_id:10s}  {e.timestamp.isoformat()}")

    repeated = find_repeated_reads(events)

    print(f"\n=== Repeated reads ({len(repeated)} tag(s)) ===")
    for tag_id, observations in repeated.items():
        print(f"  {tag_id}: {len(observations)} observations")
        for obs in observations:
            print(f"    {obs.reader_id:10s}  {obs.timestamp.isoformat()}")
