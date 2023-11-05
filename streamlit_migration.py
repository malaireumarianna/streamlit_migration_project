import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_dynamic_filters import DynamicFilters

data = pd.read_csv('Canada.csv')
data_us = pd.read_csv('americabirthplace.csv')
map_data = pd.read_csv('world_country_and_usa_states_latitude_and_longitude_values.csv')


data.drop(columns = data.iloc[:,-8:].columns.tolist(), inplace=True)
data.drop(index = data.loc[data['AREA']==999].index.tolist(), inplace=True)
data.drop(index = data.loc[data['OdName']=='Russian Federation'].index.tolist(), inplace=True)

data_us.drop(index = data_us.loc[data_us['AREA']==999].index.tolist(), inplace=True)

# Reindex the Boolean Series to match the index of the DataFrame
#boolean_series = data_us['OdName'].eq('Russian Federation')
data_us.drop(index = data_us.loc[data_us['OdName']=='Russian Federation'].index.tolist(), inplace=True)
melted_df_us = data_us.melt(id_vars=['Type', 'Coverage', 'OdName','AREA', 'AreaName', 'REG', 'RegName','DEV','DevName'], var_name='Year', value_name='Value')

melted_df_us ['Value'].replace(['..', 'D','-'], 1, inplace=True)
melted_df_us = melted_df_us.merge(map_data, left_on='OdName', right_on='country')
melted_df_us.to_csv('melted_us.csv')



melted_df = data.melt(id_vars=['Type', 'Coverage', 'OdName','AREA', 'AreaName', 'REG', 'RegName','DEV','DevName'], var_name='Year', value_name='Value')
melted_df = melted_df.merge(map_data, left_on='OdName', right_on='country')

melted_df.to_csv('melted.csv')


st.set_page_config(initial_sidebar_state='collapsed', layout="wide")

#dynamic_filters = MultiFilter(melted_df, filters=['Year', 'RegName'])


with st.sidebar:
    st.write("Apply filters in any order 👇")

#dynamic_filters.display_filters(location='sidebar')

#dynamic_filters.display_df()
#filtered_df = dynamic_filters.filter(melted_df)

data_container = st.container()
# Streamlit app

selected_country = st.sidebar.selectbox("Select country", ["Canada", "America"])

if selected_country == "Canada":
    melted_df = melted_df
else:
    melted_df = melted_df_us


melted_df['Value'] = melted_df['Value'].astype(int)
# Filter by year

#selected_area = st.sidebar.selectbox("Select Area", melted_df['RegName'].unique())
selected_dev_name = st.sidebar.multiselect('Select Dev. Regions:', melted_df['DevName'].unique(), default=melted_df['DevName'].unique().tolist())
selected_area = st.sidebar.multiselect('Select Areas:', melted_df['RegName'].unique(), default=melted_df['RegName'].unique().tolist())
selected_year = st.sidebar.multiselect("Select Year", melted_df['Year'].unique(), default=melted_df['Year'].unique().tolist())

# Filter DataFrame by selected year
#filtered_df = melted_df[melted_df['Year'] == selected_year, melted_df['RegName'] == selected_area]
#filtered_df = melted_df[(melted_df['Year'].isin(selected_year)]
#& (melted_df['RegName'] == selected_area)]
#filtered_df = filtered_df[filtered_df['Area'].isin(selected_area)]

filtered_df = melted_df[(melted_df['Year'].isin(selected_year)) & (melted_df['RegName'].isin(selected_area)) & (melted_df['DevName'].isin(selected_dev_name))]
# Create pie chart
fig = px.pie(filtered_df, names='AreaName', values='Value')
fig1 = px.pie(filtered_df, names='RegName', values='Value')




# Display pie charts
with data_container:
    plot1, plot2 = st.columns(2)
    with plot1:
        st.title("Pie Chart for Area Values")
        st.plotly_chart(fig, use_container_width=True)
    with plot2:
        st.title("Pie Chart for Reg. Values")
        st.plotly_chart(fig1, use_container_width=True)

#filtered_df['Value'] = filtered_df.groupby(['Year', 'OdName'])['Value'].sum()

fig_bar = px.histogram(filtered_df, x="Year", y="Value",
                color="RegName",  title="Distibution of Regions by Year")

fig_bar.update_layout(xaxis=dict(rangeslider=dict(visible=True),
                             type="linear"), bargap=0.05)
st.plotly_chart(fig_bar, use_container_width=True)

#if we want to see accumulated sum for bar - barmode= 'overlay',
fig_bar1 = px.histogram(filtered_df, x="Year", y="Value",
                color="DevName", title="Distibution of Regions by Year")

fig_bar1.update_layout(xaxis=dict(rangeslider=dict(visible=True),
                             type="linear"), bargap=0.05)
st.plotly_chart(fig_bar1, use_container_width=True)

top_14_odnames = filtered_df.groupby(['OdName'])['Value'].sum().reset_index().sort_values(by=['Value'], ascending=False).head(14)
new_df = filtered_df[filtered_df['OdName'].isin(top_14_odnames['OdName'])]



fig2 = px.pie(new_df, names='OdName', values='Value',hole=.3 )
st.title("Top 14 countries with hightest migration rate")
st.plotly_chart(fig2, use_container_width=True)


# Calculate the top 10 OdNames by year
top_6_odnames = filtered_df.groupby(['OdName'])['Value'].sum().reset_index().sort_values(by=['Value'], ascending=False).head(6)
print(top_6_odnames)
new_df = filtered_df[filtered_df['OdName'].isin(top_6_odnames['OdName'])]


# Create a line chart
fig3 = px.line(new_df, x='Year', y='Value', color='OdName', symbol="OdName")
st.title("Top 6 contries with hightest emigration")
st.plotly_chart(fig3, use_container_width=True)

area_df = new_df[['Year','OdName','Value']]

fig4 = px.area(new_df, x='Year', y='Value', facet_col="OdName", facet_col_wrap=2, color="OdName")

st.plotly_chart(fig4, use_container_width=True)



fig5 = px.box(filtered_df, x='Year', y='Value')
#, facet_col="OdName", facet_col_wrap=2, color="OdName")
st.title("Top 6 contries with hightest emigration")
st.plotly_chart(fig5, use_container_width=True)





fig6 = px.scatter_geo(filtered_df, lat='latitude', lon='longitude', color="RegName",
                     hover_name="OdName", size="Value",
                     animation_frame="Year",
                     projection="natural earth")
st.plotly_chart(fig6, use_container_width=True)