import streamlit as st

def add_compact_navigation():
    """Add compact horizontal navigation to any page"""
    
    # Add CSS for optimized layout
    st.markdown("""
    <style>
    .main > div {
        max-width: 95% !important;
    }
    .block-container {
        max-width: 95% !important;
        padding-top: 1rem !important;
    }
    /* Custom compact navigation */
    .nav-container {
        background-color: #f8f9fa;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e9ecef;
    }
    .nav-button {
        display: inline-block;
        margin-right: 0.5rem;
        margin-bottom: 0.25rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Compact horizontal navigation
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    st.markdown("**📋 Quick Navigation:**")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("🏠 Overview", key="nav_overview", help="System overview and status"):
            st.switch_page("pages/01_Overview.py")
    
    with col2:
        if st.button("🔗 Availability Setup", key="nav_avail", help="Setup referee availability"):
            st.switch_page("pages/02_Availability_Setup.py")

    with col3:
        if st.button("🎮 Game Management", key="nav_games", help="Create and manage games"):
            st.switch_page("pages/03_Game_Management.py")

    with col4:
        if st.button("👥 Referee Management", key="nav_refs", help="Manage referee details"):
            st.switch_page("pages/04_Referee_Management.py")

    with col5:
        if st.button("📊 Schedule Management", key="nav_schedule", help="Run optimization and view results"):
            st.switch_page("pages/05_Schedule_Management.py")

    st.markdown('</div>', unsafe_allow_html=True)
