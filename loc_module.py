


######################
# Import libraries
######################
import numpy as np
import pandas as pd
import json
import geocoder
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
import requests
import streamlit as st
import altair as alt
from pandas.io.json import json_normalize
from PIL import Image
import matplotlib.cm as cm
import matplotlib.colors as colors
from streamlit_folium import folium_static
import folium
from sklearn.cluster import KMeans
import requests # library to handle requests


def app():
    image = Image.open('LOCATION PREDICTION.png')
    
    st.image(image, use_column_width=True)
    
    st.write("""
    # LOCATION PREDICTION
    THIS APP **_PREDICTS THE SUITABLE LOCATION_** FOR OPENING A RESTAURANT
    ***
    """)
    
   
    st.write("""## NEIGHBOURHOOD DATA""")
    
    
    

    data = requests.get("https://en.wikipedia.org/wiki/Category:Neighbourhoods_in_Delhi").text
    soup = BeautifulSoup(data, 'html.parser')
    neighborhoodList = []
    for row in soup.find_all("div", class_="mw-category")[0].findAll("li"):
        neighborhoodList.append(row.text)
    neighborhoodList.pop(0)

    kl_df = pd.DataFrame({"Neighborhood": neighborhoodList})


    def get_latlng(neighborhood):
        # initialize your variable to None
        lat_lng_coords = None
        # loop until you get the coordinates
        while(lat_lng_coords is None):
            g = geocoder.arcgis('{}, Delhi, India'.format(neighborhood))
            lat_lng_coords = g.latlng
        return lat_lng_coords

    coords = [ get_latlng(neighborhood) for neighborhood in kl_df["Neighborhood"].tolist() ]

    df_coords = pd.DataFrame(coords, columns=['Latitude', 'Longitude'])
    kl_df['Latitude'] = df_coords['Latitude']
    kl_df['Longitude'] = df_coords['Longitude']


    address = 'New Delhi,India'

    geolocator = Nominatim(user_agent="http")
    location = geolocator.geocode(address)
    latitude = location.latitude
    longitude = location.longitude# create map of Delhi using latitude and longitude values
    map_kl = folium.Map(location=[latitude, longitude], zoom_start=11)


    st.write('The geograpical coordinate of Delhi,India {}, {}.'.format(latitude, longitude))




    
    
    
    
    
    # add markers to map
    for lat, lng, neighborhood in zip(kl_df['Latitude'],kl_df['Longitude'],kl_df['Neighborhood']):
         label = '{}'.format(neighborhood)
         label = folium.Popup(label, parse_html=True)
         folium.CircleMarker(
             [lat, lng],
             radius=5,
             popup=label,
             color='blue',
             fill=True,
             fill_color='#3186cc',
             fill_opacity=0.7).add_to(map_kl)  
          
    
          
    
    folium_static(map_kl)


    CLIENT_ID = '0KREV0N02JYICMYPCGBXI1WIVWA0J5Y5ETH52S5ZMBHSTFUV' # your Foursquare ID
    CLIENT_SECRET = 'UTWX0N0TTMPP0YRZ5VWWUMAHJXW5XFIF0XLDLPZWQCH0MLTM' # your Foursquare Secret
    VERSION = '201900731'



    radius = 2000
    LIMIT = 100

    venues = []

    for lat, long, neighborhood in zip(kl_df['Latitude'], kl_df['Longitude'], kl_df['Neighborhood']):
    
        # create the API request URL
        url = "https://api.foursquare.com/v2/venues/explore?client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}".format(
            CLIENT_ID,
            CLIENT_SECRET,
            VERSION,
            lat,
            long,
            radius, 
            LIMIT)
    
        # make the GET request
        results = requests.get(url).json()['response']['groups'][0]['items']
        # return only relevant information for each nearby venue
        for venue in results:
            venues.append((
                neighborhood,
                lat, 
                long, 
                venue['venue']['name'], 
                venue['venue']['location']['lat'], 
                venue['venue']['location']['lng'],  
                venue['venue']['categories'][0]['name']))
        
        
        
    venues_df = pd.DataFrame(venues)

    # define the column names
    venues_df.columns = ['Neighborhood', 'Latitude', 'Longitude', 'VenueName', 'VenueLatitude', 'VenueLongitude', 'VenueCategory']




    # one hot encoding
    kl_onehot = pd.get_dummies(venues_df[['VenueCategory']], prefix="", prefix_sep="")

    # add neighborhood column back to dataframe
    kl_onehot['Neighborhoods'] = venues_df['Neighborhood'] 

    # move neighborhood column to the first column
    fixed_columns = [kl_onehot.columns[-1]] + list(kl_onehot.columns[:-1])
    kl_onehot = kl_onehot[fixed_columns]


    kl_grouped = kl_onehot.groupby(["Neighborhoods"]).mean().reset_index()


    kl_mall = kl_grouped[["Neighborhoods","Restaurant"]]


    # set number of clusters
    kclusters = 3

    kl_clustering = kl_mall.drop(["Neighborhoods"], 1)

    # run k-means clustering
    kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(kl_clustering)

    # create a new dataframe that includes the cluster as well as the top 10 venues for each neighborhood.
    kl_merged = kl_mall.copy()

    # add clustering labels
    kl_merged["Cluster Labels"] = kmeans.labels_

    kl_merged.rename(columns={"Neighborhoods": "Neighborhood"}, inplace=True)


    # merge city_grouped with city_data to add latitude/longitude for each neighborhood
    kl_merged = kl_merged.join(kl_df.set_index("Neighborhood"), on="Neighborhood")

    kl_merged.sort_values(["Cluster Labels"], inplace=True)



    # create map
    map_clusters = folium.Map(location=[28.6138954, 77.2090057], zoom_start=11)

    # set color scheme for the clusters
    x = np.arange(kclusters)
    ys = [i+x+(i*x)**2 for i in range(kclusters)]
    colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
    rainbow = [colors.rgb2hex(i) for i in colors_array]

    # add markers to the map
    markers_colors = []
    for lat, lon, poi, cluster in zip(kl_merged['Latitude'], kl_merged['Longitude'], kl_merged['Neighborhood'], kl_merged['Cluster Labels']):
        label = folium.Popup(str(poi) + ' - Cluster ' + str(cluster), parse_html=True)
        folium.CircleMarker(
            
            [lat, lon],
            radius=5,
            popup=label,
            color=rainbow[cluster-1],
            fill=True,
            fill_color=rainbow[cluster-1],
            fill_opacity=0.7).add_to(map_clusters)
    
    
       

    folium_static(map_clusters)
    
    st.write("[Click to open xyz sales report](https://share.streamlit.io/your/app/link)")

 
    








