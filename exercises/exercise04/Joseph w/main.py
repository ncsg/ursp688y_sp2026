r"""DC dog park equity analysis framework.

Run from PowerShell in this folder:

    cd "H:\github\urban datas science\ursp688y_sp2026_JW\exercises\exercise04\Joseph w"
    H:\urbandatascience\envs\688y\python.exe main.py

Or run the Windows helper:

    .\run_windows.ps1

The script uses the local Open Data DC and ACS extracts already saved in the
``Joseph w`` folder. It creates the output folder automatically with Python,
then writes cleaned tables, charts, a short findings memo, and an optional
Folium map to ``outputs``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode

import pandas as pd

from visualize import (
    make_dog_park_leaflet_map,
    plot_dog_park_area_by_ward,
    plot_dog_parks_by_ward,
    plot_neighborhood_single_households,
    plot_supply_need_scatter,
    write_findings_markdown,
)


PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "outputs"


LOCAL_FILES = {
    "dog_parks": "Dog_Parks.csv",
    "national_parks": "National_Parks (1).csv",
    "community_gardens": "Community_Garden.csv",
    "schools": "DC_Public_Schools.csv",
    "affordable_housing": "Affordable_Housing.csv",
    "acs_economic": "ACS_5-Year_Economic_Characteristics_of_DC_Census_Tracts.csv",
    "age_citywide": "age in dc.csv",
    "one_person_households": "dc_oneperson_households.csv",
    "rent_owner_citywide": "rent vs owner dc.csv",
    "housing_structure_citywide": "houses sizes in dc.csv",
}


OPEN_DATA_DC_ENDPOINTS = {
    "dog_parks": "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Recreation_WebMercator/MapServer/2",
    "recreation_centers": "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Recreation_WebMercator/MapServer/4",
    "dc_parks": "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Recreation_WebMercator/MapServer/9",
    "national_parks": "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Recreation_WebMercator/MapServer/10",
}


ACS_5_YEAR_TABLES = {
    "median_income": "B19013",
    "age_by_sex": "B01001",
    "household_type": "B11001",
    "renters_owners": "B25003",
    "housing_occupancy": "B25014",
    "poverty": "B17001",
    "race_ethnicity": "B03002",
    "demographic_profile": "DP05",
}


@dataclass(frozen=True)
class AnalysisOutputs:
    ward_summary: Path
    tract_summary: Path | None
    chart_files: list[Path]
    memo: Path
    map_file: Path | None


def clean_number(value) -> float | None:
    """Convert ACS-style strings such as '194,851' or '±4,510' to numbers."""
    if pd.isna(value):
        return None
    cleaned = (
        str(value)
        .replace(",", "")
        .replace("±", "")
        .replace("%", "")
        .replace("(X)", "")
        .replace("*****", "")
        .strip()
    )
    if not cleaned:
        return None
    return pd.to_numeric(cleaned, errors="coerce")


def normalize_ward(value) -> str | None:
    """Return a consistent 'Ward N' label from Open Data DC ward values."""
    if pd.isna(value):
        return None
    text = str(value).strip()
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return None
    return f"Ward {int(digits)}"


def read_csv_if_exists(data_dir: Path, filename: str) -> pd.DataFrame:
    file_path = data_dir / filename
    if not file_path.exists():
        return pd.DataFrame()
    return pd.read_csv(file_path)


def arcgis_query_url(layer_url: str, where: str = "1=1", out_fields: str = "*") -> str:
    """Build a GeoJSON query URL for an ArcGIS REST feature layer."""
    params = urlencode(
        {
            "where": where,
            "outFields": out_fields,
            "returnGeometry": "true",
            "f": "geojson",
        }
    )
    return f"{layer_url}/query?{params}"


def load_arcgis_layer(layer_name: str):
    """Load an official Open Data DC layer with geopandas when available."""
    layer_url = OPEN_DATA_DC_ENDPOINTS[layer_name]
    try:
        import geopandas as gpd
    except ImportError as exc:
        raise ImportError("Install geopandas to load ArcGIS layers.") from exc
    return gpd.read_file(arcgis_query_url(layer_url))


def load_local_data(data_dir: Path) -> dict[str, pd.DataFrame]:
    return {
        name: read_csv_if_exists(data_dir, filename)
        for name, filename in LOCAL_FILES.items()
    }


def prepare_dog_parks(dog_parks: pd.DataFrame) -> pd.DataFrame:
    if dog_parks.empty:
        return dog_parks

    dog_parks = dog_parks.copy()
    dog_parks["ward"] = dog_parks["WARD"].apply(normalize_ward)
    dog_parks["SIZE_"] = pd.to_numeric(dog_parks["SIZE_"], errors="coerce")
    dog_parks["LATITUDE"] = pd.to_numeric(dog_parks["LATITUDE"], errors="coerce")
    dog_parks["LONGITUDE"] = pd.to_numeric(dog_parks["LONGITUDE"], errors="coerce")
    return dog_parks.dropna(subset=["ward"])


def summarize_ward_supply(dog_parks: pd.DataFrame) -> pd.DataFrame:
    wards = pd.DataFrame({"ward": [f"Ward {ward}" for ward in range(1, 9)]})
    if dog_parks.empty:
        wards["dog_park_count"] = 0
        wards["dog_park_sqft"] = 0
        wards["avg_dog_park_sqft"] = 0
        return wards

    summary = (
        dog_parks.groupby("ward")
        .agg(
            dog_park_count=("NAME", "count"),
            dog_park_sqft=("SIZE_", "sum"),
            avg_dog_park_sqft=("SIZE_", "mean"),
        )
        .reset_index()
    )
    return wards.merge(summary, on="ward", how="left").fillna(0)


def add_affordable_housing_proxy(
    ward_summary: pd.DataFrame, affordable_housing: pd.DataFrame
) -> pd.DataFrame:
    if affordable_housing.empty or "MAR_WARD" not in affordable_housing.columns:
        ward_summary["affordable_units"] = 0
        return ward_summary

    housing = affordable_housing.copy()
    housing["ward"] = housing["MAR_WARD"].apply(normalize_ward)
    housing["TOTAL_AFFORDABLE_UNITS"] = pd.to_numeric(
        housing["TOTAL_AFFORDABLE_UNITS"], errors="coerce"
    ).fillna(0)
    housing_by_ward = (
        housing.groupby("ward")["TOTAL_AFFORDABLE_UNITS"].sum().reset_index()
    )
    housing_by_ward = housing_by_ward.rename(
        columns={"TOTAL_AFFORDABLE_UNITS": "affordable_units"}
    )
    return ward_summary.merge(housing_by_ward, on="ward", how="left").fillna(
        {"affordable_units": 0}
    )


def add_green_space_context(
    ward_summary: pd.DataFrame,
    community_gardens: pd.DataFrame,
    schools: pd.DataFrame,
) -> pd.DataFrame:
    enriched = ward_summary.copy()

    if not community_gardens.empty and "WARD" in community_gardens.columns:
        gardens = community_gardens.copy()
        gardens["ward"] = gardens["WARD"].apply(normalize_ward)
        gardens_by_ward = gardens.groupby("ward").size().rename("community_gardens")
        enriched = enriched.merge(gardens_by_ward, on="ward", how="left")

    if not schools.empty and {"LATITUDE", "LONGITUDE"}.issubset(schools.columns):
        # School points are kept as context for future service-area analysis.
        enriched["school_points_available"] = len(schools)

    return enriched.fillna({"community_gardens": 0, "school_points_available": 0})


def summarize_acs_economic(acs: pd.DataFrame, output_dir: Path) -> Path | None:
    """Create a tract-level economic table using common DP03 fields.

    DP03_0062E is median household income in the ACS Data Profile. The poverty
    field varies by extract, so this function preserves candidate columns for
    notebook review instead of over-claiming a single poverty measure.
    """
    if acs.empty:
        return None

    keep_columns = [
        col
        for col in [
            "GEOID",
            "NAME",
            "NAMELSAD",
            "INTPTLAT",
            "INTPTLON",
            "DP03_0062E",
            "DP03_0128PE",
            "DP03_0136PE",
            "ALAND",
            "AWATER",
        ]
        if col in acs.columns
    ]
    if not keep_columns:
        return None

    tract_summary = acs[keep_columns].copy()
    rename_map = {
        "DP03_0062E": "median_household_income",
        "DP03_0128PE": "poverty_candidate_pct",
        "DP03_0136PE": "poverty_or_assistance_candidate_pct",
    }
    tract_summary = tract_summary.rename(columns=rename_map)
    for col in tract_summary.columns:
        if col not in {"GEOID", "NAME", "NAMELSAD"}:
            tract_summary[col] = tract_summary[col].apply(clean_number)

    output_dir.mkdir(parents=True, exist_ok=True)
    tract_file = output_dir / "tract_economic_summary.csv"
    tract_summary.to_csv(tract_file, index=False)
    return tract_file


def citywide_context(data: dict[str, pd.DataFrame]) -> dict[str, float | None]:
    """Extract citywide age, renter, and apartment context from local ACS files."""
    context: dict[str, float | None] = {
        "age_25_39_pct": None,
        "renter_share_pct": None,
        "multifamily_share_pct": None,
    }

    age = data.get("age_citywide", pd.DataFrame())
    if not age.empty and "Label (Grouping)" in age.columns:
        age["label"] = age["Label (Grouping)"].astype(str).str.strip()
        age["pct"] = age.get("District of Columbia!!Percent!!Estimate", "").apply(
            clean_number
        )
        age_25_39 = age[age["label"].isin(["25 to 29 years", "30 to 34 years", "35 to 39 years"])]
        context["age_25_39_pct"] = age_25_39["pct"].sum()

    rent_owner = data.get("rent_owner_citywide", pd.DataFrame())
    if not rent_owner.empty and "Label (Grouping)" in rent_owner.columns:
        rent_owner["label"] = rent_owner["Label (Grouping)"].astype(str).str.strip()
        total = rent_owner.loc[
            rent_owner["label"].eq("Total:"),
            "District of Columbia!!Estimate",
        ].apply(clean_number)
        renters = rent_owner.loc[
            rent_owner["label"].str.contains("Renter occupied", na=False),
            "District of Columbia!!Estimate",
        ].apply(clean_number)
        if not total.empty and not renters.empty and total.iloc[0]:
            context["renter_share_pct"] = renters.iloc[0] / total.iloc[0] * 100

    housing = data.get("housing_structure_citywide", pd.DataFrame())
    if not housing.empty and "Label (Grouping)" in housing.columns:
        housing["label"] = housing["Label (Grouping)"].astype(str).str.strip()
        percent_col = "District of Columbia!!Percent occupied housing units!!Estimate"
        multifamily_labels = [
            "2 apartments",
            "3 or 4 apartments",
            "5 to 9 apartments",
            "10 or more apartments",
            "10 to 19 apartments",
            "20 to 49 apartments",
            "50 or more apartments",
        ]
        if percent_col in housing:
            multifamily = housing[housing["label"].isin(multifamily_labels)]
            context["multifamily_share_pct"] = multifamily[percent_col].apply(
                clean_number
            ).sum()

    return context


def build_findings(
    dog_parks: pd.DataFrame,
    ward_summary: pd.DataFrame,
    context: dict[str, float | None],
) -> dict[str, Iterable[str]]:
    top_supply = ward_summary.sort_values("dog_park_count", ascending=False).head(3)
    low_supply = ward_summary.sort_values("dog_park_count", ascending=True).head(3)
    total_dog_parks = int(ward_summary["dog_park_count"].sum())

    bullets = [
        f"The local official Dog_Parks.csv file contains {total_dog_parks} dog parks.",
        (
            "The highest-count wards are "
            + ", ".join(
                f"{row.ward} ({int(row.dog_park_count)})"
                for row in top_supply.itertuples()
            )
            + "."
        ),
        (
            "The lowest-count wards are "
            + ", ".join(
                f"{row.ward} ({int(row.dog_park_count)})"
                for row in low_supply.itertuples()
            )
            + "."
        ),
    ]

    if context.get("renter_share_pct") is not None:
        bullets.append(
            f"Citywide ACS renter share is about {context['renter_share_pct']:.1f}%."
        )
    if context.get("age_25_39_pct") is not None:
        bullets.append(
            "Residents ages 25-39 make up about "
            f"{context['age_25_39_pct']:.1f}% of the citywide population."
        )
    if context.get("multifamily_share_pct") is not None:
        bullets.append(
            "Multifamily structures account for about "
            f"{context['multifamily_share_pct']:.1f}% of occupied housing units, "
            "a proxy for residents with less private outdoor space."
        )

    if not dog_parks.empty:
        median_size = dog_parks["SIZE_"].median()
        bullets.append(f"The median official dog park size is {median_size:,.0f} sq ft.")

    bullets.append(
        "Affordable housing units by ward are included as a local stress proxy; "
        "the next step is replacing this with tract-level ACS renter, income, "
        "poverty, car-free, race/ethnicity, and no-private-outdoor-space measures."
    )
    return {"bullets": bullets}


def run_analysis(data_dir: Path = PROJECT_DIR, output_dir: Path = OUTPUT_DIR) -> AnalysisOutputs:
    output_dir.mkdir(parents=True, exist_ok=True)

    data = load_local_data(data_dir)
    dog_parks = prepare_dog_parks(data["dog_parks"])
    ward_summary = summarize_ward_supply(dog_parks)
    ward_summary = add_affordable_housing_proxy(
        ward_summary, data["affordable_housing"]
    )
    ward_summary = add_green_space_context(
        ward_summary, data["community_gardens"], data["schools"]
    )

    context = citywide_context(data)
    findings = build_findings(dog_parks, ward_summary, context)

    ward_file = output_dir / "ward_dog_park_equity_summary.csv"
    ward_summary.to_csv(ward_file, index=False)
    tract_file = summarize_acs_economic(data["acs_economic"], output_dir)

    chart_files = [
        plot_dog_parks_by_ward(ward_summary, output_dir),
        plot_dog_park_area_by_ward(ward_summary, output_dir),
    ]
    optional_charts = [
        plot_supply_need_scatter(ward_summary, output_dir),
        plot_neighborhood_single_households(data["one_person_households"], output_dir),
    ]
    chart_files.extend(chart for chart in optional_charts if chart is not None)

    memo = write_findings_markdown(findings, output_dir)
    map_file = make_dog_park_leaflet_map(dog_parks, output_dir)

    return AnalysisOutputs(
        ward_summary=ward_file,
        tract_summary=tract_file,
        chart_files=chart_files,
        memo=memo,
        map_file=map_file,
    )


def main() -> None:
    outputs = run_analysis()
    print("DC dog park equity framework completed.")
    print(f"Ward summary: {outputs.ward_summary}")
    if outputs.tract_summary:
        print(f"Tract summary: {outputs.tract_summary}")
    for chart_file in outputs.chart_files:
        print(f"Chart: {chart_file}")
    print(f"Findings memo: {outputs.memo}")
    if outputs.map_file:
        print(f"Map: {outputs.map_file}")
    else:
        print("Map skipped: install folium to create the optional HTML map.")


if __name__ == "__main__":
    main()
