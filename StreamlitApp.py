import streamlit as st 
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px


DATA_URL = (
    "C:/Users/blaze/OneDrive/Desktop/Streamlit/Motor_Vehicle_Collisions_-_Crashes_20240221.csv"
)

st.title("Motor Vehicle Collision Analysis for New York City")
st.markdown("This application is a streamlit dashboard to analyze and visualize "
            "motor vehile collisions in New York City.🗽🚘💥")

@st.cache_data     #Use of streamlit smart cache to improve runtimes
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates = [['CRASH DATE', 'CRASH TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash date_crash time': 'Date/Time'}, inplace=True)
    data.rename(columns={'number of persons injured': 'injured_persons'}, inplace=True)
    return data


data = load_data(300000)

#Transform column names
dict = {'on street name':'on_street_name',
        'cross street name': 'cross_street',
        'off street name':'off_street',
        'number of persons killed': 'persons_killed',
        'number of pedestrians injured':'injured_pedestrians',
        'number of pedestrians killed':'killed_pedestrians',
        'number of cyclist injured':'injured_cyclist',
        'number of cyclist killed':'killed_cyclist',
        'number of motorist injured':'injured_motorist',
        'number of motorist killed':'killed_motorist',
        'zip code':'zipcode'
        }

data.rename(columns=dict, inplace=True)
orig_data = data #Creating a copy of original data

st.header("Where are the most people injured in New York City?")
injuries = st.slider("Number of people injured", 0, 25)
st.map(data.query("injured_persons >= @injuries")[["latitude", "longitude"]].dropna(how="any"))


st.header("How many vehicle collisions occur at a particular hour in NYC?")
hour = st.slider("Hour to inspect", 0, 23)
data = data[data['Date/Time'].dt.hour==hour] 

st.markdown("Vehicle Collisions between %i:00 and %i:00" % (hour, (hour+1) % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))


#Using pydeck to create a 3D visualization
st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 8,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data = data[['Date/Time', 'latitude', 'longitude']],
            get_position = ['longitude','latitude'],
            radius = 100,
            extruded=True,
            pickable=True,
            elevation_scale = 50,
            elevation_range=[0, 1000],
        ),
    ],
))

st.subheader("Breakdown of collisions by minute between %i:00 and %i:00" % (hour, (hour+1) % 24))
filtered=data[
    (data['Date/Time'].dt.hour >= hour) & (data['Date/Time'].dt.hour < (hour+1))
]


hist = np.histogram(filtered['Date/Time'].dt.minute, bins = 60, range = (0, 60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes':hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height = 400)
st.write(fig)


st.header("Top 10 dangerous streets by affected type")
select = st.selectbox('Affected type of people', ['Pedestrian', 'Cyclist', 'Motorist'])

if select == 'Pedestrian':
    st.write(orig_data.query("injured_pedestrians >= 1")[['on_street_name', 'injured_pedestrians']].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how='any')[:10])
    
elif select == 'Cyclist':
    st.write(orig_data.query("injured_cyclist >= 1")[['on_street_name', 'injured_cyclist']].sort_values(by=['injured_cyclist'], ascending=False).dropna(how='any')[:10])

else:
    st.write(orig_data.query("injured_motorist >= 1")[['on_street_name', 'injured_motorist']].sort_values(by=['injured_motorist'], ascending=False).dropna(how='any')[:10])



if st.checkbox("Show Raw Data", False):
    st.subheader("Raw_Data")
    st.write(data)












    
    
    
    


