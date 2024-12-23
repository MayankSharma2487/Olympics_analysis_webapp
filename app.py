import streamlit as st
import pandas as pd
import numpy as np
import helper
import preprocess
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
import plotly.graph_objects as go
from scipy.stats import gaussian_kde

# Load and preprocess the data
df = preprocess.preprocess()

st.sidebar.title('Olympics Analysis')

st.sidebar.image("https://images.unsplash.com/photo-1658581872509-c8d19777bd24?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8b2x5bXBpY3MlMjBsb2dvfGVufDB8fDB8fHww")

# Sidebar Menu
user_menu = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally', 'Overall Analysis', 'Country-Wise Analysis', 'Athlete-Wise Analysis')
)

# Debug: Display the dataframe (optional for large datasets)
st.write("Data Preview:")
st.text('YOU Can Touch(Mobile) or Hover(PC) on Graphs/charts to get more info these are intrective')
st.dataframe(df.head())

# Medal Tally
if user_menu == 'Medal Tally':

    st.sidebar.header('Medal Tally')
    years, countries = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox('Select Year', years, key="year_selectbox")
    selected_country = st.sidebar.selectbox('Select Country', countries, key="country_selectbox")


    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)
    title = "Medal Tally"
    if selected_year != 'Overall':
        title += f" in {selected_year} Olympics"
    if selected_country != 'Overall':
        title += f" for {selected_country}"

    st.title(title)
    st.write("### Full Medal Tally")
    # Ensure only numeric columns are formatted
    if not medal_tally.empty:
        numeric_columns = ["Gold", "Silver", "Bronze", "total"]  # Columns to format
        st.dataframe(
        medal_tally.style.format({col: "{:.0f}" for col in numeric_columns}).highlight_max(
            subset=numeric_columns, color="lightgreen"
        ),
        use_container_width=True
    )
    else:
        st.write("No data available for the selected filters.")





# Overall Analysis
elif user_menu == 'Overall Analysis':

    # Compute statistics
    editions = df['Year'].nunique() - 1  # Exclude 'Overall'
    cities = df['City'].nunique()
    sports = df['Sport'].nunique()
    events = df['Event'].nunique()
    athletes = df['Name'].nunique()
    nations = df['region_name'].nunique()

    st.title('Top Statistics')
    # Display statistics in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header('Editions')
        st.subheader(editions)

    with col2:
        st.header('Hosts')
        st.subheader(cities)

    with col3:
        st.header('Sports')
        st.subheader(sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header('Events')
        st.subheader(events)
    
    with col2:
        st.header('Nations')
        st.subheader(nations)
    
    with col3:
        st.header('Athletes')
        st.subheader(athletes)

    nations_over_time = helper.participating_nations_over_time(df)
    fig = px.line(nations_over_time, x = 'Edition',y = 'No. of Countries')
    st.title('Participating Nations Over the Years')
    st.plotly_chart(fig)

    events_over_time = helper.events_over_time(df)
    fig1 = px.line(events_over_time, x = 'Edition',y = 'No. of Events')
    st.title('Events Over Year')
    st.plotly_chart(fig1)

    athletes_over_time = helper.athletes_over_time(df)
    fig2 = px.line(athletes_over_time, x = 'Edition',y = 'No. of Athletes')
    st.title('Athletes Over Year')
    st.plotly_chart(fig2)


    st.title('No. of Events over time(Every sport)')
    fig, ax = plt.subplots(figsize=(20, 20))

    x = df.drop_duplicates(['Year','Sport','Event'])
    ax = x.pivot_table(index = 'Sport',columns = 'Year',values = 'Event',aggfunc = 'count').fillna(0).astype(int)
    sns.heatmap(ax,annot = True)
    st.pyplot(fig)

    st.title('Most Successful Athletes')
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0,'Overall')

    selected_sport = st.selectbox('Select a Sport',sport_list)

    x=helper.most_successful(df,selected_sport)
    st.table(x)


if user_menu == 'Country-Wise Analysis':
    st.sidebar.title('Country-Wise Analysis')

    country_list = df['region_name'].dropna().unique().tolist()
    country_list.sort()
    selected_country = st.sidebar.selectbox('Select a Country', country_list, key="country_selectbox1")
    
    # Year-wise medal tally
    year_wise_medal = helper.year_wise_medaltally(df, selected_country)
    fig = px.line(year_wise_medal, x='Year', y='Medal')
    st.title('Medals by Countries Over the Years')
    st.plotly_chart(fig)

    # Country-Sport heatmap
    st.title(f'{selected_country} Excels in The Following Sports')

    # Generate the pivot table
    pt = helper.country_event_heatmap(df, selected_country)
    
    if not pt.empty:  # Check if the pivot table is valid
        fig, ax = plt.subplots(figsize=(20, 20))
        sns.heatmap(pt, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax)
        st.pyplot(fig)
    else:
        st.write(f"No medal data available for {selected_country}")

    
    st.title('Most successful athletes of '+selected_country)
    top10_df = helper.most_successful_countrywise(df,selected_country)
    st.table(top10_df)

    if not top10_df.empty:  # Ensure the DataFrame is not empty
        fig = px.bar(
        top10_df,
        x='Name',  # Replace with the actual column name for athlete names
        y='Medals',  # Replace with the column name for the medal count
        color='Sport',  # Optional: Add color by sport if available
        title=f"Top 10 Most Successful Athletes of {selected_country}",
        labels={'Name': 'Athlete Name', 'Medals': 'Total Medals'},
        text='Medals',  # Show medal count on bars
        )
        fig.update_traces(textposition='outside')  # Position text outside bars
        st.plotly_chart(fig)
    else:
        st.write(f"No data available for athletes from {selected_country}.")


if user_menu == 'Athlete-Wise Analysis':

    athlete_df = df.drop_duplicates(subset = ['Name','region_name'])
    age = athlete_df['Age'].dropna().tolist()
    x1 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna().tolist()
    x2 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna().tolist()
    x3 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna().tolist()
    def compute_kde(data, x_range):
        kde = gaussian_kde(data)
        return kde(x_range)

# Define the x range for the density curves
    x_range = np.linspace(
        min(min(age), min(x1), min(x2), min(x3)), 
        max(max(age), max(x1), max(x2), max(x3)), 
        100
    )

# Compute KDE for each group
    age_kde = compute_kde(age, x_range)
    x1_kde = compute_kde(x1, x_range)
    x2_kde = compute_kde(x2, x_range)
    x3_kde = compute_kde(x3, x_range)

# Create the plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_range, y=age_kde, mode='lines', name='Overall Age'))
    fig.add_trace(go.Scatter(x=x_range, y=x1_kde, mode='lines', name='Gold Medalist Age'))
    fig.add_trace(go.Scatter(x=x_range, y=x2_kde, mode='lines', name='Silver Medalist Age'))
    fig.add_trace(go.Scatter(x=x_range, y=x3_kde, mode='lines', name='Bronze Medalist Age'))

    fig.update_layout(
        title="Age Distribution (Smooth Lines)",
        xaxis_title="Age",
        yaxis_title="Density",
        width=1000,
        height=600,
    )

    st.title('Distribution of Age')
    st.plotly_chart(fig)

    x = []
    name = []
    famous_sports = [
    "Basketball", "Judo", "Football", "Tug-Of-War", "Athletics",
    "Swimming", "Badminton", "Sailing", "Gymnastics",
    "Art Competitions", "Handball", "Weightlifting", "Wrestling",
    "Water Polo", "Hockey", "Rowing", "Fencing",
    "Shooting", "Boxing", "Taekwondo", "Cycling", "Diving", "Canoeing",
    "Tennis", "Golf", "Softball", "Archery",
    "Volleyball", "Synchronized Swimming", "Table Tennis", "Baseball",
    "Rhythmic Gymnastics", "Rugby Sevens",
    "Beach Volleyball", "Triathlon", "Rugby", "Polo", "Ice Hockey"
    ]

    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        x.append(temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna().tolist())  # Convert to list
        name.append(sport)

# Initialize the figure
    fig = go.Figure()

# Add KDE lines for each sport
    for i, data in enumerate(x):
        if len(data) > 0:  # Ensure data is not empty to avoid errors
            kde = gaussian_kde(data)
            x_range = np.linspace(min(data), max(data), 100)  # Define the range for the KDE
            density = kde(x_range)

        # Add a trace for this sport
            fig.add_trace(go.Scatter(x=x_range, y=density, mode='lines', name=name[i]))

# Update layout
    fig.update_layout(
        title="Age Distribution of Athletes Winning Gold (Line Plot)",
        xaxis_title="Age",
        yaxis_title="Density",
        autosize=False,
        width=1000,
        height=600,
    )

# Display the plot
    st.title('Age Distribution of Athletes WRT Sports (Winning Gold )')
    st.plotly_chart(fig)

    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0,'Overall')

    selected_sport = st.selectbox('Select a Sport',sport_list)

    temp_df = helper.weight_v_height(df,selected_sport)
    fig,ax = plt.subplots()
    ax = sns.scatterplot(x='Weight', y='Height', data=temp_df,hue=temp_df['Medal'],style=temp_df['Sex'],s=110)
    st.pyplot(fig)

    final = helper.men_v_women(df)
    fig = px.line(final,x='Year',y=['Male','Female'])
    st.title('Men Vs Women Participants Over The Years')
    st.plotly_chart(fig)

sticky_footer = """
<style>
footer {
    visibility: hidden;
}
div.stMarkdown > div {
    position: fixed;
    bottom: 10px;
    left: 0;
    width: 100%;
    background-color: #f1f1f1;
    color: black;
    text-align: center;
    padding: 10px;
    font-size: 14px;
    border-top: 1px solid #eaeaea;
}
</style>
<div>
    Created by <a href="https://github.com/your-profile" target="_blank">Your Name</a> | © 2024 All rights reserved.
</div>
"""
st.markdown(sticky_footer, unsafe_allow_html=True)