"""Phase 1 — Data Ingestion & Cleaning.

Parses an uploaded CSV/XLSX into a Pandas DataFrame, then applies
NumPy-backed null imputation and dtype standardization so every later phase
can assume a clean, analysis-ready DataFrame.
"""
import io
import logging
from datetime import datetime, timezone

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = (".csv", ".xlsx", ".xls")
DATE_PARSE_SUCCESS_THRESHOLD = 0.9
NUMERIC_COERCE_SUCCESS_THRESHOLD = 0.9


class UnsupportedFileTypeError(Exception):
    """Raised when the uploaded file isn't a .csv, .xlsx, or .xls."""


def load_dataframe(filename: str, file_bytes: bytes) -> pd.DataFrame:
    """Parse raw upload bytes into a DataFrame based on the file extension."""
    lower_name = filename.lower()
    buffer = io.BytesIO(file_bytes)

    if lower_name.endswith(".csv"):
        df = pd.read_csv(buffer)
    elif lower_name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(buffer)
    else:
        raise UnsupportedFileTypeError(
            f"'{filename}' is not a supported file type. Upload a .csv, .xlsx, or .xls file."
        )

    if df.empty:
        raise ValueError("The uploaded file has no rows.")

    df.columns = [str(col).strip() for col in df.columns]
    return df


def _try_parse_dates(series: pd.Series) -> pd.Series:
    """Convert a text column to datetime64 only if it's clearly date-like (>=90% parse)."""
    non_null_count = series.notna().sum()
    if non_null_count == 0:
        return series

    # format="mixed" parses each value independently (real-world CSVs aren't uniform).
    parsed = pd.to_datetime(series, errors="coerce", format="mixed")
    success_ratio = parsed.notna().sum() / non_null_count
    return parsed if success_ratio >= DATE_PARSE_SUCCESS_THRESHOLD else series


def _try_coerce_numeric(series: pd.Series) -> pd.Series:
    """Convert a text column (e.g. '1,200', '$45') to numeric if it's clearly numeric.

    Skips coercion for values with a meaningful leading zero (e.g. zip code
    '02134') — converting those would silently corrupt the identifier.
    """
    non_null_count = series.notna().sum()
    if non_null_count == 0:
        return series

    string_values = series.astype(str).str.strip()
    if string_values.str.match(r"^0\d").fillna(False).any():
        return series

    cleaned = string_values.str.replace(",", "", regex=False).str.replace("$", "", regex=False)
    coerced = pd.to_numeric(cleaned, errors="coerce")
    success_ratio = coerced.notna().sum() / non_null_count
    return coerced if success_ratio >= NUMERIC_COERCE_SUCCESS_THRESHOLD else series


def _standardize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce text columns to numeric or datetime where the data clearly supports it.

    Checks "already numeric or datetime?" rather than "dtype == object?" because
    pandas 3.x uses a dedicated `str` dtype for text, which an `object` check skips.
    """
    for column in df.columns:
        series = df[column]
        if pd.api.types.is_numeric_dtype(series) or pd.api.types.is_datetime64_any_dtype(series):
            continue
        numeric_version = _try_coerce_numeric(series)
        if pd.api.types.is_numeric_dtype(numeric_version):
            df[column] = numeric_version
        else:
            df[column] = _try_parse_dates(series)
    return df


def _impute_nulls(df: pd.DataFrame) -> pd.DataFrame:
    for column in df.columns:
        series = df[column]
        if series.isna().sum() == 0:
            continue

        if pd.api.types.is_numeric_dtype(series):
            median_value = series.median()
            df[column] = series.fillna(0.0 if np.isnan(median_value) else median_value)
        elif pd.api.types.is_datetime64_any_dtype(series):
            df[column] = series.ffill().bfill()
        else:
            mode_series = series.mode(dropna=True)
            fill_value = mode_series.iloc[0] if not mode_series.empty else "Unknown"
            df[column] = series.fillna(fill_value)
    return df


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full Phase 1 cleaning pipeline: dtype standardization then imputation."""
    cleaned = df.copy()
    cleaned = _standardize_dtypes(cleaned)
    cleaned = _impute_nulls(cleaned)
    return cleaned


def build_upload_summary(df: pd.DataFrame, filename: str, session_id: str) -> dict:
    """Metadata document persisted to MongoDB Atlas's `uploads` collection (Phase 1)."""
    return {
        "session_id": session_id,
        "filename": filename,
        "row_count": int(df.shape[0]),
        "column_count": int(df.shape[1]),
        "columns": [{"name": col, "dtype": str(df[col].dtype)} for col in df.columns],
        "uploaded_at": datetime.now(timezone.utc),
    }
