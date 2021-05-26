import streamlit as st
from PIL import Image
import loc_module
import geocoder
import subhas
import streamlit as st
import pandas as pd
import numpy as np





def app():
    image = Image.open('Simple Pizza Food Facebook Cover.png')
    st.image(image, use_column_width=True)


    st.write("""
    # BUILD YOUR RESTAURANT WEB APP 
     This app performs **_city based prediction_** for opening restaurants.
    ***
    """)

    st.write("""
    Build your restaurant uses various techniques of data science and machine learning to       
    predict a suitable location and cost for opening a restaurant in a city.


    The various techniques used in making this project are

     - Web Scraping
     - API Calls 	
     - K-Means  Clustering
     - Visualisations
    ***""")
    import geocoder
    g = geocoder.google('Delhi')
    st.write(g.latlng)

    st.write(g.city)




    



















link = '[GitHub](http://github.com)'
st.markdown(link, unsafe_allow_html=True)
