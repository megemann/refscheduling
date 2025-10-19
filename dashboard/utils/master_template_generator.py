import pandas as pd
import xlsxwriter
from io import BytesIO
import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta

def create_master_template(days_schedule=None, locations=None, min_refs=2, max_refs=3):
    """
    Create master schedule template
    
    Args:
        days_schedule: List of dicts with keys: 'day', 'date', 'times' (list of time strings)
        locations: List of dicts with keys: 'descriptor' (e.g., 'Court'), 'number' (e.g., 1)
        min_refs: Minimum referees per game (default 2)
        max_refs: Maximum referees per game (default 3)
    
    Returns:
        BytesIO object containing the Excel file
    """
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('Master Schedule')
    
    # Define formats - Times New Roman, white backgrounds, borders
    title_format = workbook.add_format({
        'font_name': 'Times New Roman',
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'bg_color': 'white'
    })
    
    subtitle_format = workbook.add_format({
        'font_name': 'Times New Roman',
        'bold': True,
        'font_size': 12,
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'bg_color': 'white'
    })
    
    header_format = workbook.add_format({
        'font_name': 'Times New Roman',
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'bg_color': 'white',
        'font_size': 11
    })
    
    day_format = workbook.add_format({
        'font_name': 'Times New Roman',
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'bg_color': 'white',
        'font_size': 11
    })
    
    time_format = workbook.add_format({
        'font_name': 'Times New Roman',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'bg_color': 'white',
        'font_size': 11
    })
    
    # Cell formats for game scheduling status
    grey_format = workbook.add_format({
        'font_name': 'Times New Roman',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'bg_color': '#C0C0C0',  # Grey - no game scheduled (default)
        'font_size': 11
    })
    
    white_format = workbook.add_format({
        'font_name': 'Times New Roman',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'bg_color': '#ffffff',  # White - game not being played
        'font_size': 11
    })
    
    green_format = workbook.add_format({
        'font_name': 'Times New Roman',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'bg_color': '#92D050',  # Green - scheduled
        'font_size': 11
    })
    
    yellow_format = workbook.add_format({
        'font_name': 'Times New Roman',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'bg_color': '#FFFF00',  # Yellow - scheduled
        'font_size': 11
    })
    
    red_format = workbook.add_format({
        'font_name': 'Times New Roman',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'bg_color': '#FF0000',  # Red - not scheduled
        'font_size': 11
    })
    
    black_separator_format = workbook.add_format({
        'bg_color': '#000000',  # Black separator between days
        'border': 0
    })
    
    date_format = workbook.add_format({
        'font_name': 'Times New Roman',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'bg_color': 'white',
        'font_size': 10
    })
    
    # Set default column widths
    worksheet.set_column('A:A', 12)  # Day column
    worksheet.set_column('B:B', 10)  # Time column
    
    # Default locations if none provided
    if locations is None:
        locations = [
            {'descriptor': 'Court', 'number': 1},
            {'descriptor': 'Court', 'number': 2},
            {'descriptor': 'Court', 'number': 3},
            {'descriptor': 'Court', 'number': 4},
        ]
    
    # Calculate number of location columns for header merging
    num_locations = len(locations)
    # Each location has 2 columns (division type + division number)
    location_columns = num_locations * 2
    # Add extra columns for legend on the right
    legend_columns = 3  # Space for legend
    padding_columns = 2  # Padding between schedule and legend
    num_cols_for_header = 2 + location_columns + padding_columns + legend_columns
    
    # Get column letter for merging
    end_col_letter = chr(ord('A') + num_cols_for_header - 1)
    
    # Row 1: Title (A to end column merged)
    worksheet.merge_range(f'A1:{end_col_letter}1', 'Volleyball Master Schedule - Fall 2025', title_format)
    worksheet.set_row(0, 20)  # Set row height
    
    # Row 2: Subtitle (A to end column merged)
    worksheet.merge_range(f'A2:{end_col_letter}2', 'UMass Intramural Sports', subtitle_format)
    worksheet.set_row(1, 18)  # Set row height
    
    # Set width for location columns (division type wider, number narrower)
    for i in range(num_locations):
        div_type_col = 2 + (i * 2)
        div_num_col = 2 + (i * 2) + 1
        worksheet.set_column(div_type_col, div_type_col, 10)  # Division type column
        worksheet.set_column(div_num_col, div_num_col, 5)     # Division number column
    
    # Set width for padding columns (empty space between schedule and legend)
    padding_start_col = 2 + location_columns
    for i in range(padding_columns):
        worksheet.set_column(padding_start_col + i, padding_start_col + i, 3)  # Small padding columns
    
    # Set width for legend columns on the right (wider for readability)
    legend_start_col = 2 + location_columns + padding_columns
    for i in range(legend_columns):
        worksheet.set_column(legend_start_col + i, legend_start_col + i, 25)
    
    # Default schedule if none provided
    if days_schedule is None:
        days_schedule = [
            {
                'day': 'Monday',
                'date': '1/20/2025',
                'times': ['6:30 pm', '7:30 pm', '8:30 pm', '9:30 pm']
            },
            {
                'day': 'Tuesday',
                'date': '1/21/2025',
                'times': ['6:30 pm', '7:30 pm', '8:30 pm', '9:30 pm']
            }
        ]
    
    # (Column widths already set above)
    
    current_row = 2  # Start after title rows (0-indexed)
    
    # Division types for reference (add as a note or separate area)
    division_examples = "CRJF, OJF, OTG, CRTG, W"
    
    # Add legend on the right side (starting at row 3)
    legend_format = workbook.add_format({
        'font_name': 'Times New Roman',
        'font_size': 10,
        'border': 1,
        'bg_color': 'white',
        'align': 'left',
        'valign': 'vcenter'
    })
    
    legend_bold = workbook.add_format({
        'font_name': 'Times New Roman',
        'font_size': 10,
        'bold': True,
        'border': 1,
        'bg_color': 'white',
        'align': 'left',
        'valign': 'vcenter'
    })
    
    legend_col = 2 + location_columns + 2  # First column after location columns + 2 padding columns
    legend_row = 2  # Start at row 3 (0-indexed)
    
    # Color Legend
    worksheet.write(legend_row, legend_col, 'Color Legend:', legend_bold)
    legend_row += 1
    worksheet.write(legend_row, legend_col, 'Grey:', legend_format)
    worksheet.write(legend_row, legend_col + 1, 'No game scheduled', grey_format)
    legend_row += 1
    worksheet.write(legend_row, legend_col, 'White:', legend_format)
    worksheet.write(legend_row, legend_col + 1, 'Not being played', white_format)
    legend_row += 1
    worksheet.write(legend_row, legend_col, 'Green:', legend_format)
    worksheet.write(legend_row, legend_col + 1, 'Scheduled', green_format)
    legend_row += 1
    worksheet.write(legend_row, legend_col, 'Yellow:', legend_format)
    worksheet.write(legend_row, legend_col + 1, 'Scheduled (alt)', yellow_format)
    legend_row += 1
    worksheet.write(legend_row, legend_col, 'Red:', legend_format)
    worksheet.write(legend_row, legend_col + 1, 'Not scheduled', red_format)
    
    legend_row += 2
    
    # Division Examples
    worksheet.write(legend_row, legend_col, 'Division Examples:', legend_bold)
    legend_row += 1
    worksheet.write(legend_row, legend_col, 'CRJF', legend_format)
    worksheet.write(legend_row, legend_col + 1, 'Co-Rec Just Fun', legend_format)
    legend_row += 1
    worksheet.write(legend_row, legend_col, 'OJF', legend_format)
    worksheet.write(legend_row, legend_col + 1, 'Open Just Fun', legend_format)
    legend_row += 1
    worksheet.write(legend_row, legend_col, 'OTG', legend_format)
    worksheet.write(legend_row, legend_col + 1, 'Open Top Gun', legend_format)
    legend_row += 1
    worksheet.write(legend_row, legend_col, 'CRTG', legend_format)
    worksheet.write(legend_row, legend_col + 1, 'Co-Rec Top Gun', legend_format)
    legend_row += 1
    worksheet.write(legend_row, legend_col, 'W', legend_format)
    worksheet.write(legend_row, legend_col + 1, 'Womens', legend_format)
    
    legend_row += 2
    worksheet.write(legend_row, legend_col, 'Instructions:', legend_bold)
    legend_row += 1
    worksheet.write(legend_row, legend_col, '1. Edit metadata below', legend_format)
    legend_row += 1
    worksheet.write(legend_row, legend_col, '2. Select division type', legend_format)
    legend_row += 1
    worksheet.write(legend_row, legend_col, '3. Type division number', legend_format)
    legend_row += 1
    worksheet.write(legend_row, legend_col, '4. Color cell green/yellow', legend_format)
    legend_row += 1
    worksheet.write(legend_row, legend_col, '5. Grey = no game', legend_format)
    
    # EDITABLE METADATA SECTION
    legend_row += 2
    
    # Section header
    editable_header_format = workbook.add_format({
        'font_name': 'Times New Roman',
        'bold': True,
        'font_size': 11,
        'align': 'left',
        'valign': 'vcenter',
        'border': 1,
        'bg_color': 'white',
        'font_color': 'black'
    })
    
    worksheet.merge_range(legend_row, legend_col, legend_row, legend_col + 1, 
                         '📋 EDITABLE METADATA & INSTRUCTIONS', editable_header_format)
    legend_row += 1
    
    # Create editable input format
    input_format = workbook.add_format({
        'font_name': 'Times New Roman',
        'font_size': 10,
        'border': 1,
        'bg_color': 'white',
        'align': 'center',
        'valign': 'vcenter'
    })
    
    # Min Refs per Game
    worksheet.write(legend_row, legend_col, 'Min Refs per Game:', legend_format)
    worksheet.write(legend_row, legend_col + 1, min_refs, input_format)
    legend_row += 1
    
    # Max Refs per Game
    worksheet.write(legend_row, legend_col, 'Max Refs per Game:', legend_format)
    worksheet.write(legend_row, legend_col + 1, max_refs, input_format)
    legend_row += 1
    
    # Additional Instructions
    editable_text_format = workbook.add_format({
        'font_name': 'Times New Roman',
        'font_size': 10,
        'border': 1,
        'bg_color': 'white',
        'align': 'left',
        'valign': 'top',
        'text_wrap': True
    })
    
    worksheet.write(legend_row, legend_col, 'Instructions:', legend_format)
    legend_row += 1
    # Set row heights BEFORE merging
    worksheet.set_row(legend_row, 25)
    worksheet.set_row(legend_row + 1, 25)
    worksheet.set_row(legend_row + 2, 25)
    worksheet.merge_range(legend_row, legend_col, legend_row + 2, legend_col + 1, 
                         'Add any special instructions or notes here...\n\n(You can edit this text)', 
                         editable_text_format)
    legend_row += 3
    
    # Notes
    worksheet.write(legend_row, legend_col, 'Notes:', legend_format)
    legend_row += 1
    # Set row heights BEFORE merging
    worksheet.set_row(legend_row, 25)
    worksheet.set_row(legend_row + 1, 25)
    worksheet.set_row(legend_row + 2, 25)
    worksheet.merge_range(legend_row, legend_col, legend_row + 2, legend_col + 1, 
                         'Add any additional notes here...\n\n(You can edit this text)', 
                         editable_text_format)
    legend_row += 3
    
    for day_idx, day_info in enumerate(days_schedule):
        day_name = day_info['day']
        day_date = day_info['date']
        times = day_info['times']
        
        # Row 3+: Headers
        worksheet.write(current_row, 0, 'Day', header_format)
        worksheet.write(current_row, 1, 'Time', header_format)
        
        # Location headers (C onwards) - each location gets 2 columns
        for loc_idx, loc in enumerate(locations):
            loc_header = f"{loc['descriptor']} {loc['number']}"
            div_type_col = 2 + (loc_idx * 2)
            div_num_col = 2 + (loc_idx * 2) + 1
            
            # Merge the two columns for the location header
            worksheet.merge_range(current_row, div_type_col, current_row, div_num_col, loc_header, header_format)
        
        current_row += 1
        
        # Row 4+: Day name and date
        worksheet.merge_range(current_row, 0, current_row, 1, day_name, day_format)
        
        # Merge all date cells (C onwards) into one cell - now spans all location columns (2 per location)
        last_location_col = 2 + (num_locations * 2) - 1
        if num_locations > 0:
            worksheet.merge_range(current_row, 2, current_row, last_location_col, day_date, date_format)
        
        current_row += 1
        
        # Rows 5+: Time slots with game cells
        for time_slot in times:
            # Time label (merged A-B)
            worksheet.merge_range(current_row, 0, current_row, 1, time_slot, time_format)
            
            # Game cells (C onwards) - each location has 2 columns: division type + division number
            for loc_idx in range(num_locations):
                div_type_col = 2 + (loc_idx * 2)
                div_num_col = 2 + (loc_idx * 2) + 1
                
                # Division Type column (left) - grey background with dropdown
                worksheet.write(current_row, div_type_col, '', grey_format)
                worksheet.data_validation(current_row, div_type_col, current_row, div_type_col, {
                    'validate': 'list',
                    'source': ['CRJF', 'OJF', 'OTG', 'CRTG', 'W'],
                    'input_title': 'Select Division Type',
                    'input_message': 'Select the division type from the dropdown',
                    'show_input': True,
                    'show_error': False
                })
                
                # Division Number column (right) - grey background for custom number entry
                worksheet.write(current_row, div_num_col, '', grey_format)
            
            current_row += 1
        
        # Add black separator row after each day
        if day_idx < len(days_schedule) - 1:
            # Fill separator with black background across schedule columns only (not legend)
            worksheet.set_row(current_row, 8)  # Reduced height for separator
            for col in range(2 + location_columns):
                worksheet.write(current_row, col, '', black_separator_format)
            current_row += 1
    
    workbook.close()
    output.seek(0)
    
    return output.getvalue()

def save_template_to_root(days_schedule=None, locations=None, min_refs=2, max_refs=3):
    """Save master template to DATA directory"""
    data = create_master_template(days_schedule, locations, min_refs, max_refs)
    root_dir = Path(__file__).resolve().parents[2]
    data_dir = root_dir / 'DATA'
    data_dir.mkdir(parents=True, exist_ok=True)
    out_path = data_dir / 'Master_Schedule_Template.xlsx'
    with open(out_path, 'wb') as f:
        f.write(data)
    return str(out_path)

if __name__ == "__main__":
    path = save_template_to_root()
    print(f"Saved template to: {path}")
