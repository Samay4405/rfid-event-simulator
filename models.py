"""Data model for simulated RFID events."""

from __future__ import annotations

import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class RfidEvent:
    """A single simulated RFID read observation.

    Attributes:
        tag_id:    Non-empty identifier for the simulated tag.
        reader_id: Non-empty identifier for the simulated reader.
        timestamp: Timezone-aware UTC datetime of the observation.
    """

    tag_id: str
    reader_id: str
    timestamp: datetime.datetime

    @classmethod
    def create(
        cls,
        tag_id: object,
        reader_id: object,
        timestamp: object,
    ) -> RfidEvent:
        """Validate inputs and return a new ``RfidEvent``.

        Raises:
            TypeError:  If any argument has the wrong type.
            ValueError: If a string is empty/whitespace or the datetime is naive.
        """
        # --- type checks (run first) ---
        if not isinstance(tag_id, str):
            raise TypeError("tag_id must be a str")
        if not isinstance(reader_id, str):
            raise TypeError("reader_id must be a str")
        if not isinstance(timestamp, datetime.datetime):
            raise TypeError("timestamp must be a datetime")

        # --- value checks ---
        if not tag_id.strip():
            raise ValueError("tag_id must not be empty")
        if not reader_id.strip():
            raise ValueError("reader_id must not be empty")
        if timestamp.tzinfo is None or timestamp.tzinfo.utcoffset(timestamp) is None:
            raise ValueError("timestamp must be timezone-aware")

        # Normalise to UTC so every stored timestamp uses the same zone.
        utc_timestamp = timestamp.astimezone(datetime.timezone.utc)

        return cls(tag_id=tag_id, reader_id=reader_id, timestamp=utc_timestamp)
