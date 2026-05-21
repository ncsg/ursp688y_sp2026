import pandas as pd
import geopandas as gpd
import glob
import os

def chunk_dataframe(df, chunk_size):
    df = df.copy()
    chunks = []
    number_chunks = len(df) // chunk_size + 1
    for i in range(number_chunks):
        chunks.append(df[i * chunk_size : (i + 1) * chunk_size])
    print(f'split dataframe into {len(chunks)} chunks')
    return chunks


def save_dfs_to_csv(dfs, output_dir='.', header=False):
    """Save each dataframe in a list (dfs) as a CSV stored in the output directory (output_dir)
    """
    # Create output directory if it doesn't exist.
    os.makedirs(output_dir, exist_ok=True)
    # Save each dataframe
    for i, df in enumerate(dfs):
        output_file = os.path.join(output_dir, f'df_{i}.csv')
        df.to_csv(output_file, header=header)

def combine_csvs(output_dir, header='infer', names=None):
    """Loads all CSV files from the given output folder and combine them into a single pandas DataFrame.

    Parameters:
        output_dir (str): Path to the directory containing the CSV files.

    Returns:
        pd.DataFrame: A DataFrame containing the combined data from all CSV files.

    Adapted from ChatGPT 03-mini-high queried with the following:
    "write a function that loads all the CSVs from the output folder and combines them into a single pandas dataframe"
    """
    # Use glob to get all CSV file paths in the output directory.
    csv_files = glob.glob(os.path.join(output_dir, "*.csv"))
    
    # Create a list to store individual DataFrames.
    dataframes = []
    
    # Loop through each file and read it into a DataFrame.
    for file in csv_files:
        try:
            df = pd.read_csv(file, header=header, names=names)
            dataframes.append(df)    
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    # Combine all DataFrames into one.
    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
        return combined_df
    else:
        print("No CSV files found or loaded.")
        return pd.DataFrame()

def lonlat_str_to_geodataframe(df, latlon_col):
    """Convert a dataframe with a column storing 'lat,lon' strings to a geodataframe with points
    """
    df = df.copy()
    lat_lon_columns = df[latlon_col].str.split(',', expand=True)
    lat_lon_columns = lat_lon_columns.rename(columns={0:'lon',1:'lat'})
    df = pd.concat([df, lat_lon_columns], axis=1)
    points = gpd.points_from_xy(df['lon'],df['lat'])
    return gpd.GeoDataFrame(df, geometry=points, crs=4326)
