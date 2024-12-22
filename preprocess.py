import pandas as pd

def preprocess():
    # Read the datasets again to avoid modifying global variables
    df = pd.read_csv('athlete_events.csv')
    region_df = pd.read_csv('noc_regions.csv')

    # Filter only Summer Olympics
    df = df[df['Season'] == 'Summer']

    # Rename columns in region_df to avoid conflicts
    region_df = region_df.rename(columns={'notes': 'region_notes', 'region': 'region_name'})

    # Perform the merge operation
    df = df.merge(region_df, on='NOC', how='left', suffixes=('_df', '_region'))

    # Drop duplicate columns after the merge
    df = df.loc[:, ~df.columns.duplicated()]

    # Add dummy variables for medals
    dummy_df = pd.get_dummies(df['Medal'], dtype=int)
    df = pd.concat([df, dummy_df], axis=1)

    # Drop duplicates in the final DataFrame
    df.drop_duplicates(inplace=True)

    return df
