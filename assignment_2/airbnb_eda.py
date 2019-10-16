import os

import streamlit as st

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

import plotly.express as px

# get mapbox token
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
if MAPBOX_TOKEN is None:
    MAPBOX_TOKEN="pk.eyJ1Ijoia2hhbGlkbzc5IiwiYSI6ImNqbGQzejBpOTAzcWczd3F6ZXFucmd0b3kifQ._SbczGYo_NXU7CNJxTPuzw"

px.set_mapbox_access_token(MAPBOX_TOKEN)


st.title("AirBnb NYC EDA")

# reading in the dataset and initial munging

@st.cache
def load_data(fraction=0.2):
    df = pd.read_csv("AB_NYC_2019.csv")

    #df.rename(columns={'neighbourhood_group': 'n_group'}, inplace=True)

    # parsing dates and making a year and month col
    df['last_review'] = pd.to_datetime(df['last_review'], format="%Y-%m-%d")
    df['year'] = df['last_review'].dt.year.astype("Int64")
    df['month'] = df['last_review'].dt.month.astype("Int64")
    df['day'] = df['last_review'].dt.day.astype("Int64")
    return df.dropna().sample(frac=fraction)

df = load_data(fraction=0.1)

st.header('Data')

n_groups = list(df.neighbourhood_group.unique())
neighbourhood_group = st.multiselect(label="Select Neighbourhood Groups", 
options=n_groups, default=n_groups)

(min_price, max_price) = st.slider("Price Range", min_value=0, max_value=df.price.max(),
value=(0,300))
st.write(f"Min Price: {min_price}, Max Price: {max_price}")

df = df.query("neighbourhood_group == @neighbourhood_group and @min_price < price < @max_price")

st.text(f'Looking at {df.shape[0]:,} rows selected using above options')
st.dataframe(df.head(5))

st.header("Price ")

fig = px.scatter(df.query("price < 2000"), x="year", y="price", color="room_type",  
                title="Price over years with price outliers removed")

#fig.update_layout(legend_orientation='h')

st.plotly_chart(fig)

st.header("Map of Listings")
st.subheader("Listings")

midpoint = (np.average(df["latitude"]), np.average(df["longitude"]))

st.deck_gl_chart(
    viewport={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 12,
        "pitch": 50,
    },
    layers=[
        {
            "type": "HexagonLayer",
            "data": df,
            "radius": 100,
            "elevationScale": 4,
            "elevationRange": [0, 1000],
            "pickable": True,
            "extruded": True,
        }
    ],
)

st.subheader("Map")

fig = px.scatter_mapbox(df, lat='latitude', lon='longitude', size='number_of_reviews', 
color='reviews_per_month', width=800, height=600,
                   size_max=20, zoom=10)

st.plotly_chart(fig)

# skjdhfsd
st.header("Metrics")

# setting up the plots
fig, (ax, ax1) = plt.subplots(2, 1, figsize=(18,8))
plt.subplots_adjust(hspace=0.35)
sns.set_style("white")
hist_kws = dict(alpha=0.2)

ax.set_title("Price distribution for the different room types (outliers removed)", fontsize=18)

for room in df.room_type.unique():
    dat = df.query("room_type == @room and price<600")
    sns.distplot(dat.price, ax=ax, label=f"{room}", 
                 hist_kws=hist_kws)

ax.legend(fontsize=16)

ax1.set_title("Price distribution for the different room types", fontsize=18)

for room in df.room_type.unique():
    dat = df.query("room_type == @room")
    sns.distplot(dat.price, ax=ax1, label=f"{room}", hist_kws=hist_kws)
    
st.pyplot()