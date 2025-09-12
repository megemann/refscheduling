import streamlit as st
import pandas as pd
import sys
import os

# Add the parent directory to the path to import from phase1
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import utility functions
from dashboard.utils.file_processor import load_availability_data

# Set page config
st.set_page_config(
    page_title="Referee Management",
    page_icon="👥",
    layout="centered"
)

st.title("👥 Referee Management")
st.markdown("Manage referee profiles, skills, and preferences")

# Placeholder content
st.markdown("---")
st.info("🚧 **This page is under construction**")
st.markdown("### Coming Soon:")
st.markdown("- Referee profile management")
st.markdown("- Skill level tracking")
st.markdown("- Performance analytics")
st.markdown("- Contact information")
st.markdown("- Preference settings")

# Navigation buttons
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("⬅️ Back to Availability Setup", use_container_width=True):
        st.switch_page("pages/Availability_Setup.py")
with col2:
    if st.button("🏠 Back to Main", use_container_width=True):
        st.switch_page("main.py")
with col3:
    if st.button("➡️ Go to Game Management", use_container_width=True):
        st.switch_page("pages/Game_Management.py")
