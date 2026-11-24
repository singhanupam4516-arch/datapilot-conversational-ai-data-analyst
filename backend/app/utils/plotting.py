"""Shared Matplotlib setup and the figure -> base64 PNG helper.

Imported before any other module touches `matplotlib.pyplot` so the headless
"Agg" backend is configured exactly once for the whole process.
"""
import base64
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (must be imported after matplotlib.use)

FIGURE_FACECOLOR = "#1C222B"
AXES_FACECOLOR = "#1C222B"
TEXT_COLOR = "#EDEFF2"
MUTED_TEXT_COLOR = "#8B94A3"
GRID_COLOR = "#2E3644"
ACCENT_DATA = "#4FB8B0"
ACCENT_INSIGHT = "#E0A94C"


def style_axes(ax) -> None:
    """Apply the shared dark chart theme to a single Matplotlib Axes."""
    ax.set_facecolor(AXES_FACECOLOR)
    ax.title.set_color(TEXT_COLOR)
    ax.xaxis.label.set_color(MUTED_TEXT_COLOR)
    ax.yaxis.label.set_color(MUTED_TEXT_COLOR)
    ax.tick_params(colors=MUTED_TEXT_COLOR)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)


def fig_to_base64(fig) -> str:
    """Render a Matplotlib Figure to a base64-encoded PNG string."""
    buffer = io.BytesIO()
    fig.patch.set_facecolor(FIGURE_FACECOLOR)
    fig.savefig(buffer, format="png", bbox_inches="tight", dpi=110, facecolor=FIGURE_FACECOLOR)
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")
