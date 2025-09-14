import xlsxwriter
from datetime import datetime
import os

def schedule_to_excel(refs, games, output_path='DATA/schedule.xlsx'):
    """
    Generate an Excel schedule from referees and games using the new Ref class structure.
    
    Args:
        refs: List of Ref objects with new class structure
        games: List of Game objects
        output_path: Path to save the Excel file
    """
    # Ensure DATA directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    workbook = xlsxwriter.Workbook(output_path)
    
    # Get all unique days and times from games
    days = set()
    all_times = set()
    
    # Create a mapping of referee assignments from their optimized_games (preferred) or assigned_games (manual)
    ref_assignments = {}
    for ref in refs:
        ref_name = ref.get_name()
        
        # Use optimized assignments if available, otherwise fall back to manual assignments
        optimized_games = ref.get_optimized_games()
        if optimized_games:
            # Use optimized game assignments directly (these are already Game objects)
            ref_assignments[ref_name] = optimized_games
            for game in optimized_games:
                days.add(game.get_date())
                all_times.add(game.get_time())
        else:
            # Fall back to manual assignments (need to convert game numbers to Game objects)
            assigned_game_numbers = ref.get_assigned_games()
            ref_assignments[ref_name] = []
            
            # Find the actual game objects for assigned game numbers
            for game in games:
                if game.get_number() in assigned_game_numbers:
                    ref_assignments[ref_name].append(game)
                    days.add(game.get_date())
                    all_times.add(game.get_time())
    
    # Also collect all days/times from all games for comprehensive view
    for game in games:
        days.add(game.get_date())
        all_times.add(game.get_time())

    # Sort days by day of week and times chronologically
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    days = sorted(days, key=lambda day: day_order.index(day) if day in day_order else 999)
    
    # Sort times chronologically using a simple time parser
    def parse_time_for_sort(time_str):
        try:
            # Handle various time formats
            if 'AM' in time_str.upper() or 'PM' in time_str.upper():
                return datetime.strptime(time_str.upper(), "%I:%M %p").time()
            else:
                # Assume 24-hour format or just hour:minute
                if ':' in time_str:
                    return datetime.strptime(time_str, "%H:%M").time()
                else:
                    return datetime.strptime(f"{time_str}:00", "%H:%M").time()
        except:
            # Fallback
            return datetime.strptime("12:00", "%H:%M").time()
    
    times = sorted(list(all_times), key=parse_time_for_sort)
    
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
        
        # Set current date header
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
        start_time_col = col
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
        
        # Get refs that work on this day or are available
        refs_for_day = []
        for ref in refs:
            ref_name = ref.get_name()
            scheduled_times_this_day = []
            
            # Check if ref has assigned games on this day
            if ref_name in ref_assignments:
                for game in ref_assignments[ref_name]:
                    if game.get_date() == day:
                        scheduled_times_this_day.append(game.get_time())
            
            # Check if ref is available on this day (from availability matrix)
            has_availability = False
            availability = ref.get_availability()
            if isinstance(availability, (list, tuple)):
                # Simple check if ref has any availability
                has_availability = any(availability)
            elif isinstance(availability, dict):
                # Check for day-specific availability
                day_keys = [k for k in availability.keys() if day.lower() in k.lower()]
                has_availability = any(availability.get(k, False) for k in day_keys)
            
            # Include refs that have games this day OR are available this day
            if scheduled_times_this_day or has_availability:
                refs_for_day.append((ref, scheduled_times_this_day))
        
        # Sort refs alphabetically
        refs_for_day.sort(key=lambda x: x[0].get_name())
        
        # Fill in referee data
        row = 3  # Start after headers
        for ref, scheduled_times in refs_for_day:
            # Official's Name
            worksheet.write(row, 0, ref.get_name(), name_format)
            
            # Time columns
            col = start_time_col
            for time in times:
                if time in scheduled_times:
                    # Find game location for this time slot
                    game_location = ""
                    ref_name = ref.get_name()
                    if ref_name in ref_assignments:
                        for game in ref_assignments[ref_name]:
                            if game.get_date() == day and game.get_time() == time:
                                game_location = game.get_location()
                                break
                    worksheet.write(row, col, game_location or "✓", time_format)
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

    # --- ADDITION: "All Assignments" Sheet (columns by day with times listed) ---
    all_assignments_sheet = workbook.add_worksheet("All Assignments")
    
    # Collect all assigned games by referee
    ref_assignments = {}
    for ref in refs:
        ref_name = ref.get_name()
        assigned_games = []
        # Use optimized if available, else manual
        if ref.get_optimized_games():
            assigned_games = ref.get_optimized_games()
        else:
            assigned_game_numbers = set(ref.get_assigned_games())
            assigned_games = [g for g in games if g.get_number() in assigned_game_numbers]
        
        if assigned_games:
            ref_assignments[ref_name] = assigned_games
    
    # Get all unique days from assignments
    all_days = set()
    for games_list in ref_assignments.values():
        for game in games_list:
            all_days.add(game.get_date())
    
    # Sort days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    sorted_days = sorted(all_days, key=lambda day: day_order.index(day) if day in day_order else 999)
    
    # Set up headers
    total_cols = 1 + len(sorted_days)  # Name + one column per day
    all_assignments_sheet.merge_range(0, 0, 0, total_cols-1, "All Assignments - [Insert Date]", header_format)
    
    # Column 0: Official's Name
    all_assignments_sheet.write(1, 0, "Official's Name", header_format)
    all_assignments_sheet.set_column(0, 0, 20)
    
    # Day headers
    for i, day in enumerate(sorted_days):
        all_assignments_sheet.write(1, i + 1, day, header_format)
        all_assignments_sheet.set_column(i + 1, i + 1, 15)
    
    # Fill in referee data
    row = 2  # Start after headers
    sorted_refs = sorted(ref_assignments.keys())
    
    for ref_name in sorted_refs:
        games_list = ref_assignments[ref_name]
        
        # Official's Name
        all_assignments_sheet.write(row, 0, ref_name, name_format)
        
        # Group games by day for this referee
        ref_games_by_day = {}
        for game in games_list:
            day = game.get_date()
            if day not in ref_games_by_day:
                ref_games_by_day[day] = []
            ref_games_by_day[day].append(game.get_time())
        
        # Fill day columns
        for i, day in enumerate(sorted_days):
            col = i + 1
            if day in ref_games_by_day:
                # Sort times and join with commas
                times = sorted(ref_games_by_day[day], key=parse_time_for_sort)
                times_text = ", ".join(times)
                all_assignments_sheet.write(row, col, times_text, time_format)
            else:
                all_assignments_sheet.write(row, col, "-", time_format)
        
        row += 1
    
    # Set row heights
    all_assignments_sheet.set_row(0, 25)  # Date row
    all_assignments_sheet.set_row(1, 20)  # Header row

    workbook.close()
    return output_path

def generate_schedule_from_session_state(session_state, output_path='DATA/schedule.xlsx'):
    """
    Convenience function to generate schedule from Streamlit session state.
    
    Args:
        session_state: Streamlit session state containing 'referees' and 'games'
        output_path: Path to save the Excel file
    """
    refs = session_state.get('referees', [])
    games = session_state.get('games', [])
    
    if not refs:
        raise ValueError("No referees found in session state")
    if not games:
        raise ValueError("No games found in session state")
    
    return schedule_to_excel(refs, games, output_path)
