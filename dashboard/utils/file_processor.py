import pandas as pd
import streamlit as st
import os
from .referee_model import Referee, create_referee_list_from_excel, get_availability_matrix_from_referees

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
    """Convert any checkbox template format to availability matrix (adaptive)"""
    
    # Debug: Show the actual Excel structure
    print("=== DEBUG: Excel Structure ===")
    print("First few rows and columns:")
    print(df.iloc[:3, :15])  # Show first 3 rows, 15 columns
    print("\nColumn names:", list(df.columns))
    print("Row 0 values:", list(df.iloc[0]))
    print("Row 1 values:", list(df.iloc[1]))
    
    # The issue seems to be that the current logic is reading data rows instead of headers
    # Let's use a different approach - assume the Excel has our template structure
    
    time_columns = []
    
    # Based on your debug output, it looks like the columns are already named correctly
    # but we're parsing them wrong. Let's just use the column names directly
    # if they match the pattern Day_Time
    
    for col in df.columns:
        if isinstance(col, str) and '_' in col:
            # Split on first underscore only
            parts = col.split('_', 1)
            if len(parts) == 2:
                day_part, time_part = parts
                # Check if this looks like a day-time combination
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                time_patterns = [':', '30', '00']  # Common time patterns
                
                if (day_part in day_names or any(d.lower() in day_part.lower() for d in day_names)) and \
                   (any(p in time_part for p in time_patterns) or time_part.replace('.', '').replace(':', '').isdigit()):
                    time_columns.append(col)
    
    # If that doesn't work, try to reconstruct from the template structure
    if not time_columns:
        # Look for day names in column headers (even if they're not perfectly formatted)
        day_cols = []
        for col in df.columns:
            col_str = str(col).lower()
            if any(day.lower() in col_str for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
                day_cols.append(col)
        
        # If we found day columns, assume 4 time slots per day
        if day_cols:
            times = ['6:30', '7:30', '8:30', '9:30']
            for day_col in day_cols:
                # Extract just the day name
                day_name = day_col.split('_')[0] if '_' in str(day_col) else str(day_col)
                for time in times:
                    time_columns.append(f"{day_name}_{time}")
    
    # Final fallback - use standard format
    if not time_columns:
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
        times = ['6:30', '7:30', '8:30', '9:30']
        time_columns = [f"{day}_{time}" for day in days for time in times]
    
    print(f"Generated time_columns: {time_columns}")
    
    # Parse availability from each referee
    availability_matrix = {}
    
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
            
        # Clean up referee name for use as identifier
        ref_name = name_cell.replace(' ', '_').replace(',', '').replace('.', '').replace('(', '').replace(')', '')
        if not ref_name:
            continue
            
        # Initialize availability array
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
        
        availability_matrix[ref_name] = availability
    
    # Convert to DataFrame
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
