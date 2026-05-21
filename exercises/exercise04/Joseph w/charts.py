"""Charts for the DC dog park equity analysis.

The functions in this module accept already-cleaned pandas DataFrames so they
can be reused from a notebook, a script, or a future web map workflow.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


WARD_ORDER = [f"Ward {ward}" for ward in range(1, 9)]
SUPPLY_COLOR = "#2374ab"
NEED_COLOR = "#db7c26"
ACCENT_COLOR = "#3f7d20"
GRID_COLOR = "#d9dee3"


def _prepare_output_dir(output_dir: Path | str) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def _style_axis(ax, title: str, xlabel: str = "", ylabel: str = "") -> None:
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_dog_parks_by_ward(ward_summary: pd.DataFrame, output_dir: Path | str) -> Path:
    """Save a bar chart showing official dog park count by ward."""
    output_path = _prepare_output_dir(output_dir)
    chart_data = (
        ward_summary.set_index("ward")
        .reindex(WARD_ORDER)
        .reset_index()
        .fillna({"dog_park_count": 0})
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(chart_data["ward"], chart_data["dog_park_count"], color=SUPPLY_COLOR)
    _style_axis(
        ax,
        "Official dog parks are unevenly distributed by ward",
        ylabel="Dog park count",
    )
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()

    chart_file = output_path / "dog_parks_by_ward.png"
    fig.savefig(chart_file, dpi=200)
    plt.close(fig)
    return chart_file


def plot_dog_park_area_by_ward(
    ward_summary: pd.DataFrame, output_dir: Path | str
) -> Path:
    """Save a bar chart showing dog park square footage by ward."""
    output_path = _prepare_output_dir(output_dir)
    chart_data = (
        ward_summary.set_index("ward")
        .reindex(WARD_ORDER)
        .reset_index()
        .fillna({"dog_park_sqft": 0})
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(chart_data["ward"], chart_data["dog_park_sqft"], color=ACCENT_COLOR)
    _style_axis(
        ax,
        "Dog park acreage is also concentrated",
        ylabel="Total official dog park square feet",
    )
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()

    chart_file = output_path / "dog_park_area_by_ward.png"
    fig.savefig(chart_file, dpi=200)
    plt.close(fig)
    return chart_file


def plot_supply_need_scatter(
    ward_summary: pd.DataFrame, output_dir: Path | str
) -> Path | None:
    """Save a supply-versus-need chart when need indicators are available."""
    required = {"dog_park_count", "affordable_units", "ward"}
    if not required.issubset(ward_summary.columns):
        return None

    output_path = _prepare_output_dir(output_dir)
    chart_data = ward_summary.copy()
    chart_data["affordable_units"] = chart_data["affordable_units"].fillna(0)

    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.scatter(
        chart_data["affordable_units"],
        chart_data["dog_park_count"],
        s=140,
        color=NEED_COLOR,
        edgecolor="#222222",
        linewidth=0.7,
    )
    for _, row in chart_data.iterrows():
        ax.annotate(
            row["ward"].replace("Ward ", "W"),
            (row["affordable_units"], row["dog_park_count"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=9,
        )

    _style_axis(
        ax,
        "Dog park supply compared with a housing stress proxy",
        xlabel="Affordable housing units in local file",
        ylabel="Official dog park count",
    )
    fig.tight_layout()

    chart_file = output_path / "dog_park_supply_vs_affordable_housing.png"
    fig.savefig(chart_file, dpi=200)
    plt.close(fig)
    return chart_file


def plot_neighborhood_single_households(
    one_person_households: pd.DataFrame, output_dir: Path | str, top_n: int = 12
) -> Path | None:
    """Save a chart of neighborhoods with high one-person household shares."""
    if one_person_households.empty or "OnePerson_Pct" not in one_person_households:
        return None

    output_path = _prepare_output_dir(output_dir)
    chart_data = one_person_households.copy()
    chart_data["one_person_pct_num"] = (
        chart_data["OnePerson_Pct"].astype(str).str.replace("%", "", regex=False)
    )
    chart_data["one_person_pct_num"] = pd.to_numeric(
        chart_data["one_person_pct_num"], errors="coerce"
    )
    chart_data = chart_data.dropna(subset=["one_person_pct_num"]).head(top_n)
    if chart_data.empty:
        return None

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(
        chart_data["Neighborhood"][::-1],
        chart_data["one_person_pct_num"][::-1],
        color=NEED_COLOR,
    )
    _style_axis(
        ax,
        "Neighborhoods with high shares of one-person households",
        xlabel="One-person households (%)",
    )
    fig.tight_layout()

    chart_file = output_path / "one_person_household_neighborhoods.png"
    fig.savefig(chart_file, dpi=200)
    plt.close(fig)
    return chart_file


def write_findings_markdown(
    findings: dict[str, object], output_dir: Path | str
) -> Path:
    """Write a concise Markdown evidence memo for the project notebook."""
    output_path = _prepare_output_dir(output_dir)
    memo_file = output_path / "dog_park_key_findings.md"

    lines = [
        "# DC Dog Park Equity: Key Findings",
        "",
        "## Claim",
        (
            "Dog parks are an emerging form of neighborhood green infrastructure, "
            "but current placement should be tested against who has access to "
            "private outdoor space, who rents, and who lives in denser households."
        ),
        "",
        "## Evidence Generated by This Framework",
    ]
    for item in findings.get("bullets", []):
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Next Data Additions",
            (
                "- Add ward or tract geometries from Open Data DC, then spatially "
                "join dog parks, parks, transit, schools, hospitals, 311 requests, "
                "tree canopy, and ACS indicators."
            ),
            (
                "- Replace citywide renter and age summaries with tract-level ACS "
                "B25003, B25014, B01001, B11001, B19013, B17001, and B03002."
            ),
        ]
    )

    memo_file.write_text("\n".join(lines), encoding="utf-8")
    return memo_file
