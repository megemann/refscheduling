import xlsxwriter

import Ref
import Game

def schedule_to_excel(refs):
    workbook = xlsxwriter.Workbook('schedule.xlsx')
    worksheet = workbook.add_worksheet('Schedule')

    # Get all days from the games
    days = set()
    for ref in refs:
        for game in ref.games:
            days.add(game.get_time_slot().split('_')[0])

    # Sort days by day of week (Monday first, Sunday last)
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    days = sorted(days, key=lambda day: day_order.index(day) if day in day_order else 999)
    
    # Write headers
    headers = ['Name'] + list(days) 
    print(headers)
    header_fmt = workbook.add_format({"bold": True, 'bg_color': '#000000', 'font_color': 'white', 'border': 1, 'border_color': 'black'})
    worksheet.write_row(0, 0, headers, header_fmt)
    
    # Set column widths - day columns should be 4 times wider
    worksheet.set_column(0, 0, 30)  # Name column
    for i, day in enumerate(days):
        worksheet.set_column(i + 1, i + 1, 30)  # Day columns (4 times wider)

    # Create UMass maroon format for time cells with white text and black borders
    umass_maroon_fmt = workbook.add_format({'bg_color': '#881C1C', 'font_color': 'white', 'border': 1, 'border_color': 'black'})
    # Create format for name cells with black borders
    name_fmt = workbook.add_format({'border': 1, 'border_color': 'black'})

    for ref in refs:
        times_per_day = {
            day: [] for day in days
        }
        for game in ref.games:
            # Format time to match image format (remove leading zeros and ensure colon format)
            formatted_time = game.time.lstrip('0') if game.time.startswith('0') else game.time
            if ':' not in formatted_time:
                # If no colon, assume it's just hour and add :00
                formatted_time += ':00'
            times_per_day[game.date].append(formatted_time)
        row_data = [ref.name]
        row_index = refs.index(ref) + 1
        
        # Write ref name with black borders
        worksheet.write(row_index, 0, ref.name, name_fmt)
        
        # Write times with UMass maroon background, white text, and black borders for each day
        for col_index, day in enumerate(days):
            times = times_per_day[day]
            # Sort times from earliest to latest
            times.sort(key=lambda t: (int(t.split(':')[0]) % 12 + (12 if 'PM' in t or (int(t.split(':')[0]) >= 12 and 'AM' not in t) else 0), int(t.split(':')[1])))
            cell_text = ', '.join(times) if times else ''
            
            # Apply UMass maroon background with white text and black borders to all time cells
            worksheet.write(row_index, col_index + 1, cell_text, umass_maroon_fmt)
            

    workbook.close()

