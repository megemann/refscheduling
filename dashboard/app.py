import streamlit as st
import pandas as pd
import sys
import os

# Add the parent directory to the path to import from phase1
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Set page config
st.set_page_config(
    page_title="Referee Availability Manager",
    page_icon="🏀",
    layout="centered"
)

# Title and description
st.title("🏀 Referee Availability Manager")
st.markdown("### Download template, fill it out, and upload your availability data")

# Create template function
@st.cache_data
def create_template():
    """Create a simple CSV availability template"""
    # Generate all time slots
    time_slots = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
    times = ['6:30', '7:30', '8:30', '9:30']
    
    for day in days:
        for time in times:
            time_slots.append(f"{day}_{time}")
    
    # Create template with sample referees
    template_refs = [f"ref{i}" for i in range(1, 36)]  # ref1 to ref35
    
    # Create empty template (all zeros - refs can fill in 1s where available)
    template_data = {}
    for ref in template_refs:
        template_data[ref] = [0] * len(time_slots)
    
    template_df = pd.DataFrame.from_dict(template_data, orient='index', columns=time_slots)
    return template_df

def create_excel_template():
    """Create an Excel template with dropdowns for time availability"""
    import xlsxwriter
    from io import BytesIO
    
    # Create a new workbook
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('Referee Availability')
    
    # Define formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#881C1C',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    example_format = workbook.add_format({
        'bg_color': '#E7E6E6',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'italic': True
    })
    
    data_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    # Create checkbox format for time slots
    checkbox_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'checkbox': True
    })
    
    # Headers - create sub-columns for each time within each day
    headers = ['Name', 'Shirt', 'Phone', 'Email', 'Team Name/Time Playing']
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
    times = ['6:30', '7:30', '8:30', '9:30']
    
    # Add headers for each day's time slots (checkbox style)
    for day in days:
        for time in times:
            headers.append(f'{day}_{time}')
    
    # Create merged cells for day headers above time slots
    day_header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#881C1C',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    # Write basic info headers in row 0
    basic_headers = ['Name', 'Shirt', 'Phone', 'Email', 'Team Name/Time Playing']
    for col, header in enumerate(basic_headers):
        worksheet.merge_range(0, col, 1, col, header, header_format)
    
    # Add day headers above time columns (merged across 4 time columns)
    for day_idx, day in enumerate(days):
        start_col = 5 + (day_idx * 4)
        end_col = start_col + 3
        worksheet.merge_range(0, start_col, 0, end_col, day, day_header_format)
        
        # Write time headers in row 1
        for time_idx, time in enumerate(times):
            col = start_col + time_idx
            worksheet.write(1, col, time, header_format)
    
    # Write example basic info in row 2
    example_basic = ['(EXAMPLE) Last, First', 'L', '123-456-7890', 'dobie@umass.edu', 
                    'Pop a Volley I\'m Settin\' Thurs 6']
    
    for col, data in enumerate(example_basic):
        worksheet.write(2, col, data, example_format)
    
    # Add example checkboxes (some checked, some unchecked for demonstration)
    example_availability = [True, True, False, True,   # Monday: 6:30✓, 7:30✓, 8:30✗, 9:30✓
                          True, False, True, True,     # Tuesday: 6:30✓, 7:30✗, 8:30✓, 9:30✓
                          False, True, True, False,    # Wednesday: 6:30✗, 7:30✓, 8:30✓, 9:30✗
                          True, True, True, True]      # Thursday: all available
    
    for i, available in enumerate(example_availability):
        col = 5 + i  # Start from column 5 (first time slot)
        worksheet.insert_checkbox(2, col, available, checkbox_format)
    
    # Add empty rows for referees (50 rows starting from row 3)
    for row in range(3, 53):  # rows 3-52 (50 referee rows)
        # Basic info columns (no validation)
        for col in range(5):
            worksheet.write(row, col, '', data_format)
        
        # Time slot checkboxes - using actual Excel checkboxes
        for col in range(5, 21):  # 16 time slots (4 days × 4 times)
            # Insert checkbox with False (unchecked) by default
            worksheet.insert_checkbox(row, col, False, checkbox_format)
    
    # Add "DONE" row - completely black with white text
    done_row = 53  # Row after the 50 referee rows
    done_format = workbook.add_format({
        'bold': True,
        'bg_color': '#000000',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    # Write "DONE" in column A and fill the rest of the row with black
    worksheet.write(done_row, 0, 'DONE', done_format)
    for col in range(1, 21):  # Fill columns B through U with black
        worksheet.write(done_row, col, '', done_format)
    
    # Set column widths
    worksheet.set_column('A:A', 20)  # Name
    worksheet.set_column('B:B', 8)   # Shirt
    worksheet.set_column('C:C', 15)  # Phone
    worksheet.set_column('D:D', 25)  # Email
    worksheet.set_column('E:E', 30)  # Team Name/Time Playing
    worksheet.set_column('F:U', 10)  # Time slot columns
    
    # Set row heights
    worksheet.set_row(0, 25)  # Header row
    worksheet.set_row(1, 25)  # Example row
    
    # Add instructions (after DONE row)
    instruction_start = done_row + 2  # Start 2 rows after DONE
    worksheet.write(instruction_start, 0, 'INSTRUCTIONS:', workbook.add_format({'bold': True, 'font_size': 12}))
    worksheet.write(instruction_start + 1, 0, '1. Fill in your basic information (Name, Shirt, Phone, Email)')
    worksheet.write(instruction_start + 2, 0, '2. Add your team name and playing time if applicable')
    worksheet.write(instruction_start + 3, 0, '3. For each time slot, simply click the checkbox:')
    worksheet.write(instruction_start + 4, 0, '   ☑ = Click to CHECK if you are AVAILABLE for that time')
    worksheet.write(instruction_start + 5, 0, '   ☐ = Leave UNCHECKED if you are NOT available')
    worksheet.write(instruction_start + 6, 0, '4. You can check multiple times per day as needed')
    worksheet.write(instruction_start + 7, 0, '5. Each column under a day represents a specific time (6:30, 7:30, etc.)')
    worksheet.write(instruction_start + 8, 0, '6. Save and submit this file when complete')
    worksheet.write(instruction_start + 9, 0, '7. Note: Checkboxes work best in Excel 2024+ (older versions show TRUE/FALSE)')
    
    workbook.close()
    output.seek(0)
    
    return output.getvalue()

# Process uploaded file
def process_uploaded_file(uploaded_file):
    """Process the uploaded availability file"""
    try:
        # Read the uploaded file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, index_col=0)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            # Read Excel file and convert to our format
            df = pd.read_excel(uploaded_file, sheet_name=0)
            
            # Check if it's the new format with referee info
            if 'Name' in df.columns:
                # Convert from referee info format to availability matrix
                availability_data = convert_referee_format_to_matrix(df)
                df = availability_data
            else:
                # Assume it's already in matrix format
                df = pd.read_excel(uploaded_file, index_col=0)
        else:
            st.error("Please upload a CSV or Excel file")
            return None
        
        # Save to the DATA folder
        output_path = 'DATA/Convert.csv'
        df.to_csv(output_path)
        
        return df
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def convert_referee_format_to_matrix(df):
    """Convert the new checkbox template format to availability matrix"""
    # Define time slots
    time_slots = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
    times = ['6:30', '7:30', '8:30', '9:30']
    
    for day in days:
        for time in times:
            time_slots.append(f"{day}_{time}")
    
    # Parse availability from each referee
    availability_matrix = {}
    
    # Expected column layout for the new template:
    # Col 0: Name, Col 1: Shirt, Col 2: Phone, Col 3: Email, Col 4: Team Name/Time Playing
    # Cols 5-20: Time slots (Monday_6:30, Monday_7:30, ..., Thursday_9:30)
    
    for idx, row in df.iterrows():
        # Skip header rows and example row
        if idx < 2:  # Skip row 0 (headers) and row 1 (time headers)
            continue
            
        # Check for DONE marker to stop processing
        if str(row.iloc[0]).strip().upper() == 'DONE':
            break
            
        # Skip if no name or example row
        name_cell = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
        if not name_cell or name_cell.startswith('(EXAMPLE)') or name_cell == '':
            continue
            
        # Clean up referee name for use as identifier
        ref_name = name_cell.replace(' ', '_').replace(',', '').replace('.', '')
        if not ref_name:
            continue
            
        # Initialize availability array
        availability = [0] * len(time_slots)
        
        # Parse checkbox values from columns 5-20 (16 time slots)
        for slot_idx in range(16):
            col_idx = 5 + slot_idx  # Columns 5-20
            if col_idx < len(row):
                cell_value = row.iloc[col_idx]
                # Handle checkbox values: True, TRUE, 1, ✓ = available
                if cell_value in [True, 'TRUE', 'True', 1, '1', '✓']:
                    availability[slot_idx] = 1
                # Everything else (False, FALSE, 0, blank, etc.) = not available
        
        availability_matrix[ref_name] = availability
    
    # Convert to DataFrame
    result_df = pd.DataFrame.from_dict(availability_matrix, orient='index', columns=time_slots)
    return result_df

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 Step 1: Download Template")
    st.write("Download the availability template and fill it out with your referee availability.")
    st.write("**Instructions:**")
    st.write("- Put `1` in cells where the referee is available")
    st.write("- Put `0` in cells where the referee is NOT available")
    st.write("- Don't change the referee names or time slot headers")
    
    # Generate template
    template_df = create_template()
    
    # Show preview of template
    with st.expander("Preview Template"):
        st.dataframe(template_df.head(), width='stretch')
        st.write(f"Template size: {len(template_df)} referees × {len(template_df.columns)} time slots")
    
    # Download buttons
    csv_template = template_df.to_csv()
    st.download_button(
        label="📊 Download CSV Template",
        data=csv_template,
        file_name="referee_availability_template.csv",
        mime="text/csv",
        width='stretch'
    )
    
    # Generate Excel template with dropdowns
    excel_data = create_excel_template()
    
    st.download_button(
        label="📈 Download Excel Template (with dropdowns)",
        data=excel_data,
        file_name="referee_availability_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width='stretch'
    )

with col2:
    st.subheader("📤 Step 2: Upload Completed File")
    st.write("Upload your completed availability file here.")
    
    uploaded_file = st.file_uploader(
        "Choose your completed availability file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload the template you filled out with availability data"
    )
    
    if uploaded_file is not None:
        st.write(f"**File:** {uploaded_file.name}")
        
        if st.button("🔄 Process Upload", width='stretch'):
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

# Load and display existing availability data
try:
    # Try to load existing processed data
    availability_df = pd.read_csv('DATA/Convert.csv', index_col=0)
    
    if len(availability_df) > 0:
        st.markdown("---")
        st.subheader("📋 Current Referee Availability")
        
        # Create a more readable view by day
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
        times = ['6:30', '7:30', '8:30', '9:30']
        
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
            day_totals = []
            for day in days:
                day_cols = [f"{day}_{time}" for time in times]
                day_total = availability_df[day_cols].sum().sum()
                day_totals.append(day_total)
            best_day = days[day_totals.index(max(day_totals))]
            st.metric("Best Coverage Day", best_day)
        
        # Display the data in a clean table
        st.dataframe(display_df, width='stretch', hide_index=True)
        
        # Add download option for the processed data
        csv_data = availability_df.to_csv()
        st.download_button(
            label="📥 Download Processed Availability Data",
            data=csv_data,
            file_name="referee_availability_processed.csv",
            mime="text/csv",
            width='stretch'
        )
        
        # Show availability by time slot
        with st.expander("📊 Detailed Availability Analysis"):
            st.subheader("Availability by Time Slot")
            
            # Create time slot summary
            time_slot_summary = []
            for day in days:
                for time in times:
                    col_name = f"{day}_{time}"
                    if col_name in availability_df.columns:
                        count = availability_df[col_name].sum()
                        time_slot_summary.append({
                            'Day': day,
                            'Time': time,
                            'Available Refs': count,
                            'Percentage': f"{(count/len(availability_df)*100):.1f}%"
                        })
            
            time_summary_df = pd.DataFrame(time_slot_summary)
            st.dataframe(time_summary_df, width='stretch', hide_index=True)
        
except FileNotFoundError:
    st.info("📋 No availability data found. Upload a completed template to get started!")
except Exception as e:
    st.error(f"Error loading availability data: {str(e)}")


