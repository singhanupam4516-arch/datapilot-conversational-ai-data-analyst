"""In-memory registry mapping session_id -> cleaned Pandas DataFrame.

Deliberately simple for a single-worker demo deployment; a production system
would use a shared cache (Redis, or per-session Parquet referenced from MongoDB).
"""
import pandas as pd

_session_frames: dict[str, pd.DataFrame] = {}


def save_dataframe(session_id: str, df: pd.DataFrame) -> None:
    _session_frames[session_id] = df


def get_dataframe(session_id: str) -> pd.DataFrame | None:
    return _session_frames.get(session_id)


def has_session(session_id: str) -> bool:
    return session_id in _session_frames


def drop_session(session_id: str) -> None:
    _session_frames.pop(session_id, None)


def active_session_count() -> int:
    return len(_session_frames)
