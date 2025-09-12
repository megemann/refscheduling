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
    page_icon="📊",
    layout="centered"
)

st.title("📊 Availability Setup")
st.markdown("Follow these steps to set up referee availability:")

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 1. Download Template")

# Template customization section
with st.expander("🔧 Customize Template", expanded=False):
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
        st.info(f"📋 Configuration: {len(selected_days)} days × {len(selected_times)} times = {total_slots} total time slots")

# Standard template download
st.write("**Standard Template:**")
st.write("Download the default template with Monday-Thursday, 6:30-9:30")

# Generate template
template_df = create_template()

# Show preview of template
with st.expander("Preview Standard Template"):
    st.dataframe(template_df.head(), width='stretch')
    st.write(f"Template size: {len(template_df)} referees × {len(template_df.columns)} time slots")

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
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error generating custom template: {str(e)}")
else:
    st.info("Select days and times above to generate a custom template")

with col2:
    st.subheader("📤 2. Upload Completed File")
st.write("Upload your completed availability file here.")

uploaded_file = st.file_uploader(
    "Choose your completed availability file",
    type=['csv', 'xlsx', 'xls'],
    help="Upload the template you filled out with availability data"
)

if uploaded_file is not None:
    st.write(f"**File:** {uploaded_file.name}")
    
    if st.button("🔄 Process Upload", use_container_width=True):
        with st.spinner("Processing your file..."):
            processed_df = process_uploaded_file(uploaded_file)
            
            if processed_df is not None:
                st.success("✅ File processed successfully!")
                
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
                
                st.info("💾 Data saved to DATA/Convert.csv")
                st.rerun()  # Refresh to show the new data below

# Reset button to upload another file
if os.path.exists('DATA/Convert.csv'):
    st.markdown("---")
    if st.button("🔄 Reset & Upload Another File", type="secondary", use_container_width=True):
        # Clear the existing data
        if clear_availability_data():
            st.success("✅ Data cleared! You can now upload a new availability file.")
            st.rerun()

# Step 3: View Current Availability Data
st.markdown("---")
st.subheader("📋 3. Current Referee Availability")

# Load and display existing availability data
availability_df, has_data = load_availability_data()

if has_data:
    # Proceed to render availability summary if data exists
    # Detect days and times from the actual column names
    detected_days = set()
    detected_times = set()
    
    for col in availability_df.columns:
        if '_' in col:
            day, time = col.split('_', 1)
            detected_days.add(day)
            detected_times.add(time)
    
    # Sort days and times
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    days = sorted(detected_days, key=lambda d: day_order.index(d) if d in day_order else 999)
    times = sorted(detected_times)
    
    # Convert to day-based availability for display
    display_data = []
    for ref_name in availability_df.index:
        ref_row = {'Referee': ref_name}
        
        for day in days:
            available_times = []
            for time in times:
                col_name = f"{day}_{time}"
                if col_name in availability_df.columns and availability_df.loc[ref_name, col_name] == 1:
                    available_times.append(time)
            
            if available_times:
                ref_row[day] = ', '.join(available_times)
            else:
                ref_row[day] = 'Not available'
        
        display_data.append(ref_row)
    
    # Create display DataFrame
    display_df = pd.DataFrame(display_data)
    
    # Show summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Referees", len(availability_df))
    with col2:
        total_slots = availability_df.sum().sum()
        st.metric("Total Availability", total_slots)
    with col3:
        avg_per_ref = availability_df.sum(axis=1).mean()
        st.metric("Avg Slots per Ref", f"{avg_per_ref:.1f}")
    with col4:
        # Calculate availability by day
        if days:
            day_totals = []
            for day in days:
                day_cols = [f"{day}_{time}" for time in times if f"{day}_{time}" in availability_df.columns]
                if day_cols:
                    day_total = availability_df[day_cols].sum().sum()
                    day_totals.append(day_total)
                else:
                    day_totals.append(0)
            
            if day_totals and max(day_totals) > 0:
                best_day = days[day_totals.index(max(day_totals))]
                st.metric("Best Coverage Day", best_day)
            else:
                st.metric("Best Coverage Day", "N/A")
        else:
            st.metric("Best Coverage Day", "N/A")
    
    # Display the data in a clean table
    st.dataframe(display_df, width='stretch', hide_index=True)
    
    # Add download option for the processed data
    csv_data = availability_df.to_csv()
    st.download_button(
        label="📥 Download Processed Availability Data",
        data=csv_data,
        file_name="referee_availability_processed.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    # Show availability by time slot
    with st.expander("📊 Detailed Availability Analysis"):
        st.subheader("Availability by Time Slot")
        
        # Debug info
        st.write(f"**Debug Info:**")
        st.write(f"Detected days: {list(days)}")
        st.write(f"Detected times: {list(times)}")
        st.write(f"Available columns: {list(availability_df.columns)}")
        
        # Create time slot summary using all actual columns
        time_slot_summary = []
        
        # Process all columns that match day_time pattern
        for col in availability_df.columns:
            if '_' in col:
                try:
                    day, time = col.split('_', 1)
                    count = availability_df[col].sum()
                    time_slot_summary.append({
                        'Day': day,
                        'Time': time,
                        'Available Refs': int(count),
                        'Percentage': f"{(count/len(availability_df)*100):.1f}%"
                    })
                except Exception as e:
                    st.write(f"Error processing column {col}: {e}")
        
        if time_slot_summary:
            time_summary_df = pd.DataFrame(time_slot_summary)
            # Sort by day order then by time
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            time_summary_df['day_sort'] = time_summary_df['Day'].apply(lambda x: day_order.index(x) if x in day_order else 999)
            time_summary_df = time_summary_df.sort_values(['day_sort', 'Time']).drop('day_sort', axis=1)
            st.dataframe(time_summary_df, width='stretch', hide_index=True)
        else:
            st.warning("No time slot data found. Please check your data format.")
    
    # Next step navigation
    st.markdown("---")
    st.success("✅ **Availability setup complete!** Ready for game management.")
    if st.button("➡️ Continue to Game Management", use_container_width=True):
        st.switch_page("pages/Game_Management.py")
    
else:
    st.info("📋 No availability data found. Upload a completed template to get started!")
    st.markdown("---")
    st.markdown("### 📝 How to get started:")
    st.markdown("1. **Download** the Excel template above")
    st.markdown("2. **Fill out** referee availability (check boxes for available times)")
    st.markdown("3. **Upload** the completed file")
    st.markdown("4. **Continue** to Game Management")
