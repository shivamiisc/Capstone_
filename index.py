import loc_module
import subhas
import streamlit as st
import byr


   
PAGES = {
"Home": byr,
"Location Prediction": loc_module,
"Housing Cost Prediction": subhas
}




genre = st.sidebar.selectbox("Navigation", 
        list(PAGES.keys()))


page = PAGES[genre]
page.app()
  