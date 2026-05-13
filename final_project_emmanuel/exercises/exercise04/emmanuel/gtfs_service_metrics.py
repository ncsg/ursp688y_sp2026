"""Utility functions for measuring scheduled Ride On service from GTFS files.

Here I use this module to support Exercise04, to turn raw GTFS schedule tables into stop-level service indicators that can
later be joined to Census geography and ACS-based transit need measures.
"""

from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

import pandas as pd


DAY_COLUMNS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


DEFAULT_PEAK_PERIODS = (
    ("morning_peak", "07:00:00", "09:00:00"),
    ("evening_peak", "16:00:00", "18:00:00"),
)


def read_gtfs_zip(zip_path: str | Path) -> dict[str, pd.DataFrame]:
    """Read the GTFS tables needed for this analysis from a ZIP file."""

    zip_path = Path(zip_path)

    required_tables = [
        "stops.txt",
        "trips.txt",
        "stop_times.txt",
        "calendar.txt",
        "calendar_dates.txt",
        "routes.txt",
    ]
    optional_tables = ["feed_info.txt"]

    tables: dict[str, pd.DataFrame] = {}

    with ZipFile(zip_path) as gtfs_zip:
        available_files = set(gtfs_zip.namelist())

        for table_name in required_tables:
            if table_name in available_files:
                short_name = table_name.replace(".txt", "")
                tables[short_name] = pd.read_csv(gtfs_zip.open(table_name), dtype=str)

        for table_name in optional_tables:
            if table_name in available_files:
                short_name = table_name.replace(".txt", "")
                tables[short_name] = pd.read_csv(gtfs_zip.open(table_name), dtype=str)

    missing_tables = [
        table.replace(".txt", "")
        for table in required_tables
        if table not in available_files
    ]

    if missing_tables:
        raise ValueError(f"Missing required GTFS tables: {missing_tables}")

    return tables


def gtfs_date_to_int(service_date: str | pd.Timestamp) -> int:
    """Convert a readable date into the YYYYMMDD integer format used by GTFS."""

    return int(pd.Timestamp(service_date).strftime("%Y%m%d"))


def parse_gtfs_time_to_seconds(time_series: pd.Series) -> pd.Series:
    """Convert GTFS HH:MM:SS times into seconds after service day midnight."""

    parts = time_series.fillna("").str.split(":", expand=True)

    hours = pd.to_numeric(parts[0], errors="coerce")
    minutes = pd.to_numeric(parts[1], errors="coerce")
    seconds = pd.to_numeric(parts[2], errors="coerce")

    return (hours * 3600) + (minutes * 60) + seconds


def seconds_to_gtfs_time(seconds: float | int | None) -> str:
    """Convert seconds after service day midnight back into HH:MM:SS text."""

    if pd.isna(seconds):
        return ""

    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"


def active_service_ids(
    tables: dict[str, pd.DataFrame],
    service_date: str | pd.Timestamp,
) -> set[str]:
    """Find the GTFS service_ids that operate on one analysis date."""

    calendar = tables["calendar"].copy()
    calendar_dates = tables["calendar_dates"].copy()

    service_date = pd.Timestamp(service_date)
    service_date_int = gtfs_date_to_int(service_date)
    weekday_column = service_date.day_name().lower()

    calendar["start_date"] = pd.to_numeric(calendar["start_date"])
    calendar["end_date"] = pd.to_numeric(calendar["end_date"])
    calendar[weekday_column] = pd.to_numeric(calendar[weekday_column])

    scheduled_mask = (
        (calendar["start_date"] <= service_date_int)
        & (calendar["end_date"] >= service_date_int)
        & (calendar[weekday_column] == 1)
    )

    services = set(calendar.loc[scheduled_mask, "service_id"].astype(str))

    calendar_dates["date"] = pd.to_numeric(calendar_dates["date"])
    calendar_dates["exception_type"] = pd.to_numeric(calendar_dates["exception_type"])

    exceptions = calendar_dates.loc[calendar_dates["date"] == service_date_int].copy()

    added_services = set(
        exceptions.loc[exceptions["exception_type"] == 1, "service_id"].astype(str)
    )
    removed_services = set(
        exceptions.loc[exceptions["exception_type"] == 2, "service_id"].astype(str)
    )

    services.update(added_services)
    services.difference_update(removed_services)

    return services


def find_first_active_date(
    tables: dict[str, pd.DataFrame],
    weekday_name: str,
) -> pd.Timestamp:
    """Find the first date in the feed where at least one service runs."""

    weekday_name = weekday_name.lower()

    if weekday_name not in DAY_COLUMNS:
        raise ValueError(f"weekday_name must be one of {DAY_COLUMNS}")

    if "feed_info" in tables:
        feed_info = tables["feed_info"].copy()
        start_date = pd.to_datetime(str(feed_info.loc[0, "feed_start_date"]))
        end_date = pd.to_datetime(str(feed_info.loc[0, "feed_end_date"]))
    else:
        calendar = tables["calendar"].copy()
        start_date = pd.to_datetime(str(calendar["start_date"].min()))
        end_date = pd.to_datetime(str(calendar["end_date"].max()))

    for candidate_date in pd.date_range(start_date, end_date, freq="D"):
        if candidate_date.day_name().lower() != weekday_name:
            continue

        if active_service_ids(tables, candidate_date):
            return candidate_date

    raise ValueError(f"No active {weekday_name} service found in the feed.")


def service_hours_from_periods(
    peak_periods: tuple[tuple[str, str, str], ...] = DEFAULT_PEAK_PERIODS,
) -> float:
    """Calculate the total number of hours represented by the peak periods."""

    total_seconds = 0

    for _name, start_time, end_time in peak_periods:
        start_seconds = parse_gtfs_time_to_seconds(pd.Series([start_time])).iloc[0]
        end_seconds = parse_gtfs_time_to_seconds(pd.Series([end_time])).iloc[0]
        total_seconds += end_seconds - start_seconds

    return total_seconds / 3600


def stop_metrics_for_date(
    tables: dict[str, pd.DataFrame],
    service_date: str | pd.Timestamp,
    peak_periods: tuple[tuple[str, str, str], ...] = DEFAULT_PEAK_PERIODS,
) -> pd.DataFrame:
    """Calculate stop-level scheduled service indicators for one date."""

    service_date = pd.Timestamp(service_date)
    services = active_service_ids(tables, service_date)

    if not services:
        raise ValueError(f"No active GTFS service found on {service_date.date()}.")

    trips = tables["trips"].copy()
    stop_times = tables["stop_times"].copy()
    stops = tables["stops"].copy()

    active_trips = trips.loc[trips["service_id"].astype(str).isin(services)].copy()

    active_stop_times = stop_times.merge(
        active_trips[["trip_id", "route_id", "service_id"]],
        on="trip_id",
        how="inner",
    )

    departure_source = active_stop_times["departure_time"].fillna(
        active_stop_times["arrival_time"]
    )
    active_stop_times["departure_seconds"] = parse_gtfs_time_to_seconds(
        departure_source
    )

    total_trips = (
        active_stop_times.groupby("stop_id")["trip_id"]
        .nunique()
        .rename("total_trips")
    )

    routes_serving_stop = (
        active_stop_times.groupby("stop_id")["route_id"]
        .nunique()
        .rename("routes_serving_stop")
    )

    peak_mask = pd.Series(False, index=active_stop_times.index)

    for _name, start_time, end_time in peak_periods:
        start_seconds = parse_gtfs_time_to_seconds(pd.Series([start_time])).iloc[0]
        end_seconds = parse_gtfs_time_to_seconds(pd.Series([end_time])).iloc[0]
        peak_mask = peak_mask | active_stop_times["departure_seconds"].between(
            start_seconds,
            end_seconds,
            inclusive="left",
        )

    peak_hours = service_hours_from_periods(peak_periods)

    peak_trips = (
        active_stop_times.loc[peak_mask]
        .groupby("stop_id")["trip_id"]
        .nunique()
        .rename("peak_trips")
    )

    service_span = (
        active_stop_times.groupby("stop_id")["departure_seconds"]
        .agg(first_departure_seconds="min", last_departure_seconds="max")
        .reset_index()
    )

    service_span["span_hours"] = (
        service_span["last_departure_seconds"]
        - service_span["first_departure_seconds"]
    ) / 3600

    service_span["first_departure_time"] = service_span[
        "first_departure_seconds"
    ].map(seconds_to_gtfs_time)
    service_span["last_departure_time"] = service_span["last_departure_seconds"].map(
        seconds_to_gtfs_time
    )

    metrics = (
        pd.DataFrame(index=total_trips.index)
        .join(total_trips)
        .join(routes_serving_stop)
        .join(peak_trips)
        .fillna({"peak_trips": 0})
        .reset_index()
    )

    metrics["peak_hours"] = peak_hours
    metrics["peak_trips_per_hour"] = metrics["peak_trips"] / metrics["peak_hours"]

    metrics = metrics.merge(service_span, on="stop_id", how="left")

    stops["stop_lat"] = pd.to_numeric(stops["stop_lat"], errors="coerce")
    stops["stop_lon"] = pd.to_numeric(stops["stop_lon"], errors="coerce")

    metrics = stops[
        ["stop_id", "stop_name", "stop_lat", "stop_lon"]
    ].merge(metrics, on="stop_id", how="inner")

    metrics.insert(0, "analysis_date", service_date.date().isoformat())
    metrics.insert(1, "active_service_count", len(services))

    numeric_columns = [
        "total_trips",
        "routes_serving_stop",
        "peak_trips",
        "peak_hours",
        "peak_trips_per_hour",
        "span_hours",
    ]
    metrics[numeric_columns] = metrics[numeric_columns].round(3)

    return metrics.sort_values(["total_trips", "stop_name"], ascending=[False, True])


def build_feed_metrics(
    zip_path: str | Path,
    feed_label: str,
    weekday_name: str = "tuesday",
    weekend_name: str = "saturday",
) -> pd.DataFrame:
    """Build one stop-level metrics table for a GTFS feed."""

    tables = read_gtfs_zip(zip_path)

    weekday_date = find_first_active_date(tables, weekday_name)
    weekend_date = find_first_active_date(tables, weekend_name)

    weekday_metrics = stop_metrics_for_date(tables, weekday_date)
    weekend_metrics = stop_metrics_for_date(tables, weekend_date)

    weekday_keep = [
        "stop_id",
        "stop_name",
        "stop_lat",
        "stop_lon",
        "analysis_date",
        "total_trips",
        "routes_serving_stop",
        "peak_trips_per_hour",
        "span_hours",
        "first_departure_time",
        "last_departure_time",
    ]

    weekend_keep = [
        "stop_id",
        "analysis_date",
        "total_trips",
        "span_hours",
    ]

    weekday_metrics = weekday_metrics[weekday_keep].rename(
        columns={
            "analysis_date": "weekday_analysis_date",
            "total_trips": "weekday_total_trips",
            "routes_serving_stop": "weekday_routes_serving_stop",
            "peak_trips_per_hour": "weekday_peak_trips_per_hour",
            "span_hours": "weekday_span_hours",
            "first_departure_time": "weekday_first_departure_time",
            "last_departure_time": "weekday_last_departure_time",
        }
    )

    weekend_metrics = weekend_metrics[weekend_keep].rename(
        columns={
            "analysis_date": "weekend_analysis_date",
            "total_trips": "weekend_total_trips",
            "span_hours": "weekend_span_hours",
        }
    )

    metrics = weekday_metrics.merge(weekend_metrics, on="stop_id", how="left")
    metrics.insert(0, "feed_label", feed_label)

    return metrics.sort_values(
        ["weekday_total_trips", "stop_name"],
        ascending=[False, True],
    )


def compare_feed_metrics(
    pre_metrics: pd.DataFrame,
    post_metrics: pd.DataFrame,
    pre_label: str,
    post_label: str,
) -> pd.DataFrame:
    """Compare stop-level metrics between two feeds using stable stop IDs."""

    id_columns = ["stop_id"]

    comparison = pre_metrics.merge(
        post_metrics,
        on=id_columns,
        how="outer",
        suffixes=(f"_{pre_label}", f"_{post_label}"),
        indicator=True,
    )

    change_columns = [
        "weekday_total_trips",
        "weekend_total_trips",
        "weekday_peak_trips_per_hour",
        "weekday_span_hours",
        "weekend_span_hours",
    ]

    for column in change_columns:
        pre_column = f"{column}_{pre_label}"
        post_column = f"{column}_{post_label}"
        change_column = f"{column}_change"

        comparison[change_column] = (
            comparison[post_column].fillna(0) - comparison[pre_column].fillna(0)
        )

    return comparison
