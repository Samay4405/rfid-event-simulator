"""Tests for models.RfidEvent, simulator.find_repeated_reads, and
simulator.generate_sample_events.

Run with:  python -m unittest test_simulator -v
"""

from __future__ import annotations

import copy
import datetime
import unittest

from models import RfidEvent
from simulator import find_repeated_reads, generate_sample_events

UTC = datetime.timezone.utc


# ── helpers ──────────────────────────────────────────────────────────────────

def _utc_now() -> datetime.datetime:
    """Return the current UTC-aware datetime."""
    return datetime.datetime.now(tz=UTC)


# ── RfidEvent.create – valid inputs ─────────────────────────────────────────

class TestRfidEventValid(unittest.TestCase):
    """Happy-path creation and UTC normalisation."""

    def test_create_with_utc_timestamp(self) -> None:
        ts = datetime.datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
        event = RfidEvent.create("TAG-1", "READER-A", ts)

        self.assertEqual(event.tag_id, "TAG-1")
        self.assertEqual(event.reader_id, "READER-A")
        self.assertEqual(event.timestamp, ts)
        self.assertEqual(event.timestamp.tzinfo, UTC)

    def test_create_normalises_non_utc_to_utc(self) -> None:
        ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        ts_ist = datetime.datetime(2026, 1, 1, 17, 30, 0, tzinfo=ist)

        event = RfidEvent.create("TAG-1", "READER-A", ts_ist)

        # 17:30 IST (+05:30) → 12:00 UTC
        expected_utc = datetime.datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
        self.assertEqual(event.timestamp, expected_utc)
        self.assertEqual(event.timestamp.tzinfo, UTC)


# ── RfidEvent.create – invalid inputs ──────────────────────────────────────

class TestRfidEventTypeErrors(unittest.TestCase):
    """Wrong argument types must raise TypeError."""

    def test_tag_id_not_str(self) -> None:
        with self.assertRaises(TypeError) as ctx:
            RfidEvent.create(123, "READER-A", _utc_now())
        self.assertIn("tag_id must be a str", str(ctx.exception))

    def test_reader_id_not_str(self) -> None:
        with self.assertRaises(TypeError) as ctx:
            RfidEvent.create("TAG-1", None, _utc_now())
        self.assertIn("reader_id must be a str", str(ctx.exception))

    def test_timestamp_not_datetime(self) -> None:
        with self.assertRaises(TypeError) as ctx:
            RfidEvent.create("TAG-1", "READER-A", "2026-01-01T00:00:00Z")
        self.assertIn("timestamp must be a datetime", str(ctx.exception))


class TestRfidEventValueErrors(unittest.TestCase):
    """Right types but invalid values must raise ValueError."""

    def test_empty_tag_id(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            RfidEvent.create("", "READER-A", _utc_now())
        self.assertIn("tag_id must not be empty", str(ctx.exception))

    def test_whitespace_tag_id(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            RfidEvent.create("   ", "READER-A", _utc_now())
        self.assertIn("tag_id must not be empty", str(ctx.exception))

    def test_empty_reader_id(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            RfidEvent.create("TAG-1", "", _utc_now())
        self.assertIn("reader_id must not be empty", str(ctx.exception))

    def test_naive_timestamp(self) -> None:
        naive = datetime.datetime(2026, 1, 1, 12, 0, 0)
        with self.assertRaises(ValueError) as ctx:
            RfidEvent.create("TAG-1", "READER-A", naive)
        self.assertIn("timestamp must be timezone-aware", str(ctx.exception))


# ── find_repeated_reads ─────────────────────────────────────────────────────

class TestFindRepeatedReads(unittest.TestCase):
    """Grouping semantics, preservation, and immutability."""

    def setUp(self) -> None:
        base = datetime.datetime(2026, 1, 1, tzinfo=UTC)
        self.events = [
            RfidEvent.create("TAG-A", "R1", base + datetime.timedelta(seconds=0)),
            RfidEvent.create("TAG-B", "R1", base + datetime.timedelta(seconds=1)),
            RfidEvent.create("TAG-A", "R2", base + datetime.timedelta(seconds=2)),
            RfidEvent.create("TAG-C", "R1", base + datetime.timedelta(seconds=3)),
            RfidEvent.create("TAG-A", "R1", base + datetime.timedelta(seconds=4)),
        ]
        # TAG-A appears 3 times, TAG-B once, TAG-C once.

    def test_only_repeated_tags_in_result(self) -> None:
        result = find_repeated_reads(self.events)
        self.assertEqual(set(result.keys()), {"TAG-A"})

    def test_single_read_tags_excluded(self) -> None:
        result = find_repeated_reads(self.events)
        self.assertNotIn("TAG-B", result)
        self.assertNotIn("TAG-C", result)

    def test_all_observations_preserved(self) -> None:
        result = find_repeated_reads(self.events)
        self.assertEqual(len(result["TAG-A"]), 3)

    def test_observation_order_matches_input(self) -> None:
        result = find_repeated_reads(self.events)
        tag_a = result["TAG-A"]
        self.assertEqual(tag_a[0].reader_id, "R1")
        self.assertEqual(tag_a[1].reader_id, "R2")
        self.assertEqual(tag_a[2].reader_id, "R1")

    def test_input_list_not_mutated(self) -> None:
        original_length = len(self.events)
        snapshot = list(self.events)  # shallow copy of the list

        find_repeated_reads(self.events)

        self.assertEqual(len(self.events), original_length)
        for original, after in zip(snapshot, self.events):
            self.assertIs(original, after)

    def test_empty_list(self) -> None:
        self.assertEqual(find_repeated_reads([]), {})


# ── generate_sample_events ──────────────────────────────────────────────────

class TestGenerateSampleEvents(unittest.TestCase):
    """Basic properties of the sample batch."""

    def test_returns_non_empty_list_of_events(self) -> None:
        events = generate_sample_events()
        self.assertGreater(len(events), 0)
        for e in events:
            self.assertIsInstance(e, RfidEvent)

    def test_contains_repeated_tags(self) -> None:
        events = generate_sample_events()
        repeated = find_repeated_reads(events)
        self.assertGreater(len(repeated), 0)


if __name__ == "__main__":
    unittest.main()
