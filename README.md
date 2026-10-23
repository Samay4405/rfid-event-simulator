# RFID Event Simulator

A minimal Python learning project that simulates RFID tag-read events.
No real hardware, databases, or external dependencies — standard library only.

## Quick start

```bash
# Run the demo
python simulator.py

# Run the tests
python -m unittest test_simulator -v
```

## Project structure

| File | Purpose |
|---|---|
| `models.py` | `RfidEvent` dataclass with validated factory method |
| `simulator.py` | Event generation and repeated-read grouping |
| `test_simulator.py` | Automated tests (unittest) |

## How it works

1. `generate_sample_events()` creates a small batch of `RfidEvent` objects.
2. Each event is validated via `RfidEvent.create()` — wrong types raise
   `TypeError`, invalid values raise `ValueError`, and timezone-aware
   timestamps are normalised to UTC.
3. `find_repeated_reads(events)` groups observations by `tag_id` and returns
   only tags observed more than once. The original list is never mutated.
