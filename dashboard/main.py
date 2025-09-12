import streamlit as st
import sys
import os

# Add the parent directory to the path to import from phase1
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Set page config
st.set_page_config(
    page_title="Referee Scheduling System",
    page_icon="🏀",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("🏀 Referee Scheduling System")
st.markdown("### Automated referee scheduling with optimization")

# Main navigation
st.markdown("---")
st.subheader("📋 Quick Start Guide")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Step 1: Availability Setup**
    - Download template
    - Fill referee availability
    - Upload completed file
    """)
    if st.button("🔗 Go to Availability Setup", use_container_width=True):
        st.switch_page("pages/Availability_Setup.py")

with col2:
    st.markdown("""
    **Step 2: Game Management**
    - Define games per time slot
    - Run optimization
    - Export schedules
    """)
    if st.button("🔗 Go to Game Management", use_container_width=True):
        st.switch_page("pages/Game_Management.py")

st.markdown("---")

# System status
st.subheader("📈 System Status")

# Check if availability data exists
try:
    import pandas as pd
    availability_df = pd.read_csv('DATA/Convert.csv', index_col=0)
    has_availability_data = len(availability_df) > 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Referees", len(availability_df))
    with col2:
        st.metric("Time Slots", len(availability_df.columns))
    with col3:
        st.metric("Total Availability", availability_df.sum().sum())
    
    st.success("✅ Availability data loaded successfully!")
    
except:
    has_availability_data = False
    st.info("📋 No availability data found. Please start with Step 1: Availability Setup")

# Show workflow progress
st.markdown("---")
st.subheader("🔄 Workflow Progress")

if has_availability_data:
    st.markdown("✅ **Step 1:** Availability data ready")
    st.markdown("🔄 **Step 2:** Ready for game management")
else:
    st.markdown("🔄 **Step 1:** Set up availability data")
    st.markdown("⏳ **Step 2:** Waiting for Step 1 completion")

st.markdown("---")
st.markdown("*Navigate using the sidebar to access specific features*")
