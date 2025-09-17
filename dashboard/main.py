import streamlit as st

# Set page config
st.set_page_config(
    page_title="Referee Scheduling System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Redirect to Overview page
st.switch_page("pages/01_Overview.py")
