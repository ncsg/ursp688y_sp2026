import requests
import geopandas as gpd
import pandas as pd
import numpy as np

UTM18 = 26918

def load_tracts():
    """Load tracts from geojson and return as geodataframe
    """
    # Load tracts and clean up table with only the columns we need
    tracts_gdf = gpd.read_file('dc_tracts.geojson')
    tracts_gdf = tracts_gdf[tracts_gdf.geoid.str.len() == 18]
    tracts_gdf = tracts_gdf.rename(columns={
        'geoid':'tract_id',
        'B01003001':'pop'
    })
    tracts_gdf =tracts_gdf[['tract_id','pop','geometry']]
    return tracts_gdf

def load_nbhds():
    """Load neighborhood points from geojson and return as geodataframe
    """
    nbhds_gdf = gpd.read_file('dc_neighborhood_points.geojson')
    nbhds_gdf = nbhds_gdf[['NAME','geometry']].rename(columns={'NAME':'nbhd'})
    return nbhds_gdf

def load_bike_data():
    """Load bikes and stations from CABI API and return as two geodataframes
    """
    bikes_json = requests.get('https://gbfs.lyft.com/gbfs/2.3/dca-cabi/en/free_bike_status.json').json()
    station_status_json = requests.get('https://gbfs.lyft.com/gbfs/2.3/dca-cabi/en/station_status.json').json()
    station_info_json = requests.get('https://gbfs.lyft.com/gbfs/2.3/dca-cabi/en/station_information.json').json()
    
    # Bikes (only includes ebikes)
    bikes_df = pd.DataFrame(bikes_json['data']['bikes'])
    bikes_df['timestamp'] = bikes_json['last_updated']
    bikes_df['timestamp'] = pd.to_datetime(bikes_df['timestamp'], unit='s')
    bikes_gdf = gpd.GeoDataFrame(
        bikes_df, 
        geometry=gpd.points_from_xy(bikes_df.lon, bikes_df.lat), 
        crs=4326
    )
    bikes_gdf['vehicle_type_id'] = bikes_gdf['vehicle_type_id'].astype(int)
    
    # Stations (includes both e-bikes and regular bikes)
    station_status_df = pd.DataFrame(station_status_json['data']['stations'])    
    station_info_df = pd.DataFrame(station_info_json['data']['stations'])
    stations_df = station_status_df.merge(station_info_df, on='station_id')
    stations_df = stations_df.rename(columns={'last_reported':'timestamp'})
    stations_df['timestamp'] = pd.to_datetime(stations_df['timestamp'], unit='s')
    stations_gdf = gpd.GeoDataFrame(
        stations_df, 
        geometry=gpd.points_from_xy(stations_df.lon, stations_df.lat), 
        crs=4326
    )    
    return bikes_gdf, stations_gdf

def expand_stations_into_bikes(stations_gdf):
    station_bikes = []
    for row in stations_gdf.itertuples():
        for vehicle_type in row.vehicle_types_available:
            for i in range(int(vehicle_type['count'])):
                station_bikes.append({
                    'lat':row.lat,
                    'lon':row.lon,
                    'vehicle_type_id':int(vehicle_type['vehicle_type_id']),
                    'station_id':row.station_id,
                    'timestamp': row.timestamp,
                    'geometry': row.geometry,
                }) 
    return gpd.GeoDataFrame(pd.DataFrame(station_bikes), geometry='geometry', crs=4326)

def attach_points_to_points(gdf_a, gdf_b):
    """Spatially join points in one gdf to the closest point in another gdf
    """
    gdf_a = gpd.sjoin_nearest(gdf_a.to_crs(UTM18), gdf_b.to_crs(UTM18))
    gdf_a = gdf_a.drop(columns='index_right')
    return gdf_a.to_crs(4326)

def count_bikes_per_nbhd(bikes_gdf):
    bikes_gdf = bikes_gdf.copy()
    bikes_gdf['eea'] = (bikes_gdf['eea_idx'] > 0).astype(int)
    bikes_per_nbhd = bikes_gdf.groupby('nbhd').agg({
        'vehicle_type_id':'count',
        'eea':'max',
        }).rename(columns={
        'vehicle_type_id':'bikes'
        })
    bikes_per_nbhd = bikes_per_nbhd.sort_values('bikes', ascending=False)
    return bikes_per_nbhd

# Attach counts to nbhd points
def attach_counts_to_nbhd_points(bikes_per_nbhd_df, nbhds_gdf):
     return nbhds_gdf.merge(bikes_per_nbhd_df, left_on='nbhd', right_index=True)

def proportional_circles_radii(values, multiplier=1):
    """Calculate radii of proportional circles from a column of values given a multiplier
    """
    return np.sqrt(values / 3.14) * multiplier

def polygons_to_points(polgyon_gdf, calc_crs=UTM18):
    initial_crs = polgyon_gdf.crs
    point_gdf = polgyon_gdf.copy()
    point_gdf = point_gdf.to_crs(calc_crs)
    point_gdf['geometry'] = point_gdf.centroid
    point_gdf = point_gdf.to_crs(initial_crs)
    return point_gdf

def get_gdf_midpoint(gdf):
    """
    Calculate the midpoint of the x and y extents of a GeoDataFrame
    """
    # Get the total bounds: (minx, miny, maxx, maxy)
    minx, miny, maxx, maxy = gdf.total_bounds
    
    # Calculate midpoint values for x and y coordinates.
    mid_x = (minx + maxx) / 2
    mid_y = (miny + maxy) / 2
    
    return float(mid_x), float(mid_y)

def int_at_least_one(num):
    num = int(num)
    if num < 1:
        num = 1
    return num

def filter_bikes(bikes_gdf, filters_dict):
    bikes_gdf = bikes_gdf.copy()
    for field, values in filters_dict.items():
        bikes_gdf = bikes_gdf[bikes_gdf[field].isin(values)]
    return bikes_gdf

def reformat_eea_census_tract_ids(eea_df):
    eea_df = eea_df.copy()
    eea_df['tract_id'] = eea_df['tract_id'].str.split(' ').str[-1].astype(float).apply(lambda x: '{:.2f}'.format(x)).astype(str).str.replace('.','').str.zfill(6)
    eea_df['tract_id'] = '14000US11001' + eea_df['tract_id']
    return eea_df

def clean_eea(eea_df):
    eea_df = eea_df.copy()
    eea_df = eea_df[eea_df.Jurisdiction == 'District of Columbia']
    columns = {
        'Census Tract':'tract_id',
        'EEA Total Index':'eea_idx',
        'Concentration Low-Income':'eea_low_income',
        'Concentration African American or Black':'eea_black',
        'Concentration Hispanic or Latino':'eea_hisp',
        'Concentration Asian':'eea_asian',
    }
    eea_df = eea_df.rename(columns=columns)
    eea_df =eea_df[columns.values()]
    eea_df = reformat_eea_census_tract_ids(eea_df)
    return eea_df

def w_avg(df, values, weights):
    """Calculate average across values column weighted by weights column
    """
    d = df[values]
    w = df[weights]
    return (d * w).sum() / w.sum()

def add_tract_data_to_nbhds(nbhds_gdf, tracts_gdf):
    nbhds_gdf = nbhds_gdf.copy()
    tracts_gdf = tracts_gdf.copy()
    
    # Attach tract data to the closest neighborhood point
    tract_points_by_neighborhood = attach_points_to_points(polygons_to_points(tracts_gdf), nbhds_gdf)

    # Calculate sum of population and weighted averages of eea indices per neighborhood
    nbhds_gdf = nbhds_gdf.set_index('nbhd')
    nbhds_gdf = pd.concat([nbhds_gdf, tract_points_by_neighborhood.groupby('nbhd').pop.sum()], axis=1)
    for col in ['eea_idx','eea_low_income','eea_black','eea_hisp','eea_asian']:
    
        weighted_average = tract_points_by_neighborhood.groupby('nbhd').apply(w_avg, col, 'pop', include_groups=False)
        weighted_average.name = col
        nbhds_gdf = pd.concat([nbhds_gdf, weighted_average], axis=1)
    
    # Drop rows with no population (didn't join to tracts)
    nbhds_gdf = nbhds_gdf[nbhds_gdf['pop'] > 0]

    return nbhds_gdf.reset_index()