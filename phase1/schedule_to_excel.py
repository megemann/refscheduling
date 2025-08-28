import xlsxwriter
from datetime import datetime

import Ref
import Game

def schedule_to_excel(refs):
    workbook = xlsxwriter.Workbook('DATA/schedule.xlsx')
    
    # Get all days and times from the games
    days = set()
    all_times = set()
    for ref in refs:
        for game in ref.games:
            day, time = game.get_time_slot().split('_')
            days.add(day)
            all_times.add(time)

    # Sort days by day of week and times chronologically
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    days = sorted(days, key=lambda day: day_order.index(day) if day in day_order else 999)
    times = sorted(list(all_times))
    
    # Define formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#881C1C',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    name_format = workbook.add_format({
        'bg_color': '#FFCCCB',  # Peach
        'align': 'left',
        'valign': 'vcenter',
        'border': 1
    })
    
    time_format = workbook.add_format({
        'bg_color': '#696969',  # Mid-dark grey
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    verification_format = workbook.add_format({
        'bg_color': '#D3D3D3',  # Light grey
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    comments_format = workbook.add_format({
        'bg_color': '#696969',  # Mid-dark grey
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    # Create a sheet for each day
    for day in days:
        worksheet = workbook.add_worksheet(day)
        
        # Set current date (you can modify this to use actual dates)
        current_date = f"{day} - [Insert Date]"
        
        # Row 0: Date header
        worksheet.merge_range('A1:Z1', current_date, header_format)
        
        # Row 1: Main headers
        col = 0
        
        # Official's Name header (merged across 2 rows)
        worksheet.merge_range(1, col, 2, col, "Official's Name", header_format)
        worksheet.set_column(col, col, 20)
        col += 1
        
        # Time headers
        worksheet.write(1, col, "Time", header_format)
        for time in times:
            worksheet.write(2, col, time, header_format)
            worksheet.set_column(col, col, 8)
            col += 1
        
        # Verification headers
        start_verification = col
        worksheet.write(1, col, "Verification", header_format)
        for time in times:
            worksheet.write(2, col, time, header_format)
            worksheet.set_column(col, col, 8)
            col += 1
        
        # Comments/Late header
        worksheet.merge_range(1, col, 2, col, "Comments / Late", header_format)
        worksheet.set_column(col, col, 15)
        
        # Get refs that work on this day
        refs_for_day = []
        for ref in refs:
            ref_times_this_day = []
            for game in ref.games:
                if game.date == day:
                    ref_times_this_day.append(game.time)
            
            # Include refs that have games this day OR are available this day
            has_availability = any(ref.availability.get(f"{day}_{time}", False) for time in times)
            if ref_times_this_day or has_availability:
                refs_for_day.append((ref, ref_times_this_day))
        
        # Sort refs alphabetically
        refs_for_day.sort(key=lambda x: x[0].name)
        
        # Fill in referee data
        row = 3  # Start after headers
        for ref, scheduled_times in refs_for_day:
            # Official's Name
            worksheet.write(row, 0, ref.name, name_format)
            
            # Time columns
            col = 1
            for time in times:
                if time in scheduled_times:
                    worksheet.write(row, col, "✓", time_format)
                else:
                    worksheet.write(row, col, "-", time_format)
                col += 1
            
            # Verification columns
            for time in times:
                worksheet.write(row, col, "", verification_format)
                col += 1
            
            # Comments column
            worksheet.write(row, col, "", comments_format)
            
            row += 1
        
        # Set row heights
        worksheet.set_row(0, 25)  # Date row
        worksheet.set_row(1, 20)  # Header row 1
        worksheet.set_row(2, 20)  # Header row 2

    workbook.close()

