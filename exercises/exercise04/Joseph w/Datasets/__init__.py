"""Visualization helpers for the DC dog park equity framework."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from charts import (
    plot_dog_park_area_by_ward,
    plot_dog_parks_by_ward,
    plot_neighborhood_single_households,
    plot_supply_need_scatter,
    write_findings_markdown,
)


def make_dog_park_leaflet_map(
    dog_parks: pd.DataFrame, output_dir: Path | str, filename: str = "dog_parks_map.html"
) -> Path | None:
    """Create a simple Folium map when folium is installed.

    This is intentionally optional so the rest of the framework works in a
    lightweight class environment with only pandas and matplotlib.
    """
    if dog_parks.empty or not {"LATITUDE", "LONGITUDE"}.issubset(dog_parks.columns):
        return None

    try:
        import folium
    except ImportError:
        return None

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    center = [dog_parks["LATITUDE"].mean(), dog_parks["LONGITUDE"].mean()]
    dc_map = folium.Map(location=center, zoom_start=12, tiles="CartoDB positron")

    for _, row in dog_parks.iterrows():
        popup_parts = [
            str(row.get("NAME", "Dog park")),
            str(row.get("ADDRESS", "")),
            f"Ward {row.get('WARD', '')}",
            f"{row.get('SIZE_', 0):,.0f} sq ft",
        ]
        folium.CircleMarker(
            location=[row["LATITUDE"], row["LONGITUDE"]],
            radius=6,
            color="#2374ab",
            fill=True,
            fill_color="#db7c26",
            fill_opacity=0.85,
            popup="<br>".join(part for part in popup_parts if part),
        ).add_to(dc_map)

    map_file = output_path / filename
    dc_map.save(map_file)
    return map_file


__all__ = [
    "make_dog_park_leaflet_map",
    "plot_dog_park_area_by_ward",
    "plot_dog_parks_by_ward",
    "plot_neighborhood_single_households",
    "plot_supply_need_scatter",
    "write_findings_markdown",
]
