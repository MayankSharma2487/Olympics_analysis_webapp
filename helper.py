import numpy as np

def medal_tally(df):
    medal_tally = df.drop_duplicates(subset=['Team','NOC','Games','Year','City','Sport','Event','Medal'])
    medal_tally = medal_tally.groupby('NOC').sum()[['Gold','Silver','Bronze']].sort_values('Gold',ascending=False).reset_index()

    medal_tally['total'] = medal_tally['Gold'] +  medal_tally['Silver'] +  medal_tally['Bronze']

    return medal_tally

def country_year_list(df):
    years = df['Year'].unique().tolist()
    years.sort()
    years.insert(0,'Overall')

    country = np.unique(df['region_name'].dropna().values).tolist()
    country.sort()
    country.insert(0,'Overall')

    return years,country

def fetch_medal_tally(df, year, country):
    medal_df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    flag = 0
    temp_df = None  # Initialize temp_df to avoid UnboundLocalError
    
    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df
        
    elif year == 'Overall' and country != 'Overall':
        flag = 1
        temp_df = medal_df[medal_df['region_name'] == country]
        
    elif year != 'Overall' and country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]
        
    elif year != 'Overall' and country != 'Overall':
        temp_df = medal_df[(medal_df['Year'] == int(year)) & (medal_df['region_name'] == country)]
    
    # If temp_df is not initialized, raise an error for debugging
    if temp_df is None:
        raise ValueError("temp_df was not initialized. Check your input values for year and country.")
    
    if flag == 1:   
        x = temp_df.groupby('Year').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Year').reset_index()
    else:
        x = temp_df.groupby('region_name').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold', ascending=False).reset_index()

    x['total'] = x['Gold'] + x['Silver'] + x['Bronze']
    
    return x


def participating_nations_over_time(df):
    nations_over_time = df.drop_duplicates(['Year','region_name'])['Year'].value_counts().reset_index().sort_values('Year')
    nations_over_time.rename(columns={'Year':'Edition','count': 'No. of Countries'},inplace = True)

    return nations_over_time

def events_over_time(df):
    Events_over_time = df.drop_duplicates(['Year','Event'])['Year'].value_counts().reset_index().sort_values('Year')
    Events_over_time.rename(columns={'Year':'Edition','count': 'No. of Events'},inplace = True)

    return Events_over_time

def athletes_over_time(df):
    athletes_over_time = df.drop_duplicates(['Year','Name'])['Year'].value_counts().reset_index().sort_values('Year')
    athletes_over_time.rename(columns={'Year':'Edition','count': 'No. of Athletes'},inplace = True)

    return athletes_over_time

def most_successful(df, sport):
    # Drop rows where 'Medal' is NaN
    temp_df = df.dropna(subset=['Medal'])
    
    # Filter by sport if not 'Overall'
    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]
    
    # Get the top 15 athletes by medal count
    top_athletes = (
        temp_df['Name']
        .value_counts()
        .reset_index()
        .rename(columns={'index': 'Name', 'count': 'Medals'})  # Renamed 'count' to 'medals'
        .head(15)
    )
    
    # Merge with the original DataFrame to get additional details
    merged_df = top_athletes.merge(df, on='Name', how='left')[['Name', 'Medals', 'Sport', 'region_name']]
    
    # Drop duplicates to keep only the relevant rows
    return merged_df.drop_duplicates(subset=['Name'])



def year_wise_medaltally(df,country):
    temp_df = df.dropna(subset = ['Medal'])
    temp_df.drop_duplicates(subset=['Team','NOC','Games','Year','City','Sport','Event','Medal'],inplace = True)

    new_df = temp_df[temp_df['region_name']== country]
    final_df = new_df.groupby('Year').count()['Medal'].reset_index()

    return final_df

def country_event_heatmap(df, country):
    # Drop rows where 'Medal' is NaN
    temp_df = df.dropna(subset=['Medal'])
    
    # Drop duplicates to ensure unique records
    temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'], inplace=True)
    
    # Filter for the specific country
    new_df = temp_df[temp_df['region_name'] == country]
    
    # Create a pivot table with Sports as rows and Years as columns
    pt = new_df.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0)
    
    return pt

def most_successful_countrywise(df, country):
    # Drop rows where 'Medal' is NaN
    temp_df = df.dropna(subset=['Medal'])


    temp_df = temp_df[temp_df['region_name'] == country]
    
    # Get the top 15 athletes by medal count
    top_athletes = (
        temp_df['Name']
        .value_counts()
        .reset_index()
        .rename(columns={'index': 'Name', 'count': 'Medals'})  # Renamed 'count' to 'medals'
        .head(15)
    )
    
    # Merge with the original DataFrame to get additional details
    merged_df = top_athletes.merge(df, on='Name', how='left')[['Name', 'Medals', 'Sport']]
    
    # Drop duplicates to keep only  the relevant rows
    return merged_df.drop_duplicates(subset=['Name'])

def weight_v_height(df,sport):
    athlete_df = df.drop_duplicates(subset = ['Name','region_name'])
    athlete_df['Medal'].fillna('No Medal',inplace=True)
    if sport != 'Overall':
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        return temp_df
    else:
        return athlete_df
    

def men_v_women(df):
    athlete_df = df.drop_duplicates(subset = ['Name','region_name'])
    men = athlete_df[athlete_df['Sex']=='M'].groupby('Year').count()['Name'].reset_index()
    women = athlete_df[athlete_df['Sex']=='F'].groupby('Year').count()['Name'].reset_index()
    final = men.merge(women,on='Year',how='left')
    final.rename(columns={'Name_x':'Male','Name_y':'Female'},inplace=True)
    final.fillna(0,inplace=True)

    return final