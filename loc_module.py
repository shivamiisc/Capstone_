######################
# Import libraries
######################
import numpy as np
import pandas as pd
import json
import geocoder
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from opencage.geocoder import OpenCageGeocode
import requests
import streamlit as st
import time
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
    
   
    


    val = st.text_input("Enter Wikipedia Page link for location data : ")
    City= st.text_input("enter City")


    

    
    def scraping():
            data = requests.get(val).text
            soup = BeautifulSoup(data, 'html.parser')
            neighborhoodList = []
            # append the data into the list
            for row in soup.find_all("div", class_="mw-category")[0].findAll("li"):
                neighborhoodList.append(row.text)
    
            # create a new DataFrame from the list
            kl_df = pd.DataFrame({"Neighborhood": neighborhoodList})

            st.write(""" Data Frame scraped from the Wikipedia. """)
            st.dataframe(kl_df)
            
                           
    

    
            key = 'c1c41ad8b5ea4137bace4778fd7aee18'  # get api key from:  https://opencagedata.com
            geocoder = OpenCageGeocode(key)

            with st.spinner('Wait for it... it make 2-5 minutes'):
                time.sleep(5)
 
  
                list_lat = []   # create empty lists
                list_long = []

                for index, row in kl_df.iterrows(): # iterate over rows in dataframe
                    Neighborhood = row['Neighborhood'] 
    
                    query = str(Neighborhood)+','+str(City)
     
                    results = geocoder.geocode(query)
                    if(results==[]):
                        list_lat.append(np.nan)
                        list_long.append(np.nan) 
                        continue
                    lat = results[0]['geometry']['lat']
                    long = results[0]['geometry']['lng']
 
                    list_lat.append(lat)
                    list_long.append(long)
            st.success('Done!')
            # create new columns from lists    

            kl_df['Latitude'] = list_lat   
            kl_df['Longitude'] = list_long
            kl_df=kl_df.dropna()
            st.write("""Neighbourhoods with Cordinates""")
            st.dataframe(kl_df)

            


            geolocator = Nominatim(user_agent="http")
            location = geolocator.geocode(City)
            latitude = location.latitude
            longitude = location.longitude# create map of city using latitude and longitude values
            map_kl = folium.Map(location=[latitude, longitude], zoom_start=11)



    
    
    
            st.write("""Plotting coordinates on the city map""")
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


            CLIENT_ID = 'BMHCFKTJSRN2H3VGV3UCO1JFKE5AOOKSP00YEDHNGHHPJAVR' # your Foursquare ID
            CLIENT_SECRET = '5L2Q3AAPDUPE40K5EELLHHLNXASOATVX44ZCJU5FR15DLQFY' # your Foursquare Secret
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


            st.write('Map with the clustered data')
            # create map
            map_clusters = folium.Map(location=[latitude, longitude], zoom_start=11)

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
            st.write('data set with clustered data')
            st.dataframe(kl_merged)

    if st.checkbox('Go Ahead'):
        scraping()


