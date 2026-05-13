"""Main tract-level analysis for the Ride On Reimagined final project.

This script builds the analysis for the final project. The main steps are:

1. Convert stop-level GTFS service metrics into tract-level service measures.
2. Use a 0.25-mile stop catchment to approximate nearby scheduled service.
3. Join tract service measures to the ACS Transit Need Index.
4. Compare service changes across transit need quartiles.
5. Build and save tables and figures that can be used to support the project.

The analysis measures scheduled service supply near tracts, not actual rider experience or destination accessibility.
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.patches import Patch, Rectangle
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

try:
    import contextily as cx
except ImportError:  # pragma: no cover - maps still render without a tile basemap.
    cx = None


matplotlib.use("Agg")


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_GTFS_DIR = PROCESSED_DIR / "gtfs"
PROCESSED_ACS_DIR = PROCESSED_DIR / "acs"
PROCESSED_GEOGRAPHY_DIR = PROCESSED_DIR / "geography"
FINAL_OUTPUT_DIR = PROCESSED_DIR / "final_analysis"
FINAL_FIGURE_DIR = PROJECT_DIR / "figures" / "final_analysis"


# Maryland StatePlane meters. This projected CRS makes distance buffers sensible.
ANALYSIS_CRS = "EPSG:26985"

# Web Mercator is used only for cartographic basemap display.
WEB_MERCATOR_CRS = "EPSG:3857"

# A quarter mile is a common simple proxy for walking access to bus service.
CATCHMENT_MILES = 0.25
CATCHMENT_METERS = CATCHMENT_MILES * 1609.344


SERVICE_SUM_COLUMNS = [
    "weekday_total_trips",
    "weekend_total_trips",
    "weekday_peak_trips_per_hour",
]

SERVICE_MEAN_COLUMNS = [
    "weekday_span_hours",
    "weekend_span_hours",
]

CHANGE_METRICS = [
    "weekday_total_trips_accessible",
    "weekend_total_trips_accessible",
    "weekday_peak_trips_per_hour_accessible",
    "mean_weekday_span_hours",
    "mean_weekend_span_hours",
]


NEED_QUARTILE_ORDER = ["low", "moderate_low", "moderate_high", "high"]
NEED_QUARTILE_LABELS = {
    "low": "Low",
    "moderate_low": "Moderate Low",
    "moderate_high": "Moderate High",
    "high": "High",
}
FEED_LABELS = {
    "2024_january": "Jan 2024",
    "2024_may": "May 2024",
    "2024_september": "Sep 2024",
    "2025_january": "Jan 2025",
    "2025_june": "Jun 2025",
    "2025_september": "Sep 2025",
    "2026_may_current": "May 2026",
}

NEED_COLORS = {
    "low": "#2C7BB6",
    "moderate_low": "#ABD9E9",
    "moderate_high": "#FDAE61",
    "high": "#D7191C",
}

CHANGE_COLORS = {
    "Large loss": "#B2182B",
    "Moderate loss": "#EF8A62",
    "Little/no change": "#F7F7F7",
    "Moderate gain": "#67A9CF",
    "Large gain": "#2166AC",
}

CHANGE_FILL_COLORS = {
    "Large loss": to_rgba("#B2182B", 0.86),
    "Moderate loss": to_rgba("#EF8A62", 0.78),
    "Little/no change": to_rgba("#FFFFFF", 0.22),
    "Moderate gain": to_rgba("#67A9CF", 0.78),
    "Large gain": to_rgba("#2166AC", 0.86),
}

MILES_TO_METERS = 1609.344


def ensure_output_dirs() -> None:
    """Create folders for final analysis tables and figures."""

    FINAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def create_map_layout(
    title: str,
    subtitle: str,
    source: str,
) -> tuple[plt.Figure, plt.Axes, plt.Axes]:
    """Create an 11-by-8.5 map layout with a neatline and separate legend panel."""

    fig = plt.figure(figsize=(11, 8))
    fig.patch.set_facecolor("white")
    fig.add_artist(
        Rectangle(
            (0.015, 0.015),
            0.97,
            0.97,
            transform=fig.transFigure,
            fill=False,
            edgecolor="#222222",
            linewidth=1.1,
            zorder=100,
        )
    )

    grid = fig.add_gridspec(
        nrows=3,
        ncols=2,
        height_ratios=[0.10, 0.84, 0.06],
        width_ratios=[0.78, 0.22],
        left=0.045,
        right=0.955,
        top=0.955,
        bottom=0.045,
        wspace=0.035,
        hspace=0.015,
    )

    title_ax = fig.add_subplot(grid[0, :])
    title_ax.set_axis_off()
    title_ax.text(
        0,
        0.72,
        title,
        ha="left",
        va="center",
        fontsize=16,
        fontweight="bold",
        transform=title_ax.transAxes,
    )
    title_ax.text(
        0,
        0.28,
        subtitle,
        ha="left",
        va="center",
        fontsize=9.5,
        color="#333333",
        transform=title_ax.transAxes,
    )

    map_ax = fig.add_subplot(grid[1, 0])
    legend_ax = fig.add_subplot(grid[1, 1])
    source_ax = fig.add_subplot(grid[2, :])

    legend_ax.set_axis_off()
    source_ax.set_axis_off()
    source_ax.text(
        0,
        0.60,
        source,
        ha="left",
        va="center",
        fontsize=7.8,
        color="#444444",
        transform=source_ax.transAxes,
    )

    for layout_ax in [map_ax, legend_ax]:
        layout_ax.add_patch(
            Rectangle(
                (0, 0),
                1,
                1,
                transform=layout_ax.transAxes,
                fill=False,
                edgecolor="#333333",
                linewidth=0.9,
                zorder=30,
            )
        )

    return fig, map_ax, legend_ax


def add_light_gray_basemap(ax: plt.Axes) -> None:
    """Add a light gray basemap if tiles are reachable; otherwise use a canvas fallback."""

    ax.set_facecolor("#E9ECEF")
    if cx is None:
        return

    for provider in [cx.providers.Esri.WorldGrayCanvas, cx.providers.CartoDB.Positron]:
        try:
            cx.add_basemap(
                ax,
                source=provider,
                attribution=False,
                reset_extent=False,
                alpha=1.0,
                zoom=10,
            )
            return
        except Exception:
            continue

    ax.set_facecolor("#E9ECEF")


def set_map_extent(ax: plt.Axes, map_data: gpd.GeoDataFrame, pad_ratio: float = 0.015) -> None:
    """Set a padded extent so the county does not crowd the layout edges."""

    x_min, y_min, x_max, y_max = map_data.total_bounds
    x_pad = (x_max - x_min) * pad_ratio
    y_pad = (y_max - y_min) * pad_ratio
    ax.set_xlim(x_min - x_pad, x_max + x_pad)
    ax.set_ylim(y_min - y_pad, y_max + y_pad)


def add_north_arrow(ax: plt.Axes) -> None:
    """Place a compact north arrow inside the map frame."""

    ax.annotate(
        "N",
        xy=(0.92, 0.88),
        xytext=(0.92, 0.78),
        xycoords="axes fraction",
        arrowprops={"arrowstyle": "-|>", "lw": 1.6, "color": "black"},
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        bbox={"facecolor": "white", "edgecolor": "#333333", "boxstyle": "square,pad=0.25"},
        zorder=35,
    )


def add_scale_bar(ax: plt.Axes, scale_miles: int = 5) -> None:
    """Place a simple scale bar inside the map frame."""

    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    scale_length = scale_miles * MILES_TO_METERS
    x_start = x_min + (x_max - x_min) * 0.06
    y_start = y_min + (y_max - y_min) * 0.06

    ax.plot(
        [x_start, x_start + scale_length],
        [y_start, y_start],
        color="black",
        linewidth=3,
        solid_capstyle="butt",
    )
    ax.text(
        x_start + scale_length / 2,
        y_start + (y_max - y_min) * 0.015,
        f"{scale_miles} miles",
        ha="center",
        va="bottom",
        fontsize=9,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 1.5},
        zorder=35,
    )


def finish_map_axis(ax: plt.Axes) -> None:
    """Hide axes while preserving the cartographic frame."""

    ax.set_axis_off()
    ax.add_patch(
        Rectangle(
            (0, 0),
            1,
            1,
            transform=ax.transAxes,
            fill=False,
            edgecolor="#333333",
            linewidth=0.9,
            zorder=40,
        )
    )


def draw_legend_panel(
    legend_ax: plt.Axes,
    handles: list[Patch],
    title: str,
    note: str | None = None,
) -> None:
    """Draw a dedicated legend panel so legends do not cover mapped tracts."""

    legend_ax.add_patch(
        Rectangle(
            (0.04, 0.08),
            0.92,
            0.84,
            transform=legend_ax.transAxes,
            facecolor="white",
            edgecolor="#333333",
            linewidth=0.9,
            zorder=1,
        )
    )
    legend_ax.legend(
        handles=handles,
        title=title,
        loc="upper left",
        bbox_to_anchor=(0.10, 0.86),
        frameon=False,
        fontsize=8.7,
        title_fontsize=9.5,
    )
    if note:
        legend_ax.text(
            0.10,
            0.15,
            note,
            ha="left",
            va="bottom",
            fontsize=7.5,
            color="#444444",
            linespacing=1.2,
            transform=legend_ax.transAxes,
        )


def classify_change(value: float) -> str:
    """Classify tract-level weekday trip change into reader-friendly bins."""

    if value <= -500:
        return "Large loss"
    if value < -100:
        return "Moderate loss"
    if value <= 100:
        return "Little/no change"
    if value < 500:
        return "Moderate gain"
    return "Large gain"


def load_project_inputs() -> tuple[pd.DataFrame, pd.DataFrame, gpd.GeoDataFrame]:
    """Load GTFS inventory, ACS indicators, and tract boundaries."""

    gtfs_inventory = pd.read_csv(PROCESSED_GTFS_DIR / "gtfs_feed_inventory.csv")
    acs = pd.read_csv(PROCESSED_ACS_DIR / "acs_transit_need_2024_montgomery_tracts.csv")
    tracts = gpd.read_file(PROCESSED_GEOGRAPHY_DIR / "montgomery_tracts_2024.geojson")

    acs["GEOID"] = acs["GEOID"].astype(str)
    tracts["GEOID"] = tracts["GEOID"].astype(str)

    acs["transit_need_quartile"] = pd.Categorical(
        acs["transit_need_quartile"],
        categories=NEED_QUARTILE_ORDER,
        ordered=True,
    )

    return gtfs_inventory, acs, tracts


def stop_metrics_to_geodataframe(stop_metrics: pd.DataFrame) -> gpd.GeoDataFrame:
    """Convert a stop metrics table into projected stop point geometries."""

    stops = stop_metrics.copy()
    stops["stop_id"] = stops["stop_id"].astype(str)

    stop_points = gpd.GeoDataFrame(
        stops,
        geometry=gpd.points_from_xy(stops["stop_lon"], stops["stop_lat"]),
        crs="EPSG:4326",
    )

    return stop_points.to_crs(ANALYSIS_CRS)


def aggregate_feed_to_tracts(
    feed_label: str,
    feed_role: str,
    tracts: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Aggregate one feed's stop-level service metrics to Census tracts."""

    metrics_path = PROCESSED_GTFS_DIR / f"stop_service_metrics_{feed_label}.csv"
    stop_metrics = pd.read_csv(metrics_path)

    # Pseudocode:
    # 1. Convert stops to points.
    # 2. Buffer each stop by 0.25 miles.
    # 3. Intersect stop catchments with tracts.
    # 4. Sum trip-based indicators for each tract.
    # 5. Average span indicators because span should not be summed.
    stop_points = stop_metrics_to_geodataframe(stop_metrics)
    stop_buffers = stop_points.copy()
    stop_buffers["geometry"] = stop_buffers.geometry.buffer(CATCHMENT_METERS)

    tracts_projected = tracts[["GEOID", "geometry"]].to_crs(ANALYSIS_CRS)

    stop_tract_links = gpd.sjoin(
        stop_buffers,
        tracts_projected,
        how="inner",
        predicate="intersects",
    )

    sum_aggregates = stop_tract_links.groupby("GEOID")[SERVICE_SUM_COLUMNS].sum()
    mean_aggregates = stop_tract_links.groupby("GEOID")[SERVICE_MEAN_COLUMNS].mean()
    max_aggregates = stop_tract_links.groupby("GEOID")[SERVICE_MEAN_COLUMNS].max()
    stop_counts = stop_tract_links.groupby("GEOID")["stop_id"].nunique()

    tract_metrics = pd.DataFrame({"GEOID": tracts["GEOID"].astype(str)})
    tract_metrics = tract_metrics.merge(
        stop_counts.rename("accessible_stop_count"),
        on="GEOID",
        how="left",
    )
    tract_metrics = tract_metrics.merge(sum_aggregates, on="GEOID", how="left")
    tract_metrics = tract_metrics.merge(
        mean_aggregates.add_prefix("mean_"),
        on="GEOID",
        how="left",
    )
    tract_metrics = tract_metrics.merge(
        max_aggregates.add_prefix("max_"),
        on="GEOID",
        how="left",
    )

    zero_columns = ["accessible_stop_count", *SERVICE_SUM_COLUMNS]
    tract_metrics[zero_columns] = tract_metrics[zero_columns].fillna(0)

    tract_metrics = tract_metrics.rename(
        columns={
            "weekday_total_trips": "weekday_total_trips_accessible",
            "weekend_total_trips": "weekend_total_trips_accessible",
            "weekday_peak_trips_per_hour": "weekday_peak_trips_per_hour_accessible",
        }
    )

    tract_metrics.insert(0, "feed_label", feed_label)
    tract_metrics.insert(1, "feed_role", feed_role)
    tract_metrics.insert(2, "catchment_miles", CATCHMENT_MILES)

    date_columns = [
        "weekday_analysis_date",
        "weekend_analysis_date",
    ]
    for column in date_columns:
        tract_metrics[column] = stop_metrics[column].iloc[0]

    return tract_metrics


def build_tract_service_panel(
    gtfs_inventory: pd.DataFrame,
    acs: pd.DataFrame,
    tracts: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Build a tract-by-feed service panel for all available GTFS feeds."""

    panel_parts = []

    for row in gtfs_inventory.itertuples(index=False):
        tract_metrics = aggregate_feed_to_tracts(
            feed_label=row.feed_label,
            feed_role=row.role,
            tracts=tracts,
        )
        panel_parts.append(tract_metrics)

    panel = pd.concat(panel_parts, ignore_index=True)
    panel = panel.merge(acs, on="GEOID", how="left")

    population_in_thousands = panel["total_population"].replace(0, pd.NA) / 1000
    panel["weekday_trips_per_1000_residents"] = (
        panel["weekday_total_trips_accessible"] / population_in_thousands
    )
    panel["weekend_trips_per_1000_residents"] = (
        panel["weekend_total_trips_accessible"] / population_in_thousands
    )
    panel["accessible_stops_per_1000_residents"] = (
        panel["accessible_stop_count"] / population_in_thousands
    )

    panel.to_csv(FINAL_OUTPUT_DIR / "tract_service_panel_025mi.csv", index=False)

    trend = (
        panel.groupby(["feed_label", "feed_role", "transit_need_quartile"], observed=True)
        .agg(
            n_tracts=("GEOID", "nunique"),
            mean_weekday_trips_accessible=(
                "weekday_total_trips_accessible",
                "mean",
            ),
            median_weekday_trips_accessible=(
                "weekday_total_trips_accessible",
                "median",
            ),
            mean_weekend_trips_accessible=(
                "weekend_total_trips_accessible",
                "mean",
            ),
            mean_accessible_stop_count=("accessible_stop_count", "mean"),
            mean_weekday_trips_per_1000_residents=(
                "weekday_trips_per_1000_residents",
                "mean",
            ),
        )
        .reset_index()
    )

    trend.to_csv(
        FINAL_OUTPUT_DIR / "tract_service_trend_by_need_quartile_025mi.csv",
        index=False,
    )

    return panel


def build_change_table(
    panel: pd.DataFrame,
    tracts: gpd.GeoDataFrame,
    pre_label: str,
    post_label: str,
    output_stem: str,
) -> gpd.GeoDataFrame:
    """Build one tract-level service change table between two feeds."""

    id_columns = [
        "GEOID",
        "tract_name",
        "transit_need_index",
        "transit_need_percentile",
        "transit_need_quartile",
        "pct_households_no_vehicle",
        "pct_people_below_poverty",
        "pct_age_65_plus",
        "pct_disabled",
        "pct_people_of_color",
        "median_household_income",
        "total_population",
    ]

    metric_columns = [
        "accessible_stop_count",
        "weekday_total_trips_accessible",
        "weekend_total_trips_accessible",
        "weekday_peak_trips_per_hour_accessible",
        "weekday_trips_per_1000_residents",
        "weekend_trips_per_1000_residents",
        "accessible_stops_per_1000_residents",
        "mean_weekday_span_hours",
        "mean_weekend_span_hours",
        "max_weekday_span_hours",
        "max_weekend_span_hours",
    ]

    pre = panel.loc[panel["feed_label"] == pre_label, id_columns + metric_columns].copy()
    post = panel.loc[panel["feed_label"] == post_label, ["GEOID", *metric_columns]].copy()

    change = pre.merge(
        post,
        on="GEOID",
        how="inner",
        suffixes=(f"_{pre_label}", f"_{post_label}"),
    )

    for metric in metric_columns:
        change[f"{metric}_change"] = (
            change[f"{metric}_{post_label}"] - change[f"{metric}_{pre_label}"]
        )

    change["transit_need_quartile"] = pd.Categorical(
        change["transit_need_quartile"],
        categories=NEED_QUARTILE_ORDER,
        ordered=True,
    )

    change.to_csv(FINAL_OUTPUT_DIR / f"{output_stem}.csv", index=False)

    tract_geometries = tracts[["GEOID", "geometry"]].copy()
    tract_geometries["GEOID"] = tract_geometries["GEOID"].astype(str)

    change_geo = tract_geometries.merge(change, on="GEOID", how="inner")
    change_geo.to_file(FINAL_OUTPUT_DIR / f"{output_stem}.geojson", driver="GeoJSON")

    return change_geo


def summarize_change_by_need(
    change_geo: gpd.GeoDataFrame,
    output_stem: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create descriptive and inferential equity summaries."""

    primary_metric = "weekday_total_trips_accessible_change"
    baseline_metric = "weekday_total_trips_accessible_2025_january"

    quartile_summary = (
        change_geo.groupby("transit_need_quartile", observed=True)
        .agg(
            n_tracts=("GEOID", "count"),
            mean_transit_need_index=("transit_need_index", "mean"),
            mean_baseline_weekday_trips=(baseline_metric, "mean"),
            mean_weekday_trip_change=(primary_metric, "mean"),
            median_weekday_trip_change=(primary_metric, "median"),
            mean_weekend_trip_change=("weekend_total_trips_accessible_change", "mean"),
            mean_peak_frequency_change=(
                "weekday_peak_trips_per_hour_accessible_change",
                "mean",
            ),
            mean_weekday_trips_per_1000_change=(
                "weekday_trips_per_1000_residents_change",
                "mean",
            ),
            mean_accessible_stop_change=("accessible_stop_count_change", "mean"),
        )
        .reset_index()
    )

    high_need = change_geo.loc[change_geo["transit_need_quartile"] == "high"]
    lower_need = change_geo.loc[change_geo["transit_need_quartile"] != "high"]

    t_test = stats.ttest_ind(
        high_need[primary_metric],
        lower_need[primary_metric],
        equal_var=False,
        nan_policy="omit",
    )

    pearson = stats.pearsonr(
        change_geo["transit_need_index"],
        change_geo[primary_metric],
    )
    spearman = stats.spearmanr(
        change_geo["transit_need_index"],
        change_geo[primary_metric],
    )

    test_summary = pd.DataFrame(
        [
            {
                "test": "Welch t-test: high need vs all other tracts",
                "metric": primary_metric,
                "statistic": t_test.statistic,
                "p_value": t_test.pvalue,
                "high_need_mean": high_need[primary_metric].mean(),
                "other_tracts_mean": lower_need[primary_metric].mean(),
                "interpretation_note": "Positive difference means high-need tracts gained more scheduled weekday trips.",
            },
            {
                "test": "Pearson correlation",
                "metric": primary_metric,
                "statistic": pearson.statistic,
                "p_value": pearson.pvalue,
                "high_need_mean": pd.NA,
                "other_tracts_mean": pd.NA,
                "interpretation_note": "Positive correlation means higher transit need is associated with larger service gains.",
            },
            {
                "test": "Spearman rank correlation",
                "metric": primary_metric,
                "statistic": spearman.statistic,
                "p_value": spearman.pvalue,
                "high_need_mean": pd.NA,
                "other_tracts_mean": pd.NA,
                "interpretation_note": "Positive correlation means higher transit need rank is associated with larger service-gain rank.",
            },
        ]
    )

    regression = smf.ols(
        formula=(
            "weekday_total_trips_accessible_change ~ "
            "transit_need_index + weekday_total_trips_accessible_2025_january"
        ),
        data=change_geo,
    ).fit()

    regression_summary = pd.DataFrame(
        {
            "term": regression.params.index,
            "estimate": regression.params.values,
            "std_error": regression.bse.values,
            "t_value": regression.tvalues.values,
            "p_value": regression.pvalues.values,
        }
    )

    quartile_summary.to_csv(
        FINAL_OUTPUT_DIR / f"{output_stem}_quartile_summary.csv",
        index=False,
    )
    test_summary.to_csv(
        FINAL_OUTPUT_DIR / f"{output_stem}_equity_tests.csv",
        index=False,
    )
    regression_summary.to_csv(
        FINAL_OUTPUT_DIR / f"{output_stem}_ols_summary.csv",
        index=False,
    )

    high_need_watchlist = (
        high_need.sort_values(primary_metric)
        [
            [
                "GEOID",
                "tract_name",
                "transit_need_index",
                "transit_need_percentile",
                "pct_households_no_vehicle",
                "pct_people_below_poverty",
                "pct_disabled",
                "weekday_total_trips_accessible_2025_january",
                "weekday_total_trips_accessible_change",
                "weekend_total_trips_accessible_change",
                "accessible_stop_count_change",
            ]
        ]
        .head(20)
    )
    high_need_watchlist.to_csv(
        FINAL_OUTPUT_DIR / f"{output_stem}_high_need_limited_improvement_watchlist.csv",
        index=False,
    )

    return quartile_summary, test_summary, regression_summary


def plot_need_map(tracts: gpd.GeoDataFrame, acs: pd.DataFrame) -> None:
    """Map the ACS Transit Need Index quartiles."""

    map_data = tracts.merge(acs, on="GEOID", how="left")
    map_data = map_data.to_crs(WEB_MERCATOR_CRS)
    map_data["need_color"] = map_data["transit_need_quartile"].map(NEED_COLORS)

    fig, ax, legend_ax = create_map_layout(
        title="Transit Need Across Montgomery County Census Tracts",
        subtitle="ACS index quartiles using no-vehicle households, poverty, age 65+, and disability.",
        source=(
            "Sources: 2020-2024 ACS 5-year estimates; 2024 TIGER/Line tracts. "
            "Basemap: Esri World Gray Canvas or CartoDB Positron, when available."
        ),
    )
    set_map_extent(ax, map_data)
    add_light_gray_basemap(ax)
    map_data.plot(
        color=map_data["need_color"],
        alpha=0.68,
        linewidth=0.35,
        edgecolor="white",
        ax=ax,
        zorder=5,
    )
    map_data.boundary.plot(ax=ax, color="#333333", linewidth=0.25, zorder=6)

    legend_handles = [
        Patch(facecolor=NEED_COLORS[key], edgecolor="#333333", label=NEED_QUARTILE_LABELS[key])
        for key in NEED_QUARTILE_ORDER
    ]
    draw_legend_panel(
        legend_ax,
        handles=legend_handles,
        title="Transit Need Quartile",
        note="Higher quartiles:\ngreater likely reliance\non transit.",
    )

    add_north_arrow(ax)
    add_scale_bar(ax)
    finish_map_axis(ax)
    fig.savefig(FINAL_FIGURE_DIR / "map_01_transit_need_quartiles.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def plot_change_map(change_geo: gpd.GeoDataFrame, output_name: str, title: str) -> None:
    """Map categorized weekday scheduled service change by tract."""

    metric = "weekday_total_trips_accessible_change"
    map_data = change_geo.to_crs(WEB_MERCATOR_CRS).copy()
    map_data["change_category"] = map_data[metric].map(classify_change)
    map_data["change_color"] = map_data["change_category"].map(CHANGE_FILL_COLORS)

    fig, ax, legend_ax = create_map_layout(
        title=title,
        subtitle="Change in scheduled weekday trips accessible within 0.25 miles of each tract.",
        source=(
            "Sources: Montgomery County Ride On GTFS; 2024 TIGER/Line tracts. "
            "Basemap: Esri World Gray Canvas or CartoDB Positron, when available."
        ),
    )
    set_map_extent(ax, map_data)
    add_light_gray_basemap(ax)
    map_data.plot(
        color=map_data["change_color"],
        linewidth=0.35,
        edgecolor="white",
        ax=ax,
        zorder=5,
    )
    map_data.boundary.plot(ax=ax, color="#333333", linewidth=0.25, zorder=6)

    legend_handles = [
        Patch(facecolor=CHANGE_COLORS[label], edgecolor="#333333", label=label)
        for label in CHANGE_COLORS
    ]
    draw_legend_panel(
        legend_ax,
        handles=legend_handles,
        title="Weekday Trip Change",
        note="Blue: more trips\nRed: fewer trips\nWhite: little/no change",
    )

    add_north_arrow(ax)
    add_scale_bar(ax)
    finish_map_axis(ax)
    fig.savefig(FINAL_FIGURE_DIR / output_name, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_high_need_watchlist_map(change_geo: gpd.GeoDataFrame) -> None:
    """Highlight high-need tracts with negative Phase 1 service change."""

    metric = "weekday_total_trips_accessible_change"
    map_data = change_geo.to_crs(WEB_MERCATOR_CRS).copy()
    map_data["map_category"] = "Other tracts"
    map_data.loc[
        map_data["transit_need_quartile"] == "high",
        "map_category",
    ] = "High need"
    map_data.loc[
        (map_data["transit_need_quartile"] == "high") & (map_data[metric] < 0),
        "map_category",
    ] = "High need + service loss"

    colors = {
        "Other tracts": "#E6E6E6",
        "High need": "#FDB863",
        "High need + service loss": "#B2182B",
    }

    fig, ax, legend_ax = create_map_layout(
        title="High-Need Tracts With Phase 1 Scheduled Service Losses",
        subtitle="Diagnostic watchlist: high transit need quartile and negative weekday trip change.",
        source=(
            "Sources: Montgomery County Ride On GTFS; 2020-2024 ACS; 2024 TIGER/Line tracts. "
            "Basemap: Esri World Gray Canvas or CartoDB Positron, when available."
        ),
    )
    set_map_extent(ax, map_data)
    add_light_gray_basemap(ax)
    for category, color in colors.items():
        subset = map_data.loc[map_data["map_category"] == category]
        subset.plot(color=color, alpha=0.72, linewidth=0.35, edgecolor="white", ax=ax, zorder=5)

    map_data.boundary.plot(ax=ax, color="#333333", linewidth=0.25, zorder=6)

    legend_handles = [
        Patch(facecolor=color, edgecolor="#333333", label=category)
        for category, color in colors.items()
    ]
    draw_legend_panel(
        legend_ax,
        handles=legend_handles,
        title="Watchlist Category",
        note="Red: high need + loss\nOrange: high need only\nGray: other tracts",
    )

    add_north_arrow(ax)
    add_scale_bar(ax)
    finish_map_axis(ax)
    fig.savefig(FINAL_FIGURE_DIR / "map_03_high_need_service_loss_watchlist.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def plot_quartile_summary(summary: pd.DataFrame, output_name: str, title: str) -> None:
    """Plot average weekday scheduled service change by need quartile."""

    summary = summary.copy()
    summary["transit_need_quartile"] = pd.Categorical(
        summary["transit_need_quartile"],
        categories=NEED_QUARTILE_ORDER,
        ordered=True,
    )
    summary = summary.sort_values("transit_need_quartile")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(
        summary["transit_need_quartile"].astype(str).map(NEED_QUARTILE_LABELS),
        summary["mean_weekday_trip_change"],
        color=["#8AA6A3", "#B5B682", "#D99B66", "#B85C5C"],
    )
    ax.axhline(0, color="black", linewidth=1)
    ax.set_xlabel("Transit need quartile")
    ax.set_ylabel("Mean change in accessible weekday trips")
    ax.set_title(title)
    for bar in ax.patches:
        value = bar.get_height()
        vertical_alignment = "bottom" if value >= 0 else "top"
        offset = 1 if value >= 0 else -1
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + offset,
            f"{value:.1f}",
            ha="center",
            va=vertical_alignment,
        )
    fig.savefig(FINAL_FIGURE_DIR / output_name, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_baseline_and_change_story(
    summary: pd.DataFrame,
    output_name: str,
    title: str,
    comparison_label: str,
) -> None:
    """Create a two-panel chart explaining baseline service and service change."""

    summary = summary.copy()
    summary["transit_need_quartile"] = pd.Categorical(
        summary["transit_need_quartile"],
        categories=NEED_QUARTILE_ORDER,
        ordered=True,
    )
    summary = summary.sort_values("transit_need_quartile")
    labels = summary["transit_need_quartile"].astype(str).map(NEED_QUARTILE_LABELS)
    colors = [NEED_COLORS[key] for key in NEED_QUARTILE_ORDER]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.6), constrained_layout=True)

    baseline_bars = axes[0].bar(
        labels,
        summary["mean_baseline_weekday_trips"],
        color=colors,
        edgecolor="#333333",
        linewidth=0.6,
    )
    axes[0].set_title("Before redesign period")
    axes[0].set_ylabel("Mean accessible weekday trips per tract")
    axes[0].tick_params(axis="x", rotation=20)
    for bar in baseline_bars:
        axes[0].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{bar.get_height():,.0f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    change_bars = axes[1].bar(
        labels,
        summary["mean_weekday_trip_change"],
        color=colors,
        edgecolor="#333333",
        linewidth=0.6,
    )
    axes[1].axhline(0, color="black", linewidth=1)
    axes[1].set_title(comparison_label)
    axes[1].set_ylabel("Mean change in accessible weekday trips")
    axes[1].tick_params(axis="x", rotation=20)
    for bar in change_bars:
        value = bar.get_height()
        vertical_alignment = "bottom" if value >= 0 else "top"
        offset = 2 if value >= 0 else -2
        axes[1].text(
            bar.get_x() + bar.get_width() / 2,
            value + offset,
            f"{value:,.1f}",
            ha="center",
            va=vertical_alignment,
            fontsize=9,
        )

    fig.suptitle(title, fontsize=16, fontweight="bold")
    fig.text(
        0.01,
        -0.03,
        "Note: Service is measured as scheduled weekday trips within 0.25 miles of each tract. "
        "Bars compare tract averages by ACS Transit Need Index quartile.",
        fontsize=9,
        color="#444444",
    )
    fig.savefig(FINAL_FIGURE_DIR / output_name, dpi=240, bbox_inches="tight")
    plt.close(fig)


def plot_analysis_workflow() -> None:
    """Draw a simple project workflow diagram for the final narrative."""

    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.set_axis_off()

    boxes = [
        (0.03, 0.55, "Ride On GTFS\nschedule feeds", "#E8F1F2"),
        (0.25, 0.55, "Stop-level service\nmetrics", "#E8F1F2"),
        (0.47, 0.55, "0.25-mile stop\ncatchments", "#E8F1F2"),
        (0.69, 0.55, "Tract-level service\nchange", "#E8F1F2"),
        (0.03, 0.14, "ACS tract\nindicators", "#F5E8D7"),
        (0.25, 0.14, "Transit Need\nIndex", "#F5E8D7"),
        (0.69, 0.14, "Equity test:\nDo higher-need tracts\ngain more service?", "#EAD7E8"),
    ]

    for x, y, text, color in boxes:
        ax.add_patch(
            plt.Rectangle(
                (x, y),
                0.16,
                0.24,
                facecolor=color,
                edgecolor="#333333",
                linewidth=1.1,
                transform=ax.transAxes,
            )
        )
        ax.text(
            x + 0.08,
            y + 0.12,
            text,
            ha="center",
            va="center",
            fontsize=10,
            transform=ax.transAxes,
        )

    arrows = [
        ((0.19, 0.67), (0.25, 0.67)),
        ((0.41, 0.67), (0.47, 0.67)),
        ((0.63, 0.67), (0.69, 0.67)),
        ((0.19, 0.26), (0.25, 0.26)),
        ((0.41, 0.26), (0.69, 0.26)),
        ((0.77, 0.55), (0.77, 0.38)),
    ]

    for start, end in arrows:
        ax.annotate(
            "",
            xy=end,
            xytext=start,
            xycoords="axes fraction",
            arrowprops={"arrowstyle": "->", "lw": 1.5, "color": "#333333"},
        )

    ax.text(
        0.03,
        0.92,
        "How The Final Analysis Answers The Research Question",
        fontsize=16,
        fontweight="bold",
        transform=ax.transAxes,
    )
    ax.text(
        0.03,
        0.86,
        "The workflow turns scheduled bus service and neighborhood need into comparable tract-level evidence.",
        fontsize=10,
        transform=ax.transAxes,
    )

    fig.savefig(FINAL_FIGURE_DIR / "figure_00_analysis_workflow.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def plot_need_scatter(change_geo: gpd.GeoDataFrame, output_name: str, title: str) -> None:
    """Plot Transit Need Index against weekday service change."""

    metric = "weekday_total_trips_accessible_change"

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(
        change_geo["transit_need_index"],
        change_geo[metric],
        s=28,
        color="#2F6B9A",
        alpha=0.75,
    )

    x = change_geo["transit_need_index"]
    y = change_geo[metric]
    slope, intercept, _r_value, _p_value, _std_err = stats.linregress(x, y)
    ax.plot(x, intercept + slope * x, color="black", linewidth=1.5)

    ax.axhline(0, color="gray", linewidth=1)
    ax.set_xlabel("Transit Need Index")
    ax.set_ylabel("Change in accessible weekday trips")
    ax.set_title(title)
    fig.savefig(FINAL_FIGURE_DIR / output_name, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_trend_by_quartile(trend: pd.DataFrame) -> None:
    """Plot service trends across all downloaded GTFS feeds by need quartile."""

    feed_order = [
        "2024_january",
        "2024_may",
        "2024_september",
        "2025_january",
        "2025_june",
        "2025_september",
        "2026_may_current",
    ]

    trend = trend.copy()
    trend["feed_label"] = pd.Categorical(
        trend["feed_label"],
        categories=feed_order,
        ordered=True,
    )
    trend = trend.sort_values(["feed_label", "transit_need_quartile"])
    trend["feed_display"] = trend["feed_label"].astype(str).map(FEED_LABELS)

    fig, ax = plt.subplots(figsize=(12.5, 6.2))
    fig.subplots_adjust(top=0.80)
    for quartile in NEED_QUARTILE_ORDER:
        group = trend.loc[trend["transit_need_quartile"] == quartile]
        ax.plot(
            group["feed_display"],
            group["mean_weekday_trips_accessible"],
            marker="o",
            linewidth=2.2,
            label=NEED_QUARTILE_LABELS[quartile],
            color=NEED_COLORS[quartile],
        )

    feed_labels = [FEED_LABELS[label] for label in feed_order]
    for implementation_label, note in [
        ("Jan 2025", "baseline"),
        ("Jun 2025", "Phase 1"),
        ("May 2026", "current"),
    ]:
        if implementation_label in feed_labels:
            x_position = feed_labels.index(implementation_label)
            ax.axvline(x_position, color="#555555", linestyle="--", linewidth=0.9, alpha=0.65)
            ax.text(
                x_position,
                0.98,
                note,
                transform=ax.get_xaxis_transform(),
                ha="center",
                va="top",
                fontsize=9,
                color="#333333",
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.75, "pad": 1.5},
            )

    ax.grid(axis="y", color="#DDDDDD", linewidth=0.8)
    ax.set_xlabel("GTFS feed")
    ax.set_ylabel("Mean accessible weekday trips per tract")
    fig.suptitle(
        "Scheduled Weekday Service Levels Across All GTFS Feeds",
        x=0.125,
        y=0.97,
        ha="left",
        fontsize=15,
        fontweight="bold",
    )
    fig.text(
        0.125,
        0.92,
        "Each line is a transit need quartile; vertical markers show the main comparison dates.",
        ha="left",
        fontsize=10,
    )
    ax.tick_params(axis="x", rotation=35)
    ax.legend(title="Transit need", frameon=True)
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(
        FINAL_FIGURE_DIR / "trend_weekday_service_by_need_quartile.png",
        dpi=220,
        bbox_inches="tight",
    )
    plt.close(fig)


def main() -> None:
    """Run the full tract-level final project analysis."""

    ensure_output_dirs()

    gtfs_inventory, acs, tracts = load_project_inputs()

    panel = build_tract_service_panel(gtfs_inventory, acs, tracts)

    phase1_change = build_change_table(
        panel,
        tracts,
        pre_label="2025_january",
        post_label="2025_june",
        output_stem="tract_service_change_phase1_2025jan_to_2025jun_025mi",
    )
    current_change = build_change_table(
        panel,
        tracts,
        pre_label="2025_january",
        post_label="2026_may_current",
        output_stem="tract_service_change_current_2025jan_to_2026may_025mi",
    )

    phase1_summary, _phase1_tests, _phase1_regression = summarize_change_by_need(
        phase1_change,
        output_stem="phase1_2025jan_to_2025jun",
    )
    current_summary, _current_tests, _current_regression = summarize_change_by_need(
        current_change,
        output_stem="current_2025jan_to_2026may",
    )

    trend = pd.read_csv(FINAL_OUTPUT_DIR / "tract_service_trend_by_need_quartile_025mi.csv")

    plot_analysis_workflow()
    plot_need_map(tracts, acs)
    plot_change_map(
        phase1_change,
        output_name="map_02_phase1_weekday_trip_change_categories.png",
        title="Pre/Post Phase 1 Scheduled Weekday Service Change",
    )
    plot_change_map(
        current_change,
        output_name="map_04_current_weekday_trip_change_categories.png",
        title="Published 2026 Schedule Sensitivity: Weekday Service Change",
    )
    plot_high_need_watchlist_map(phase1_change)
    plot_baseline_and_change_story(
        phase1_summary,
        output_name="figure_05_phase1_baseline_and_change_by_need.png",
        title="Pre vs Initial Post-Implementation: High-Need Tracts Did Not Receive Larger Average Gains",
        comparison_label="Change from pre feed to Phase 1 feed",
    )
    plot_baseline_and_change_story(
        current_summary,
        output_name="figure_06_current_baseline_and_change_by_need.png",
        title="Published 2026 Schedule Sensitivity: Changes Remain Mixed Across Need Quartiles",
        comparison_label="Change from Jan 2025 to May 2026 published schedule",
    )
    plot_trend_by_quartile(trend)


if __name__ == "__main__":
    main()
