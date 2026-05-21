import os
import pandas as pd
import utils


# warrants_df['EventDate'] = pd.to_datetime(warrants_df['EventDate'])
# warrants_df['EventDate'] = pd.to_datetime(warrants_df['EventDate'])
# warrants_df['TenantZipCode'] = warrants_df['TenantZipCode'].astype('Int64').astype('string')

def prep_warrants_for_geocoding(df):

    # Operate on a copy of the dataframe
    # (this ensures that changes to the df made within this function don't
    # percolate into the df object in the parent namespace)
    df = df.copy()
    
    print(f'{len(df)} warrants input')

    # Ensure zip codes are stored as strings without decimal places
    df['TenantZipCode'] = df['TenantZipCode'].astype('Int64').astype('string')
    
    # Reduce to unique addresses to economize geocoding
    df = df.drop_duplicates(['TenantAddress','TenantCity','TenantState','TenantZipCode'])

    print(f'Reduced to {len(df)} unique addresses')

    # Make sure the row index indices provide unique IDs
    df = df.reset_index(drop=True) # Makes a fresh index with unique sequential values

    # Reduce to columns required for geocoding
    df = df[['TenantAddress','TenantCity','TenantState','TenantZipCode']]

    return df

def combine_census_geocoded_csvs(output_dir):
    return utils.combine_csvs(
        output_dir,
        header=None, 
        names=[
            'unique_id',
            'input_address',
            'match_status',
            'match_type',
            'match_address',
            'match_lon_lat',
            'match_tiger_line_id',
            'match_tiger_line_side',
        ]
    )
    

    