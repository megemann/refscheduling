import pandas as pd
import xlsxwriter
from io import BytesIO
import streamlit as st

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

def create_custom_template(selected_days, selected_times, num_refs=50):
    """Create a customizable Excel template with user-selected days and times"""
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
    
    # Create formats with thick borders for day separation
    thick_left_border_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'left': 3,  # Thick left border
        'checkbox': True
    })
    
    thick_right_border_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'right': 3,  # Thick right border
        'checkbox': True
    })
    
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
    
    # Add day headers above time columns (merged across time columns)
    col_offset = 5
    for day_idx, day in enumerate(selected_days):
        num_times = len(selected_times)
        start_col = col_offset + (day_idx * num_times)
        end_col = start_col + num_times - 1
        worksheet.merge_range(0, start_col, 0, end_col, day, day_header_format)
        
        # Write time headers in row 1
        for time_idx, time in enumerate(selected_times):
            col = start_col + time_idx
            worksheet.write(1, col, time, header_format)
    
    # Write example basic info in row 2
    example_basic = ['(EXAMPLE) Last, First', 'L', '123-456-7890', 'dobie@umass.edu', 
                    'Pop a Volley I\'m Settin\' Example Team']
    
    for col, data in enumerate(example_basic):
        worksheet.write(2, col, data, example_format)
    
    # Add example checkboxes (some checked, some unchecked for demonstration)
    total_time_slots = len(selected_days) * len(selected_times)
    example_pattern = [True, True, False, True] * (total_time_slots // 4 + 1)
    example_pattern = example_pattern[:total_time_slots]
    
    for i, available in enumerate(example_pattern):
        col = 5 + i  # Start from column 5 (first time slot)
        
        # Apply same border logic for example row
        day_idx = i // len(selected_times)
        time_idx_in_day = i % len(selected_times)
        
        # Choose format based on position within day group
        if len(selected_days) == 1:
            format_to_use = checkbox_format
        elif day_idx == 0 and time_idx_in_day == 0:
            format_to_use = thick_left_border_format
        elif day_idx == len(selected_days) - 1 and time_idx_in_day == len(selected_times) - 1:
            format_to_use = thick_right_border_format
        elif time_idx_in_day == 0:
            format_to_use = thick_left_border_format
        elif time_idx_in_day == len(selected_times) - 1:
            format_to_use = thick_right_border_format
        else:
            format_to_use = checkbox_format
        
        worksheet.insert_checkbox(2, col, available, format_to_use)
    
    # Add empty rows for referees (starting from row 3)
    for row in range(3, 3 + num_refs):
        # Basic info columns (no validation)
        for col in range(5):
            worksheet.write(row, col, '', data_format)
        
        # Time slot checkboxes with thick borders for day separation
        for slot_idx in range(total_time_slots):
            col = 5 + slot_idx
            
            # Determine which day this slot belongs to
            day_idx = slot_idx // len(selected_times)
            time_idx_in_day = slot_idx % len(selected_times)
            
            # Choose format based on position within day group
            if len(selected_days) == 1:
                # Single day - use regular format
                format_to_use = checkbox_format
            elif day_idx == 0 and time_idx_in_day == 0:
                # First column of first day - thick left border only
                format_to_use = thick_left_border_format
            elif day_idx == len(selected_days) - 1 and time_idx_in_day == len(selected_times) - 1:
                # Last column of last day - thick right border only
                format_to_use = thick_right_border_format
            elif time_idx_in_day == 0:
                # First column of any other day - thick left border only
                format_to_use = thick_left_border_format
            elif time_idx_in_day == len(selected_times) - 1:
                # Last column of any day - thick right border only
                format_to_use = thick_right_border_format
            else:
                # Middle columns - regular format
                format_to_use = checkbox_format
            
            worksheet.insert_checkbox(row, col, False, format_to_use)
    
    # Add "DONE" row - completely black with white text
    done_row = 3 + num_refs
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
    for col in range(1, 5 + total_time_slots):
        worksheet.write(done_row, col, '', done_format)
    
    # Set column widths (expand by 2.5x except shirt size)
    worksheet.set_column('A:A', 50)  # Name (20 * 2.5)
    worksheet.set_column('B:B', 8)   # Shirt (keep same)
    worksheet.set_column('C:C', 37.5)  # Phone (15 * 2.5)
    worksheet.set_column('D:D', 62.5)  # Email (25 * 2.5)
    worksheet.set_column('E:E', 75)  # Team Name/Time Playing (30 * 2.5)
    
    # Set time slot columns width dynamically
    if total_time_slots > 0:
        # Calculate the last column letter properly
        start_col = 5  # Column F is index 5
        end_col = start_col + total_time_slots - 1
        
        # Convert column indices to Excel column letters
        def col_num_to_letter(col_num):
            """Convert column number to Excel column letter(s)"""
            result = ""
            while col_num >= 0:
                result = chr(col_num % 26 + ord('A')) + result
                col_num = col_num // 26 - 1
            return result
        
        start_letter = col_num_to_letter(start_col)
        end_letter = col_num_to_letter(end_col)
        worksheet.set_column(f'{start_letter}:{end_letter}', 10)  # Time slot columns
    
    # Set row heights
    worksheet.set_row(0, 25)  # Header row
    worksheet.set_row(1, 25)  # Time header row
    worksheet.set_row(2, 25)  # Example row
    
    # Add instructions (after DONE row)
    instruction_start = done_row + 2
    worksheet.write(instruction_start, 0, 'INSTRUCTIONS:', workbook.add_format({'bold': True, 'font_size': 12}))
    worksheet.write(instruction_start + 1, 0, '1. Fill in your basic information (Name, Shirt, Phone, Email)')
    worksheet.write(instruction_start + 2, 0, '2. Add your team name and playing time if applicable')
    worksheet.write(instruction_start + 3, 0, '3. For each time slot, simply click the checkbox:')
    worksheet.write(instruction_start + 4, 0, '   ☑ = Click to CHECK if you are AVAILABLE for that time')
    worksheet.write(instruction_start + 5, 0, '   ☐ = Leave UNCHECKED if you are NOT available')
    worksheet.write(instruction_start + 6, 0, '4. You can check multiple times per day as needed')
    worksheet.write(instruction_start + 7, 0, '5. Each column under a day represents a specific time')
    worksheet.write(instruction_start + 8, 0, '6. Save and submit this file when complete')
    worksheet.write(instruction_start + 9, 0, '7. Note: Checkboxes work best in Excel 2024+ (older versions show TRUE/FALSE)')
    
    workbook.close()
    output.seek(0)
    
    return output.getvalue()
