from __future__ import annotations

import json
import traceback
from dataclasses import asdict, is_dataclass
from datetime import date, datetime, time, timezone
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID


TRACE_ROOT = Path(__file__).resolve().parents[2] / "debug_traces"
TRACE_FILE_NAME = "analyze_trace.log"


def _serialize_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, (UUID, datetime, date, time, Decimal, Path)):
        return str(value)

    if isinstance(value, Enum):
        return value.value

    if is_dataclass(value):
        return _serialize_value(asdict(value))

    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        return _serialize_value(model_dump())

    dict_method = getattr(value, "dict", None)
    if callable(dict_method):
        return _serialize_value(dict_method())

    if isinstance(value, dict):
        return {
            str(key): _serialize_value(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set, frozenset)):
        return [_serialize_value(item) for item in value]

    if hasattr(value, "_asdict"):
        return _serialize_value(value._asdict())

    if hasattr(value, "__dict__"):
        public_attrs = {
            key: item
            for key, item in vars(value).items()
            if not key.startswith("_")
        }
        if public_attrs:
            return _serialize_value(public_attrs)

    return repr(value)


class DebugTrace:
    def __init__(self, trace_name: str, context: dict[str, Any] | None = None):
        TRACE_ROOT.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        self.started_at = datetime.now(timezone.utc)
        self.trace_name = trace_name
        self.request_id = f"{trace_name}_{timestamp}"
        self.path = TRACE_ROOT / TRACE_FILE_NAME
        self.context = _serialize_value(context or {})
        self._write_header()

    def _write_header(self) -> None:
        header = {
            "request_id": self.request_id,
            "trace_name": self.trace_name,
            "trace_started_at": self.started_at.isoformat(),
            "context": self.context,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write("# Debug Trace\n")
            handle.write(json.dumps(header, indent=2, ensure_ascii=False))
            handle.write("\n\n")

    def log(
        self,
        step: str,
        *,
        summary: str | None = None,
        payload: Any = None,
    ) -> None:
        now = datetime.now(timezone.utc)
        entry = {
            "timestamp": now.isoformat(),
            "elapsed_ms": round((now - self.started_at).total_seconds() * 1000, 3),
            "step": step,
            "summary": summary,
            "payload": _serialize_value(payload),
        }

        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(f"[{entry['timestamp']}] {step} ({self.request_id})\n")
            if summary:
                handle.write(f"summary: {summary}\n")
            handle.write("payload:\n")
            handle.write(json.dumps(entry["payload"], indent=2, ensure_ascii=False))
            handle.write("\n")
            handle.write(f"elapsed_ms: {entry['elapsed_ms']}\n\n")

    def log_exception(self, step: str, exc: BaseException) -> None:
        self.log(
            step,
            summary=f"{type(exc).__name__}: {exc}",
            payload={
                "exception_type": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc(),
            },
        )
