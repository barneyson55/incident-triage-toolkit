from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class LogEvent:
    timestamp: datetime
    level: str
    component: str
    message: str
    correlation_id: str | None
    raw: str
    source_timestamp: str | None = None
    source_offset: str | None = None
    source_path: str | None = None
    line_number: int | None = None
    source_order: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "source_timestamp": self.source_timestamp,
            "source_offset": self.source_offset,
            "source_path": self.source_path,
            "line_number": self.line_number,
            "level": self.level,
            "component": self.component,
            "message": self.message,
            "correlation_id": self.correlation_id,
        }
