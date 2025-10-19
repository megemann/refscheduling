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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add CSS for wider container and step boxes
st.markdown("""
<style>
.main > div {
    max-width: 95% !important;
}
.block-container {
    max-width: 95% !important;
}

/* Step box styling */
.step-box {
    padding: 25px;
    border-radius: 10px;
    border: 2px solid rgba(255, 255, 255, 0.2);
    margin: 20px 0;
    background-color: rgba(255, 255, 255, 0.05);
}

.step-header {
    font-size: 1.3em;
    font-weight: 600;
    margin-bottom: 15px;
    color: #4CAF50;
}

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
st.markdown("Set up referee availability by downloading a template, filling it out, and uploading it back.")

# Check if data already exists
data_exists = os.path.exists('DATA/Convert.csv')

# ==================== STEP 1: Download Template ====================

st.markdown('<div class="step-header">Step 1: Download Template</div>', unsafe_allow_html=True)
st.markdown("Customize and download an Excel template for your referees to fill out.")

# Template customization section
col_config1, col_config2 = st.columns(2)

with col_config1:
    st.markdown("**Days of the Week:**")
    all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    selected_days = st.multiselect(
        "Select Days",
        all_days,
        default=['Monday', 'Tuesday', 'Wednesday', 'Thursday'],
        label_visibility="collapsed"
    )
    
    st.markdown("**Number of Referee Rows:**")
    num_refs = st.number_input(
        "Number of rows",
        min_value=10,
        max_value=100,
        value=50,
        label_visibility="collapsed"
    )

with col_config2:
    st.markdown("**Time Slots:**")
    all_times = []
    for hour in range(3, 24):  # 3 AM to 11 PM
        for minute in [0, 30]:
            time_str = f"{hour}:{minute:02d}" if hour < 24 else f"{hour-24}:{minute:02d}"
            all_times.append(time_str)
    
    selected_times = st.multiselect(
        "Select Times",
        all_times,
        default=['6:30', '7:30', '8:30', '9:30'],
        label_visibility="collapsed"
    )

# Show configuration summary and download button
if selected_days and selected_times:
    total_slots = len(selected_days) * len(selected_times)
    
    try:
        custom_excel_data = create_custom_template(selected_days, selected_times, num_refs)
        st.download_button(
            label=f"Download Template ({len(selected_days)} days, {len(selected_times)} times, {num_refs} refs)",
            data=custom_excel_data,
            file_name=f"referee_availability_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )
    except Exception as e:
        st.error(f"Error generating template: {str(e)}")
else:
    st.warning("Please select at least one day and one time slot to generate the template.")

st.markdown('</div>', unsafe_allow_html=True)

# ==================== STEP 2: Upload Completed File ====================
st.markdown('<div class="step-header">Step 2: Upload Completed File</div>', unsafe_allow_html=True)

if data_exists:
    st.warning("**Note:** You already have availability data loaded. Uploading a new file will replace the existing data.")
    
    col_upload, col_reset = st.columns([3, 1])
    with col_reset:
        if st.button("Clear Existing Data", type="secondary", use_container_width=True):
            if clear_availability_data():
                st.success("Data cleared!")
                st.rerun()
    with col_upload:
        st.markdown("Upload your completed template below:")
else:
    st.markdown("Upload your completed template after filling in referee availability:")

uploaded_file = st.file_uploader(
    "Choose File",
    type=['csv', 'xlsx', 'xls'],
    help="Upload the template you filled out with availability data",
    label_visibility="collapsed"
)

if uploaded_file is not None:
    st.success(f"File selected: **{uploaded_file.name}**")
    
    col_process, col_spacer = st.columns([2, 1])
    with col_process:
        if st.button("Process and Import", use_container_width=True, type="primary"):
            with st.spinner("Processing your file..."):
                processed_df = process_uploaded_file(uploaded_file)
                
                if processed_df is not None:
                    st.success("File processed successfully!")
                    
                    # Show summary
                    st.markdown("**Import Summary:**")
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        st.metric("Referees", len(processed_df))
                    with col_b:
                        st.metric("Time Slots", len(processed_df.columns))
                    with col_c:
                        total_avail = processed_df.sum().sum()
                        st.metric("Total Availability", int(total_avail))
                    with col_d:
                        avg_avail = processed_df.sum(axis=1).mean()
                        st.metric("Avg per Referee", f"{avg_avail:.1f}")
                    
                    st.info("Data has been saved and is ready to use.")
                    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ==================== Current Status ====================
st.markdown("---")
st.subheader("Current Status")

# Check for availability data without caching
try:
    import pandas as pd
    availability_df = pd.read_csv('DATA/Convert.csv', index_col=0)
    if len(availability_df) > 0:
        num_refs = len(availability_df)
        num_slots = len(availability_df.columns)
        total_availability = availability_df.sum().sum()
        
        st.success(f"Availability data loaded: {num_refs} referees across {num_slots} time slots")
        
        # Show summary in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Referees", num_refs)
        with col2:
            st.metric("Time Slots", num_slots)
        with col3:
            st.metric("Total Availability Entries", int(total_availability))
    else:
        st.warning("No availability data found")
except FileNotFoundError:
    st.info("No availability data uploaded yet. Follow the steps above to get started.")
except Exception as e:
    st.error(f"Error reading availability data: {str(e)}")

