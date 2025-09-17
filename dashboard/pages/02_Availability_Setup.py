import streamlit as st
import pandas as pd
import sys
import os

# Add the parent directory to the path to import from phase1
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import utility functions
from dashboard.utils.template_generator import create_template, create_custom_template
from dashboard.utils.file_processor import process_uploaded_file, load_availability_data, clear_availability_data

# Set page config
st.set_page_config(
    page_title="Availability Setup",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add CSS for wider container
st.markdown("""
<style>
.main > div {
    max-width: 95% !important;
}
.block-container {
    max-width: 95% !important;
}
</style>
""", unsafe_allow_html=True)

# Add table styling CSS for better readability
st.markdown("""
<style>
/* Table styling for better readability */
.stDataFrame, .stTable {
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

.stDataFrame th, .stTable th {
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    padding: 8px !important;
    font-weight: 600 !important;
}

.stDataFrame td, .stTable td {
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    padding: 8px !important;
}

.stDataFrame th:last-child, .stTable th:last-child,
.stDataFrame td:last-child, .stTable td:last-child {
    border-right: none !important;
}

.stDataFrame tr:last-child td, .stTable tr:last-child td {
    border-bottom: none !important;
}
</style>
""", unsafe_allow_html=True)

st.title("Availability Setup")
st.markdown("Follow these steps to set up referee availability:")

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Download Template")

# Template customization section
with st.expander("Customize Template", expanded=True):
    st.write("**Select days and times for your template:**")
    
    # Day selection
    all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    selected_days = st.multiselect(
        "Select Days:",
        all_days,
        default=['Monday', 'Tuesday', 'Wednesday', 'Thursday']
    )
    
    # Number of referees
    num_refs = st.number_input("Number of Referee Rows:", min_value=10, max_value=100, value=50)
    
    # Time selection with all available times
    all_times = []
    for hour in range(3, 24):  # 3 AM to 11 PM
        for minute in [0, 30]:
            time_str = f"{hour}:{minute:02d}" if hour < 24 else f"{hour-24}:{minute:02d}"
            all_times.append(time_str)
    
    # Multi-select for times
    selected_times = st.multiselect(
        "Select Times:",
        all_times,
        default=['6:30', '7:30', '8:30', '9:30']
    )
    
    # Show configuration summary
    if selected_days and selected_times:
        total_slots = len(selected_days) * len(selected_times)
        st.info(f"Configuration: {len(selected_days)} days × {len(selected_times)} times = {total_slots} total time slots")

# Custom template download
if 'selected_days' in locals() and 'selected_times' in locals() and selected_days and selected_times:
    st.write("**Custom Template:**")
    
    # Generate custom Excel template
    try:
        custom_excel_data = create_custom_template(selected_days, selected_times, num_refs)
        
        st.download_button(
            label=f"📈 Download Custom Excel Template ({len(selected_days)} days × {len(selected_times)} times)",
            data=custom_excel_data,
            file_name=f"custom_referee_template_{len(selected_days)}days_{len(selected_times)}times.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch'
        )
    except Exception as e:
        st.error(f"Error generating custom template: {str(e)}")
else:
    st.info("Select days and times above to generate a custom template")

with col2:
    st.subheader("2. Upload Completed File")
st.write("Upload your completed availability file here.")

uploaded_file = st.file_uploader(
    "Choose your completed availability file",
    type=['csv', 'xlsx', 'xls'],
    help="Upload the template you filled out with availability data"
)

if uploaded_file is not None:
    st.write(f"**File:** {uploaded_file.name}")
    
    if st.button("Process Upload", width='stretch'):
        with st.spinner("Processing your file..."):
            processed_df = process_uploaded_file(uploaded_file)
            
            if processed_df is not None:
                st.success("File processed successfully!")
                
                # Show summary
                st.write("**Summary:**")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Referees", len(processed_df))
                    st.metric("Time Slots", len(processed_df.columns))
                with col_b:
                    total_avail = processed_df.sum().sum()
                    st.metric("Total Availability", total_avail)
                    avg_avail = processed_df.sum(axis=1).mean()
                    st.metric("Avg per Referee", f"{avg_avail:.1f}")
                
                st.info("Data saved to DATA/Convert.csv")
                st.rerun()  # Refresh to show the new data below

# Reset button to upload another file
if os.path.exists('DATA/Convert.csv'):
    st.markdown("---")
    if st.button("Reset & Upload Another File", type="secondary", width='stretch'):
        # Clear the existing data
        if clear_availability_data():
            st.success("Data cleared! You can now upload a new availability file.")
            st.rerun()

# Availability Status Confirmation
st.markdown("---")
st.subheader("Availability Status")

# Check for availability data without caching
try:
    import pandas as pd
    availability_df = pd.read_csv('DATA/Convert.csv', index_col=0)
    if len(availability_df) > 0:
        num_refs = len(availability_df)
        num_slots = len(availability_df.columns)
        total_availability = availability_df.sum().sum()
        
        st.success(f"✅ Availability data loaded: {num_refs} referees × {num_slots} time slots")
        st.info(f"Total availability entries: {int(total_availability)}")
    else:
        st.warning("❌ No availability data found")
except FileNotFoundError:
    st.warning("❌ No availability data found")
except Exception as e:
    st.error(f"❌ Error reading availability data: {str(e)}")


