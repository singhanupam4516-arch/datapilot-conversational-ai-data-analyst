"""Phase 3 — Context Chunking.

Turns a cleaned DataFrame's schema and summary statistics into short,
descriptive text chunks suitable for embedding — one per column, plus one
dataset-overview chunk — so retrieval can surface just the relevant columns.
"""
import pandas as pd

TOP_N_CATEGORIES_IN_CHUNK = 5


def _describe_numeric_column(name: str, series: pd.Series) -> str:
    return (
        f"Column '{name}' is numeric ({series.dtype}). "
        f"It ranges from {series.min():.2f} to {series.max():.2f}, with a mean of "
        f"{series.mean():.2f}, a median of {series.median():.2f}, and a standard "
        f"deviation of {series.std(ddof=0):.2f}."
    )


def _describe_categorical_column(name: str, series: pd.Series) -> str:
    top_values = series.value_counts().head(TOP_N_CATEGORIES_IN_CHUNK)
    top_description = ", ".join(f"'{index}' ({count} rows)" for index, count in top_values.items())
    return (
        f"Column '{name}' is categorical/text with {series.nunique()} unique values. "
        f"Most common: {top_description}."
    )


def _describe_datetime_column(name: str, series: pd.Series) -> str:
    return f"Column '{name}' is a date/time field, ranging from {series.min()} to {series.max()}."


def build_schema_chunks(df: pd.DataFrame) -> list[dict]:
    """Returns [{chunk_type, column_name, text}, ...] ready to be embedded."""
    chunks: list[dict] = [{
        "chunk_type": "dataset_overview",
        "column_name": None,
        "text": (
            f"This dataset has {df.shape[0]} rows and {df.shape[1]} columns. "
            f"The columns are: {', '.join(df.columns)}."
        ),
    }]

    for column in df.columns:
        series = df[column]
        if pd.api.types.is_numeric_dtype(series):
            text = _describe_numeric_column(column, series)
        elif pd.api.types.is_datetime64_any_dtype(series):
            text = _describe_datetime_column(column, series)
        else:
            text = _describe_categorical_column(column, series)
        chunks.append({"chunk_type": "column_profile", "column_name": column, "text": text})

    return chunks
