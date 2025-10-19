import pandas as pd
import streamlit as st
import os
import sys

# Add path to access phase3 classes
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from phase3.Ref import Ref
from phase3.Game import Game
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

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

def process_master_schedule(uploaded_file, min_refs=2, max_refs=3):
    """Process the uploaded master schedule file and extract games
    
    Args:
        uploaded_file: The uploaded Excel file
        min_refs: Minimum referees per game (default 2, overridden by Excel value if present)
        max_refs: Maximum referees per game (default 3, overridden by Excel value if present)
    
    Note: If the Excel file contains "Min Refs per Game" and "Max Refs per Game" fields
    in the metadata section, those values will be used instead of the parameters.
    """
    try:
        # Save uploaded file temporarily
        temp_path = 'DATA/temp_master_schedule.xlsx'
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        # Load workbook with openpyxl to read colors
        wb = load_workbook(temp_path)
        ws = wb.active
        
        games = []
        game_number = 1
        
        # Read min_refs and max_refs from the Excel file metadata section
        # Search for these values in the first 30 rows
        for row_idx in range(1, 30):
            for col_idx in range(1, 20):
                cell_value = ws.cell(row=row_idx, column=col_idx).value
                if cell_value and 'Min Refs per Game' in str(cell_value):
                    # Value is in the next column
                    min_refs_value = ws.cell(row=row_idx, column=col_idx + 1).value
                    if min_refs_value is not None:
                        try:
                            min_refs = int(float(min_refs_value))
                        except (ValueError, TypeError):
                            pass
                elif cell_value and 'Max Refs per Game' in str(cell_value):
                    # Value is in the next column
                    max_refs_value = ws.cell(row=row_idx, column=col_idx + 1).value
                    if max_refs_value is not None:
                        try:
                            max_refs = int(float(max_refs_value))
                        except (ValueError, TypeError):
                            pass
        
        # Parse the schedule structure
        # Find where the actual schedule starts (after title rows)
        schedule_start_row = None
        for row_idx in range(1, 20):  # Check first 20 rows
            cell_value = ws.cell(row=row_idx, column=1).value
            if cell_value == 'Day':
                schedule_start_row = row_idx
                break
        
        if not schedule_start_row:
            raise ValueError("Could not find schedule start (Day header)")
        
        # Read location headers
        locations = []
        col_idx = 3  # Start from column C (after Day and Time)
        while True:
            header_cell = ws.cell(row=schedule_start_row, column=col_idx)
            if header_cell.value:
                # Location header spans 2 columns (division type + number)
                locations.append(header_cell.value)
                col_idx += 2  # Skip to next location (2 columns per location)
            else:
                break
        
        if not locations:
            raise ValueError("Could not find any location headers")
        
        # Parse each day section
        current_row = schedule_start_row + 1
        while current_row < ws.max_row:
            # Check if this is a day row (merged cells in columns A-B)
            day_cell = ws.cell(row=current_row, column=1)
            day_name = day_cell.value
            
            if not day_name or day_name == '':
                current_row += 1
                continue
            
            # Get the date for this day (merged across location columns)
            date_cell = ws.cell(row=current_row, column=3)
            day_date = date_cell.value if date_cell.value else ''
            
            current_row += 1
            
            # Process time slots until we hit a black separator or end
            while current_row < ws.max_row:
                time_cell = ws.cell(row=current_row, column=1)
                time_value = time_cell.value
                
                # Check if we hit a separator (black row) or next day
                if not time_value or time_value == '':
                    break
                
                # Check if it's a valid time (not a day name)
                if str(time_value) in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Day']:
                    break
                
                # Process each location for this time slot
                for loc_idx, location in enumerate(locations):
                    # Calculate column indices (2 columns per location)
                    div_type_col = 3 + (loc_idx * 2)
                    div_num_col = 3 + (loc_idx * 2) + 1
                    
                    # Get cell values
                    div_type_cell = ws.cell(row=current_row, column=div_type_col)
                    div_num_cell = ws.cell(row=current_row, column=div_num_col)
                    
                    division_type = div_type_cell.value
                    division_number = div_num_cell.value
                    
                    # Check cell color to determine if game is scheduled
                    fill = div_type_cell.fill
                    is_scheduled = False
                    
                    if fill and fill.start_color:
                        # Get color as string
                        if hasattr(fill.start_color, 'rgb'):
                            color_str = str(fill.start_color.rgb) if fill.start_color.rgb else ''
                        elif hasattr(fill.start_color, 'index'):
                            color_str = str(fill.start_color.index)
                        else:
                            color_str = str(fill.start_color)
                        
                        # Green, Yellow, or Red means scheduled
                        # Check if it's NOT grey (C0C0C0) or white - if it has color, it's scheduled
                        if color_str and color_str not in ['', '00000000', 'FFC0C0C0', 'C0C0C0', 'FFFFFFFF', 'FFFFFF']:
                            # Check for green, yellow, or red
                            if any(c in color_str.upper() for c in ['FF92D050', '92D050', 'FFFFFF00', 'FFFF00', '00FF00', '90EE90', 'FFFF0000', 'FF0000', 'FF9999']):
                                is_scheduled = True
                    
                    # Only create game if it has BOTH division type AND division number and is scheduled
                    if division_type and division_type != '' and division_number and division_number != '' and is_scheduled:
                        # Parse location (e.g., "Court 1")
                        location_parts = location.split()
                        location_descriptor = location_parts[0] if len(location_parts) > 0 else "Court"
                        location_number = int(location_parts[1]) if len(location_parts) > 1 else 1
                        
                        # Parse time - strip PM/AM labels for scheduler compatibility
                        time_str = str(time_value).strip()
                        # Remove "pm", "PM", "am", "AM" if present
                        time_str = time_str.replace(' pm', '').replace(' PM', '').replace('pm', '').replace('PM', '')
                        time_str = time_str.replace(' am', '').replace(' AM', '').replace('am', '').replace('AM', '')
                        time_str = time_str.strip()
                        
                        # Map division type to difficulty
                        difficulty_map = {
                            'CRJF': 'Co-Rec - Just Fun',
                            'OJF': 'Open - Just Fun',
                            'OTG': 'Open - Top Gun',
                            'CRTG': 'Co-Rec - Top Gun',
                            'W': 'Womens'
                        }
                        difficulty = difficulty_map.get(str(division_type), str(division_type))
                        
                        # Create game object
                        new_game = Game(
                            date=day_name,  # Use day of week, not actual date
                            time=time_str,  # Time without PM/AM label
                            number=game_number,
                            difficulty=difficulty,  # Mapped from division type
                            location=location,
                            min_refs=min_refs,  # From parameters
                            max_refs=max_refs,  # From parameters
                            location_descriptor=location_descriptor,
                            location_number=location_number,
                            division_type=str(division_type) if division_type else None,
                            division_number=str(division_number) if division_number else None
                        )
                        
                        games.append(new_game)
                        game_number += 1
                
                current_row += 1
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        return games, True
        
    except Exception as e:
        st.error(f"Error processing master schedule: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return [], False
