import pandas as pd
import streamlit as st
import os
import sys

# Add path to access phase2 classes
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from phase2.Ref import Ref

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
    """Convert any checkbox template format to availability matrix and create Ref objects"""
    
    # Debug: Show the actual Excel structure
    print("=== DEBUG: Excel Structure ===")
    print("First few rows and columns:")
    print(df.iloc[:3, :15])  # Show first 3 rows, 15 columns
    print("\nColumn names:", list(df.columns))
    print("Row 0 values:", list(df.iloc[0]))
    print("Row 1 values:", list(df.iloc[1]))
    
    # Extract time columns by reconstructing from Excel merged header structure
    time_columns = []
    
    # Get the actual time values from row 0 (header row with times)
    time_values = []
    for col_idx in range(5, len(df.columns)):  # Start after basic info columns
        if col_idx < len(df.iloc[0]):
            time_val = df.iloc[0].iloc[col_idx]
            if pd.notna(time_val) and str(time_val) not in ['nan', '']:
                time_values.append(str(time_val))
            else:
                # If we hit a NaN, use the previous time (merged cell behavior)
                if time_values:
                    time_values.append(time_values[-1])
                else:
                    time_values.append("Unknown")
    
    # Get day names from column headers
    day_names = []
    current_day = None
    for col in df.columns[5:]:  # Skip basic info columns
        col_str = str(col)
        # Check if this column is a day name
        if col_str in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            current_day = col_str
        day_names.append(current_day if current_day else "Unknown")
    
    # Combine day names with times to create proper time_columns
    for i, (day, time) in enumerate(zip(day_names, time_values)):
        if day and day != "Unknown" and time and time != "Unknown":
            # Clean up the time format (remove any extra characters)
            clean_time = time.strip()
            if clean_time not in ['5:30']:  # Skip any unwanted times like 5:30
                time_columns.append(f"{day}_{clean_time}")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_time_columns = []
    for col in time_columns:
        if col not in seen:
            seen.add(col)
            unique_time_columns.append(col)
    
    time_columns = unique_time_columns
    
    # Final fallback if extraction failed
    if not time_columns:
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
        times = ['6:30', '7:30', '8:30', '9:30']
        time_columns = [f"{day}_{time}" for day in days for time in times]
    
    print(f"Generated time_columns: {time_columns}")
    
    # Parse availability from each referee and create Ref objects
    availability_matrix = {}
    ref_objects = []
    
    for idx, row in df.iterrows():
        # Skip header rows (rows 0 and 1 contain headers)
        if idx < 2:
            continue
            
        # Check for DONE marker to stop processing
        if str(row.iloc[0]).strip().upper() == 'DONE':
            break
            
        # Skip if no name or example row
        name_cell = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
        if not name_cell or name_cell.startswith('(EXAMPLE)') or name_cell == '':
            continue
        
        # Extract referee information from Excel columns
        # Expected columns: 0=Name, 1=Shirt, 2=Phone, 3=Email, 4=Team, 5+=Availability
        name = name_cell
        
        # Extract email (column 3)
        email_raw = row.iloc[3] if len(row) > 3 else ""
        email = str(email_raw).strip() if pd.notna(email_raw) and str(email_raw).strip() not in ['nan', ''] else ""
        
        # Extract phone (column 2)
        phone_raw = row.iloc[2] if len(row) > 2 else ""
        phone = str(phone_raw).strip() if pd.notna(phone_raw) and str(phone_raw).strip() not in ['nan', ''] else ""
        
        # Debug output for first few referees
        if len(ref_objects) < 3:
            print(f"DEBUG Ref {len(ref_objects)+1}: Name='{name}', Email='{email}', Phone='{phone}'")
            
        # Clean up referee name for availability matrix key
        ref_name = name_cell.replace(' ', '_').replace(',', '').replace('.', '').replace('(', '').replace(')', '')
        if not ref_name:
            continue
            
        # Initialize availability array (binary: 0 or 1 for MILP)
        availability = [0] * len(time_columns)
        
        # For actual Excel columns, map by column index
        time_col_start = 5  # After basic info columns
        for slot_idx in range(min(len(time_columns), len(df.columns) - time_col_start)):
            col_idx = time_col_start + slot_idx
            if col_idx < len(row):
                cell_value = row.iloc[col_idx]
                # Handle checkbox values: True, TRUE, 1, ✓ = available
                if cell_value in [True, 'TRUE', 'True', 1, '1', '✓']:
                    availability[slot_idx] = 1
                # Everything else (False, FALSE, 0, blank, etc.) = not available
        
        # Create Ref object and add to list
        ref_obj = Ref(name=name, availability=availability, email=email, phone_number=phone)
        ref_objects.append(ref_obj)
        
        # Also maintain availability matrix for backward compatibility
        availability_matrix[ref_name] = availability
    
    # Store Ref objects and time columns in session state
    st.session_state['referees'] = ref_objects
    st.session_state['time_columns'] = time_columns
    
    # Convert to DataFrame for return (backward compatibility)
    result_df = pd.DataFrame.from_dict(availability_matrix, orient='index', columns=time_columns)
    return result_df

def load_availability_data():
    """Load availability data if it exists"""
    try:
        availability_df = pd.read_csv('DATA/Convert.csv', index_col=0)
        return availability_df, len(availability_df) > 0
    except:
        return None, False

def clear_availability_data():
    """Clear existing availability data"""
    if os.path.exists('DATA/Convert.csv'):
        os.remove('DATA/Convert.csv')
        return True
    return False
