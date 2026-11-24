"""Phase 2 — Automated Exploratory Data Analysis.

Pandas statistical profiling plus Seaborn/Matplotlib visuals (distributions +
correlation heatmap), returned as base64 PNG strings for the dashboard.
"""
import logging

from app.utils.plotting import fig_to_base64, style_axes, ACCENT_DATA

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)

sns.set_theme(style="darkgrid")

MAX_DISTRIBUTION_CHARTS = 8
TOP_N_CATEGORIES = 8


def compute_numeric_summary(df: pd.DataFrame) -> dict:
    """Pandas-computed mean/median/std/min/max for every numeric column."""
    numeric_df = df.select_dtypes(include=[np.number])
    summary = {}
    for column in numeric_df.columns:
        series = numeric_df[column]
        summary[column] = {
            "mean": float(series.mean()),
            "median": float(series.median()),
            "std": float(series.std(ddof=0)) if series.count() > 1 else 0.0,
            "min": float(series.min()),
            "max": float(series.max()),
            "count": int(series.count()),
        }
    return summary


def compute_categorical_summary(df: pd.DataFrame) -> dict:
    """Cardinality and top values for every categorical/text column."""
    # "str" listed alongside "object": pandas 3.x uses a dedicated str dtype.
    categorical_df = df.select_dtypes(include=["object", "category", "str"])
    summary = {}
    for column in categorical_df.columns:
        value_counts = categorical_df[column].value_counts().head(TOP_N_CATEGORIES)
        summary[column] = {
            "unique_count": int(categorical_df[column].nunique()),
            "top_values": {str(index): int(count) for index, count in value_counts.items()},
        }
    return summary


def generate_distribution_charts(df: pd.DataFrame) -> list[dict]:
    """One Seaborn histogram+KDE per numeric column (capped for a readable dashboard)."""
    numeric_columns = list(df.select_dtypes(include=[np.number]).columns)[:MAX_DISTRIBUTION_CHARTS]
    charts = []

    for column in numeric_columns:
        fig, ax = plt.subplots(figsize=(5, 3.2))
        sns.histplot(df[column].dropna(), kde=True, ax=ax, color=ACCENT_DATA, edgecolor="none")
        ax.set_title(column, fontsize=11)
        style_axes(ax)
        charts.append({
            "column": column,
            "chart_type": "distribution",
            "image_base64": fig_to_base64(fig),
        })

    return charts


def generate_correlation_heatmap(df: pd.DataFrame) -> str | None:
    """A Seaborn heatmap of pairwise correlation across all numeric columns."""
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        return None

    correlation = numeric_df.corr(numeric_only=True)
    side = max(4.5, len(correlation.columns) * 0.65)
    fig, ax = plt.subplots(figsize=(side, side * 0.85))
    sns.heatmap(
        correlation,
        annot=True,
        fmt=".2f",
        cmap="mako",
        ax=ax,
        linewidths=0.5,
        linecolor="#2E3644",
        cbar_kws={"label": "Correlation"},
    )
    ax.set_title("Correlation Heatmap", fontsize=12)
    style_axes(ax)
    return fig_to_base64(fig)


def run_eda(df: pd.DataFrame) -> dict:
    """Entry point used by GET /api/eda/{session_id} — runs the full Phase 2 pipeline."""
    return {
        "numeric_summary": compute_numeric_summary(df),
        "categorical_summary": compute_categorical_summary(df),
        "distribution_charts": generate_distribution_charts(df),
        "correlation_heatmap": generate_correlation_heatmap(df),
    }
