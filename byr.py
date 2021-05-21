import streamlit as st
from PIL import Image
import loc_module
import subhas
import streamlit as st




image = Image.open('Simple Pizza Food Facebook Cover.png')
st.image(image, use_column_width=True)


st.write("""
# BUILD YOUR RESTAURANT WEB APP 
 This app performs **_city based prediction_** for opening restaurants.




***
""")

st.write("""
Build your restaurant uses various techniques of data science and machine learning to predict a suitable location and cost for opening a restaurant in a city.


The various techniques used in making tis project are

 - Web Scraping
 - API Calls 	
 - K-Means  Clustering
 - Visualisations



***
""")










PAGES = {
    "Location Prediction": loc_module,
    "Housing Cost Prediction": subhas
}


st.title('MODULES PROVIDED')

genre = st.radio(
     "Pick one of these",
      list(PAGES.keys()))

if genre == 'Location prediction':
     st.write('You selected Location prediction.')
else:
     st.write("You didn't select Location prediction.")

page = PAGES[genre]
page.app()

























link = '[GitHub](http://github.com)'
st.markdown(link, unsafe_allow_html=True)