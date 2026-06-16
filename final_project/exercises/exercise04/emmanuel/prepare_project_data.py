"""Preparing the main project datasets for the Ride On Reimagined analysis.

1. A GTFS inventory and stop-level service metrics for multiple schedule feeds.
2. ACS 2024 tract indicators for the Transit Need Index.
3. 2024 TIGER tract boundaries for Montgomery County, Maryland.

"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from zipfile import ZipFile

import geopandas as gpd
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from gtfs_service_metrics import (
    build_feed_metrics,
    compare_feed_metrics,
    find_first_active_date,
    read_gtfs_zip,
)


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

RAW_GTFS_DIR = RAW_DIR / "gtfs"
RAW_ACS_DIR = RAW_DIR / "acs"
RAW_TIGER_DIR = RAW_DIR / "tiger"

PROCESSED_GTFS_DIR = PROCESSED_DIR / "gtfs"
PROCESSED_ACS_DIR = PROCESSED_DIR / "acs"
PROCESSED_GEOGRAPHY_DIR = PROCESSED_DIR / "geography"


GTFS_FEEDS = {
    "2024_january": {
        "file": "rideon_2024_january.zip",
        "role": "early_pre_implementation_context",
        "url": "https://mcg.montgomerycountymd.gov/DOT-Transit/Resources/Files/GTFS/RideOnGTFS_removed_042524.zip",
    },
    "2024_may": {
        "file": "rideon_2024_may.zip",
        "role": "pre_implementation_context",
        "url": "https://mcg.montgomerycountymd.gov/DOT-Transit/Resources/Files/GTFS/RideOnGTFS_removed_082724.zip",
    },
    "2024_september": {
        "file": "rideon_2024_september.zip",
        "role": "pre_implementation_context",
        "url": "https://mcg.montgomerycountymd.gov/DOT-Transit/Resources/Files/GTFS/RideOnGTFS_removed_010825.zip",
    },
    "2025_january": {
        "file": "rideon_2025_january.zip",
        "role": "primary_pre_phase1_baseline",
        "url": "https://mcg.montgomerycountymd.gov/DOT-Transit/Resources/Files/GTFS/RideOnGTFS_removed_061225.zip",
    },
    "2025_june": {
        "file": "rideon_2025_june.zip",
        "role": "primary_post_phase1_feed",
        "url": "https://mcg.montgomerycountymd.gov/DOT-Transit/Resources/Files/GTFS/RideOnGTFS_removed_082825.zip",
    },
    "2025_september": {
        "file": "rideon_2025_september.zip",
        "role": "post_phase1_followup",
        "url": "https://mcg.montgomerycountymd.gov/DOT-Transit/Resources/Files/GTFS/RideOnGTFS_removed_010726.zip",
    },
    "2026_may_current": {
        "file": "rideon_2026_may_current.zip",
        "role": "published_current_feed_as_of_2026_04_30",
        "url": "https://mcg.montgomerycountymd.gov/DOT-Transit/Resources/Files/GTFS/RideOnGTFS.zip",
    },
}


ACS_YEAR = "2024"
ACS_STATE = "24"
ACS_COUNTY = "031"

ACS_PROFILE_VARIABLES = {
    "DP05_0001E": "total_population",
    "DP04_0058PE": "pct_households_no_vehicle",
    "DP03_0128PE": "pct_people_below_poverty",
    "DP05_0024PE": "pct_age_65_plus",
    "DP02_0072PE": "pct_disabled",
    "DP03_0062E": "median_household_income",
}

ACS_RACE_VARIABLES = {
    "B03002_001E": "race_ethnicity_total_population",
    "B03002_003E": "non_hispanic_white_alone",
    "B03002_004E": "non_hispanic_black_alone",
    "B03002_006E": "non_hispanic_asian_alone",
    "B03002_012E": "hispanic_or_latino",
}


def ensure_directories() -> None:
    """Create the raw and processed data folders used by the project."""

    for directory in [
        RAW_GTFS_DIR,
        RAW_ACS_DIR,
        RAW_TIGER_DIR,
        PROCESSED_GTFS_DIR,
        PROCESSED_ACS_DIR,
        PROCESSED_GEOGRAPHY_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)


def fetch_census_table(base_url: str, variables: dict[str, str]) -> pd.DataFrame:
    """Download one Census API table and return a named DataFrame."""

    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

    requested_variables = ["NAME", *variables.keys()]

    params = [
        ("get", ",".join(requested_variables)),
        ("for", "tract:*"),
        ("in", f"state:{ACS_STATE}"),
        ("in", f"county:{ACS_COUNTY}"),
    ]

    census_api_key = os.environ.get("CENSUS_API_KEY")
    if census_api_key:
        params.append(("key", census_api_key))

    response = session.get(base_url, params=params, timeout=180)
    response.raise_for_status()

    try:
        payload = response.json()
    except json.JSONDecodeError as exc:
        error_path = RAW_ACS_DIR / "last_census_api_response.txt"
        error_path.write_text(response.text, encoding="utf-8")
        preview = response.text[:500].replace("\n", " ")
        if "Invalid Key" in response.text:
            raise ValueError(
                "Census API rejected the provided CENSUS_API_KEY as invalid. "
                "Check that the key was copied correctly and activated, or unset "
                "CENSUS_API_KEY and try the public API request without a key."
            ) from exc
        raise ValueError(
            "Census API returned a non-JSON response. "
            f"Status: {response.status_code}. "
            f"Content-Type: {response.headers.get('content-type')}. "
            f"Preview: {preview}. "
            f"Full response saved to {error_path}."
        ) from exc
    header = payload[0]
    rows = payload[1:]

    frame = pd.DataFrame(rows, columns=header)
    frame["GEOID"] = frame["state"] + frame["county"] + frame["tract"]

    renamed_columns = {"NAME": "tract_name", **variables}
    frame = frame.rename(columns=renamed_columns)

    keep_columns = ["GEOID", "tract_name", *variables.values()]
    frame = frame[keep_columns]

    for column in variables.values():
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frame.loc[frame[column] < 0, column] = pd.NA

    return frame


def build_acs_transit_need_dataset() -> pd.DataFrame:
    """Fetch ACS indicators and calculate a tract-level Transit Need Index."""

    profile_url = f"https://api.census.gov/data/{ACS_YEAR}/acs/acs5/profile"
    detailed_url = f"https://api.census.gov/data/{ACS_YEAR}/acs/acs5"

    profile = fetch_census_table(profile_url, ACS_PROFILE_VARIABLES)
    race = fetch_census_table(detailed_url, ACS_RACE_VARIABLES)

    profile.to_csv(
        RAW_ACS_DIR / f"acs_{ACS_YEAR}_profile_montgomery_tracts.csv",
        index=False,
    )
    race.to_csv(
        RAW_ACS_DIR / f"acs_{ACS_YEAR}_race_ethnicity_montgomery_tracts.csv",
        index=False,
    )

    acs = profile.merge(
        race.drop(columns=["tract_name"]),
        on="GEOID",
        how="left",
    )

    acs["pct_people_of_color"] = (
        100
        * (
            acs["race_ethnicity_total_population"]
            - acs["non_hispanic_white_alone"]
        )
        / acs["race_ethnicity_total_population"]
    )

    index_components = [
        "pct_households_no_vehicle",
        "pct_people_below_poverty",
        "pct_age_65_plus",
        "pct_disabled",
    ]

    for column in index_components:
        z_column = f"{column}_z"
        acs[z_column] = (acs[column] - acs[column].mean()) / acs[column].std()

    z_columns = [f"{column}_z" for column in index_components]
    acs["transit_need_index"] = acs[z_columns].mean(axis=1)
    acs["transit_need_percentile"] = acs["transit_need_index"].rank(pct=True)
    acs["transit_need_quartile"] = pd.qcut(
        acs["transit_need_index"],
        q=4,
        labels=["low", "moderate_low", "moderate_high", "high"],
    )

    acs.to_csv(
        PROCESSED_ACS_DIR / f"acs_transit_need_{ACS_YEAR}_montgomery_tracts.csv",
        index=False,
    )

    return acs


def prepare_montgomery_tract_boundaries() -> gpd.GeoDataFrame:
    """Prepare Montgomery County tracts from the 2024 Maryland TIGER file."""

    tiger_zip = RAW_TIGER_DIR / "tl_2024_24_tract.zip"

    if not tiger_zip.exists():
        raise FileNotFoundError(
            "Missing TIGER ZIP file. Expected data/raw/tiger/tl_2024_24_tract.zip"
        )

    maryland_tracts = gpd.read_file(f"zip://{tiger_zip}")

    montgomery_tracts = maryland_tracts.loc[
        maryland_tracts["COUNTYFP"] == ACS_COUNTY
    ].copy()

    output_columns = [
        "STATEFP",
        "COUNTYFP",
        "TRACTCE",
        "GEOID",
        "NAME",
        "NAMELSAD",
        "ALAND",
        "AWATER",
        "geometry",
    ]
    montgomery_tracts = montgomery_tracts[output_columns]

    montgomery_tracts.to_file(
        PROCESSED_GEOGRAPHY_DIR / "montgomery_tracts_2024.geojson",
        driver="GeoJSON",
    )
    montgomery_tracts.to_file(
        PROCESSED_GEOGRAPHY_DIR / "montgomery_tracts_2024.gpkg",
        layer="montgomery_tracts_2024",
        driver="GPKG",
    )

    return montgomery_tracts


def build_gtfs_inventory() -> pd.DataFrame:
    """Create a metadata table describing each downloaded GTFS feed."""

    inventory_rows = []

    for feed_label, feed_info in GTFS_FEEDS.items():
        zip_path = RAW_GTFS_DIR / feed_info["file"]

        if not zip_path.exists():
            raise FileNotFoundError(f"Missing GTFS feed: {zip_path}")

        tables = read_gtfs_zip(zip_path)
        if "feed_info" in tables:
            feed_table = tables["feed_info"].iloc[0].to_dict()
            feed_start_date = feed_table.get("feed_start_date")
            feed_end_date = feed_table.get("feed_end_date")
            feed_version = feed_table.get("feed_version")
        else:
            calendar = tables["calendar"].copy()
            feed_start_date = calendar["start_date"].min()
            feed_end_date = calendar["end_date"].max()
            feed_version = "missing_feed_info_table"

        with ZipFile(zip_path) as gtfs_zip:
            file_list = gtfs_zip.namelist()
            row_counts = {
                table_name.replace(".txt", "_rows"): len(tables[table_name.replace(".txt", "")])
                for table_name in file_list
                if table_name.endswith(".txt") and table_name.replace(".txt", "") in tables
            }

        representative_tuesday = find_first_active_date(
            tables,
            "tuesday",
        ).date()
        representative_saturday = find_first_active_date(
            tables,
            "saturday",
        ).date()

        inventory_rows.append(
            {
                "feed_label": feed_label,
                "role": feed_info["role"],
                "local_file": feed_info["file"],
                "source_url": feed_info["url"],
                "feed_start_date": feed_start_date,
                "feed_end_date": feed_end_date,
                "feed_version": feed_version,
                "representative_tuesday": representative_tuesday,
                "representative_saturday": representative_saturday,
                **row_counts,
            }
        )

    inventory = pd.DataFrame(inventory_rows)
    inventory.to_csv(PROCESSED_GTFS_DIR / "gtfs_feed_inventory.csv", index=False)

    return inventory


def build_all_gtfs_metrics() -> None:
    """Build stop-level metrics for every GTFS feed in the project inventory."""

    metrics_by_feed: dict[str, pd.DataFrame] = {}

    for feed_label, feed_info in GTFS_FEEDS.items():
        metrics = build_feed_metrics(RAW_GTFS_DIR / feed_info["file"], feed_label)
        metrics_by_feed[feed_label] = metrics
        metrics.to_csv(
            PROCESSED_GTFS_DIR / f"stop_service_metrics_{feed_label}.csv",
            index=False,
        )

    phase1_change = compare_feed_metrics(
        metrics_by_feed["2025_january"],
        metrics_by_feed["2025_june"],
        "2025_january",
        "2025_june",
    )
    phase1_change.to_csv(
        PROCESSED_GTFS_DIR / "stop_service_change_2025_january_to_2025_june.csv",
        index=False,
    )

    current_change = compare_feed_metrics(
        metrics_by_feed["2025_january"],
        metrics_by_feed["2026_may_current"],
        "2025_january",
        "2026_may_current",
    )
    current_change.to_csv(
        PROCESSED_GTFS_DIR / "stop_service_change_2025_january_to_2026_may_current.csv",
        index=False,
    )


def write_data_catalog(
    gtfs_inventory: pd.DataFrame,
    acs: pd.DataFrame | None,
    tracts: gpd.GeoDataFrame,
) -> None:
    """Write a compact catalog that documents the prepared project datasets."""

    catalog_rows = [
        {
            "dataset": "Ride On GTFS snapshots",
            "path": "data/raw/gtfs/",
            "rows_or_features": f"{len(gtfs_inventory)} feeds",
            "source": "Montgomery County Current and Archived GTFS files",
            "notes": "Includes pre-implementation, Phase 1, follow-up, and current published feeds.",
        },
        {
            "dataset": "GTFS feed inventory",
            "path": "data/processed/gtfs/gtfs_feed_inventory.csv",
            "rows_or_features": len(gtfs_inventory),
            "source": "Derived from GTFS feed_info and table row counts",
            "notes": "Use this to choose pre/post comparison feeds with explicit dates.",
        },
        {
            "dataset": "Stop-level GTFS service metrics",
            "path": "data/processed/gtfs/stop_service_metrics_*.csv",
            "rows_or_features": "one row per served stop per feed",
            "source": "Derived from GTFS trips, stop_times, stops, and calendar tables",
            "notes": "Measures scheduled service supply, not rider experience.",
        },
        {
            "dataset": "ACS Transit Need Index",
            "path": f"data/processed/acs/acs_transit_need_{ACS_YEAR}_montgomery_tracts.csv",
            "rows_or_features": len(acs) if acs is not None else "pending",
            "source": f"2020-{ACS_YEAR} ACS 5-year profile and detailed tables",
            "notes": "Index averages z-scores for no-vehicle households, poverty, age 65+, and disability. Requires Census API access.",
        },
        {
            "dataset": "Montgomery County Census tracts",
            "path": "data/processed/geography/montgomery_tracts_2024.geojson",
            "rows_or_features": len(tracts),
            "source": "2024 TIGER/Line tract boundaries for Maryland",
            "notes": "Filtered to Montgomery County, Maryland.",
        },
    ]

    catalog = pd.DataFrame(catalog_rows)
    catalog.to_csv(DATA_DIR / "project_data_catalog.csv", index=False)


def main(skip_acs: bool = False) -> None:
    """Run the full project data preparation workflow."""

    ensure_directories()
    gtfs_inventory = build_gtfs_inventory()
    build_all_gtfs_metrics()
    acs = None if skip_acs else build_acs_transit_need_dataset()
    tracts = prepare_montgomery_tract_boundaries()
    write_data_catalog(gtfs_inventory, acs, tracts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Prepare project datasets for the Ride On Reimagined analysis."
    )
    parser.add_argument(
        "--skip-acs",
        action="store_true",
        help="Prepare GTFS and geography outputs without fetching ACS from the Census API.",
    )
    args = parser.parse_args()
    main(skip_acs=args.skip_acs)
