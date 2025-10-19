import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, time

# Add the parent directory to the path to import from phase1
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import utility functions
from dashboard.utils.file_processor import load_availability_data

# Import Game class from phase3
try:
    from phase3.Game import Game
except ImportError:
    st.error("Could not import Game class. Please ensure phase3/Game.py exists.")
    st.stop()

# Set page config
st.set_page_config(
    page_title="Game Management",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add CSS for wider container
st.markdown("""
<style>
.main > div {
    max-width: 95% !important;
}
.block-container {
    max-width: 95% !important;
}
</style>
""", unsafe_allow_html=True)

# Add table styling CSS for better readability
st.markdown("""
<style>
/* Table styling for better readability */
.stDataFrame, .stTable {
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

.stDataFrame th, .stTable th {
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    padding: 8px !important;
    font-weight: 600 !important;
}

.stDataFrame td, .stTable td {
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    padding: 8px !important;
}

.stDataFrame th:last-child, .stTable th:last-child,
.stDataFrame td:last-child, .stTable td:last-child {
    border-right: none !important;
}

.stDataFrame tr:last-child td, .stTable tr:last-child td {
    border-bottom: none !important;
}
</style>
""", unsafe_allow_html=True)

st.title("Game Management")

st.markdown("---")

# Load availability data
availability_df, has_availability_data = load_availability_data()

if not has_availability_data:
    st.error("**This step is locked**")
    st.markdown("**You must complete Step 1 first:**")
    st.markdown("1. Download template")
    st.markdown("2. Fill referee availability") 
    st.markdown("3. Upload completed file")
    st.markdown("4. 🔒 Create games")
    st.markdown("5. 🔒 Assign referees")
    st.markdown("6. 🔒 Export schedules")
    
    st.info("👈 Go back to **Step 1: Availability Setup** to get started")
    
    if st.button("Go to Availability Setup", width='stretch'):
        st.switch_page("pages/Availability_Setup.py")
    
else:

    # Initialize games in session state
    if 'games' not in st.session_state:
        st.session_state['games'] = []
    
    # Initialize unsaved changes tracking
    if 'unsaved_game_changes' not in st.session_state:
        st.session_state['unsaved_game_changes'] = False
    
    with st.expander("📋 Master Schedule Import/Export", expanded=True):
        st.write("Configure, download, fill out, and upload your master schedule template.")
        
        try:
            from dashboard.utils.master_template_generator import create_master_template
            
            # Create two columns for download and upload
            col_download, col_upload = st.columns([1, 1])
            
            with col_download:
                st.markdown("##### 📥 Download Template")
                
                # Day selection
                st.markdown("**Select Days**")
                col1, col2, col3, col4 = st.columns(4)
                days_selected = {}
                with col1:
                    days_selected['Sunday'] = st.checkbox("Sun", value=True, key="master_sun")
                    days_selected['Monday'] = st.checkbox("Mon", value=True, key="master_mon")
                with col2:
                    days_selected['Tuesday'] = st.checkbox("Tue", value=True, key="master_tue")
                    days_selected['Wednesday'] = st.checkbox("Wed", value=True, key="master_wed")
                with col3:
                    days_selected['Thursday'] = st.checkbox("Thu", value=True, key="master_thu")
                    days_selected['Friday'] = st.checkbox("Fri", value=False, key="master_fri")
                with col4:
                    days_selected['Saturday'] = st.checkbox("Sat", value=False, key="master_sat")
                
                # Time slot selection
                st.markdown("**Select Time Slots**")
                
                # Generate time options - All PM times
                time_options = []
                time_display_map = {}
                for hour in range(12, 24):
                    for minute in [0, 30]:
                        time_obj = time(hour, minute)
                        storage_format = time_obj.strftime("%I:%M").lstrip('0').lower() + " pm"
                        display_format = time_obj.strftime("%I:%M").lstrip('0')
                        time_options.append(storage_format)
                        time_display_map[storage_format] = display_format
                
                default_times = ['6:30 pm', '7:30 pm', '8:30 pm', '9:30 pm', '10:30 pm']
                valid_defaults = [t for t in default_times if t in time_options]
                
                selected_times = st.multiselect(
                    "Times (shown without 'pm'):",
                    options=time_options,
                    default=valid_defaults,
                    format_func=lambda x: time_display_map.get(x, x),
                    key="master_time_select"
                )
                
                # Metadata section
                st.markdown("**Other Metadata**")
                col1, col2 = st.columns(2)
                with col1:
                    master_min_refs = st.number_input(
                        "Min Refs",
                        min_value=1,
                        max_value=5,
                        value=2,
                        help="Minimum referees for all games",
                        key="master_min_refs"
                    )
                with col2:
                    master_max_refs = st.number_input(
                        "Max Refs",
                        min_value=1,
                        max_value=5,
                        value=3,
                        help="Maximum referees for all games",
                        key="master_max_refs"
                    )
                
                if master_max_refs < master_min_refs:
                    st.warning("⚠️ Max refs must be >= Min refs")
                
                # Location configuration
                st.markdown("**Configure Locations**")
                col1, col2 = st.columns(2)
                with col1:
                    location_descriptor = st.text_input(
                        "Descriptor",
                        value="Court",
                        key="master_loc_desc"
                    )
                with col2:
                    num_locations = st.number_input(
                        "Count",
                        min_value=1,
                        max_value=20,
                        value=6,
                        key="master_num_locs"
                    )
                
                # Date configuration
                st.markdown("**Configure Dates**")
                selected_days = [day for day, selected in days_selected.items() if selected]
                
                dates_input = {}
                for day in selected_days:
                    dates_input[day] = st.text_input(
                        f"{day}",
                        value="9/21, 9/28, 10/5, 10/12, 10/19",
                        key=f"master_date_{day}"
                    )
                
                # Generate template button
                if st.button("🎯 Generate & Download", width='stretch', type="primary"):
                    if not selected_times:
                        st.error("Please select at least one time slot!")
                    elif not selected_days:
                        st.error("Please select at least one day!")
                    else:
                        days_schedule = []
                        for day in selected_days:
                            days_schedule.append({
                                'day': day,
                                'date': dates_input[day],
                                'times': selected_times
                            })
                        
                        locations = []
                        for i in range(1, num_locations + 1):
                            locations.append({
                                'descriptor': location_descriptor,
                                'number': i
                            })
                        
                        template_data = create_master_template(
                            days_schedule=days_schedule,
                            locations=locations,
                            min_refs=master_min_refs,
                            max_refs=master_max_refs
                        )
                        
                        st.download_button(
                            label="📥 Download Master Schedule Template",
                            data=template_data,
                            file_name="Master_Schedule_Template.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="download_master_template_final"
                        )
                        st.success(f"✅ Template ready with {len(selected_days)} days, {len(selected_times)} times, {num_locations} locations!")
        
            with col_upload:
                st.markdown("##### 📤 Upload Filled Schedule")
                st.write("Upload your completed master schedule to import games.")
                
                # File upload
                uploaded_master = st.file_uploader(
                    "Choose filled Master Schedule",
                    type=['xlsx', 'xls'],
                    help="Upload the master schedule you filled out",
                    key="master_schedule_upload"
                )
                
                if uploaded_master is not None:
                    try:
                        from dashboard.utils.file_processor import process_master_schedule
                        
                        # Get min_refs and max_refs from session state (from download section)
                        min_refs = st.session_state.get('master_min_refs', 2)
                        max_refs = st.session_state.get('master_max_refs', 3)
                        
                        # Process the master schedule
                        imported_games, success = process_master_schedule(uploaded_master, min_refs=min_refs, max_refs=max_refs)
                        
                        if success and imported_games:
                            st.success(f"✅ Found {len(imported_games)} games in the master schedule!")
                            
                            # Show preview
                            st.write("**Preview of imported games:**")
                            preview_data = []
                            for game in imported_games[:5]:  # Show first 5
                                preview_data.append({
                                    'Game #': game.get_number(),
                                    'Date': game.get_date(),
                                    'Time': game.get_time(),
                                    'Location': game.get_location(),
                                    'Division': f"{game.get_division_type() or ''} - {game.get_division_number() or ''}"
                                })
                            
                            if preview_data:
                                st.dataframe(pd.DataFrame(preview_data), width='stretch')
                                if len(imported_games) > 5:
                                    st.write(f"... and {len(imported_games) - 5} more games")
                            
                            # Import button
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                if st.button("Import All Games", width='stretch', type="primary"):
                                    # Clear existing games
                                    st.session_state['games'] = imported_games
                                    st.session_state['unsaved_game_changes'] = True
                                    st.success(f"Imported {len(imported_games)} games! Scroll down to view and edit. Use 'Save All Changes' to persist.")
                                    st.rerun()
                            with col2:
                                if st.button("Add to Existing Games", width='stretch'):
                                    # Add to existing games
                                    if 'games' not in st.session_state:
                                        st.session_state['games'] = []
                                    st.session_state['games'].extend(imported_games)
                                    st.session_state['unsaved_game_changes'] = True
                                    st.success(f"Added {len(imported_games)} games! Scroll down to view and edit. Use 'Save All Changes' to persist.")
                                    st.rerun()
                        elif success and not imported_games:
                            st.warning("No scheduled games found. Make sure cells have division types AND are colored green/yellow.")
                            st.info("Tip: Grey cells are treated as 'no game scheduled'. Color cells green or yellow after filling them in.")
                        
                    except Exception as e:
                        st.error(f"Error importing master schedule: {e}")
                        import traceback
                        st.code(traceback.format_exc())
        
        except Exception as e:
            st.error(f"Error with master schedule: {e}")
            import traceback
            st.code(traceback.format_exc())
    
    # Show Add Game Form (outside tabs)
    if st.session_state.get('show_add_game_form', False):
        with st.form("add_game_form", clear_on_submit=True):
            st.markdown("#### Add New Game")
            
            # Game details inputs
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Game Number
                game_number = st.number_input(
                    "Game Number",
                    min_value=1,
                    value=len(st.session_state['games']) + 1,
                    help="Unique identifier for this game"
                )
                
                # Day of Week Selection
                day_of_week = st.selectbox(
                    "Day of Week",
                    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    help="Select the day this game will be played"
                )
                
                # Time Selection (30-minute intervals)
                time_options = []
                for hour in range(6, 24):  # 6 AM to 11:30 PM
                    for minute in [0, 30]:
                        time_obj = time(hour, minute)
                        time_str = time_obj.strftime("%I:%M %p")
                        time_options.append(time_str)
                
                game_time = st.selectbox(
                    "Time",
                    time_options,
                    index=time_options.index("06:30 PM") if "06:30 PM" in time_options else 0,
                    help="Select game start time (30-minute intervals)"
                )
                
                # Date (using day of week for now)
                game_date = st.date_input(
                    "Date",
                    value=datetime.now().date(),
                    help="Specific date for this game"
                )
            
            with col2:
                # Location fields
                location_descriptor = st.text_input(
                    "Location Descriptor",
                    value="Court",
                    help="e.g., Court, Field"
                )
                
                location_number = st.number_input(
                    "Location Number",
                    min_value=1,
                    value=1,
                    help="e.g., 1, 2, 3"
                )
                
                # Difficulty/Division
                difficulty = st.selectbox(
                    "Difficulty/Division",
                    ["Open - Just Fun", "Open - Top Gun", "Co-Rec - Just Fun", "Co-Rec - Top Gun", "Womens"],
                    help="Game difficulty level or division type"
                )
                
                # Min and Max Refs
                col_min, col_max = st.columns(2)
                with col_min:
                    min_refs = st.number_input(
                        "Min Refs",
                        min_value=1,
                        max_value=5,
                        value=2,
                        help="Minimum referees required"
                    )
                with col_max:
                    max_refs = st.number_input(
                        "Max Refs",
                        min_value=1,
                        max_value=5,
                        value=3,
                        help="Maximum referees allowed"
                    )
            
            with col3:
                # Division fields
                division_type = st.selectbox(
                    "Division Type",
                    ["CRJF", "OJF", "OTG", "CRTG", "W", ""],
                    index=5,
                    help="CRJF=Co-Rec Just Fun, OJF=Open Just Fun, OTG=Open Top Gun, CRTG=Co-Rec Top Gun, W=Womens"
                )
                
                division_number = st.text_input(
                    "Division Number",
                    value="",
                    help="e.g., 01, 02"
                    )
                
                # Ensure max >= min
                if max_refs < min_refs:
                    st.warning("Max refs must be >= Min refs")
            
            # Form buttons
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.form_submit_button("Add Game", width='stretch'):
                    # Validate inputs
                    if max_refs >= min_refs:
                        # Create new game
                        new_game = Game(
                            date=str(game_date),
                            time=game_time,
                            number=game_number,
                            difficulty=difficulty,
                            location=f"{location_descriptor} {location_number}",
                            min_refs=min_refs,
                            max_refs=max_refs,
                            location_descriptor=location_descriptor,
                            location_number=location_number,
                            division_type=division_type if division_type else None,
                            division_number=division_number if division_number else None
                        )
                        
                        # Add to session state
                        st.session_state['games'].append(new_game)
                        st.session_state['show_add_game_form'] = False
                        st.session_state['unsaved_game_changes'] = True
                        
                        st.success(f"Game {game_number} added successfully! Use 'Save All Changes' to persist.")
                        st.rerun()
                    else:
                        st.error("Max refs must be greater than or equal to Min refs")
            
            with col3:
                if st.form_submit_button("Cancel", width='stretch'):
                    st.session_state['show_add_game_form'] = False
                    st.rerun()

    # Current Games Management Section
    st.markdown("---")
    st.subheader("Current Games & Management")
    
    # Show unsaved changes warning and bulk save button
    if st.session_state.get('unsaved_game_changes', False):
        st.warning("**You have unsaved changes!** Use the 'Save All Changes' button below to persist your modifications.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Save All Game Changes", width='stretch', type="primary"):
                # Save games to session (they're already there)
                # The games are already in st.session_state['games'], so we just need to mark as saved
                st.session_state['unsaved_game_changes'] = False
                st.success("All game changes saved successfully!")
                st.rerun()
        
        st.markdown("---")
    
    if st.session_state['games']:
        # Games summary metrics
        total_games = len(st.session_state['games'])
        total_min_refs = sum(game.get_min_refs() for game in st.session_state['games'])
        total_max_refs = sum(game.get_max_refs() for game in st.session_state['games'])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Games", total_games)
        with col2:
            st.metric("Min Refs Needed", total_min_refs)
        with col3:
            st.metric("Max Refs Needed", total_max_refs)
        with col4:
            st.metric("Total Locations", len(set(g.get_location() for g in st.session_state['games'])))
        
        # Download and Upload section for simple Excel format
        st.markdown("---")
        col_download, col_upload = st.columns(2)
        
        with col_download:
            st.markdown("**📥 Download for Editing**")
            st.write("Download games in simple Excel format to easily edit min/max refs")
            
            import pandas as pd
            import io
            
            games_data = []
            for game in st.session_state['games']:
                games_data.append({
                    'Game_Number': game.get_number(),
                    'Date': game.get_date(),
                    'Time': game.get_time(),
                    'Location_Descriptor': game.get_location_descriptor(),
                    'Location_Number': game.get_location_number(),
                    'Difficulty': game.get_difficulty(),
                    'Division_Type': game.get_division_type() or '',
                    'Division_Number': game.get_division_number() or '',
                    'Min_Refs': game.get_min_refs(),
                    'Max_Refs': game.get_max_refs(),
                })
            
            games_df = pd.DataFrame(games_data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                games_df.to_excel(writer, sheet_name='Games', index=False)
            
            st.download_button(
                label="📥 Download Games Excel",
                data=output.getvalue(),
                file_name="games_for_editing.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_current_games",
                help="Download to edit min/max refs in Excel"
            )
        
        with col_upload:
            st.markdown("**📤 Upload Edited Games**")
            st.write("Upload the edited Excel file to update min/max refs")
            
            uploaded_games_excel = st.file_uploader(
                "Choose edited games Excel",
                type=['xlsx', 'xls'],
                help="Upload the games Excel you edited",
                key="upload_edited_games"
            )
            
            if uploaded_games_excel is not None:
                try:
                    edited_games_df = pd.read_excel(uploaded_games_excel)
                    st.success(f"Loaded {len(edited_games_df)} games from Excel")
                    
                    # Show preview
                    st.write("**Preview:**")
                    st.dataframe(edited_games_df.head(3), width='stretch')
                    
                    if st.button("Update Games", width='stretch', type="primary", key="update_from_excel"):
                        # Update existing games
                        updated_count = 0
                        for _, row in edited_games_df.iterrows():
                            game_num = int(row['Game_Number'])
                            # Find game by number
                            for game in st.session_state['games']:
                                if game.get_number() == game_num:
                                    # Update all fields from Excel
                                    game.set_date(str(row['Date']))
                                    game.set_time(str(row['Time']))
                                    game.set_location_descriptor(str(row['Location_Descriptor']))
                                    game.set_location_number(int(row['Location_Number']))
                                    game.set_difficulty(str(row['Difficulty']))
                                    game.set_division_type(str(row['Division_Type']) if row['Division_Type'] else None)
                                    game.set_division_number(str(row['Division_Number']) if row['Division_Number'] else None)
                                    game.set_min_refs(int(row['Min_Refs']))
                                    game.set_max_refs(int(row['Max_Refs']))
                                    updated_count += 1
                                    break
                        
                        st.session_state['unsaved_game_changes'] = True
                        st.success(f"Updated {updated_count} games! Use 'Save All Changes' to persist.")
                        st.rerun()
                
                except Exception as e:
                    st.error(f"Error reading Excel file: {e}")
                    import traceback
                    st.code(traceback.format_exc())
        
        # Sort games by game number
        sorted_games_with_index = sorted(
            enumerate(st.session_state['games']), 
            key=lambda x: x[1].get_number()
        )
        
        # Game editing interface
        for display_idx, (original_idx, game) in enumerate(sorted_games_with_index):
            with st.expander(f"Game #{game.get_number()} - {game.get_date()} {game.get_time()}", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Editable fields
                    new_number = st.number_input(
                        "Game Number",
                        min_value=1,
                        value=game.get_number(),
                        key=f"edit_number_{original_idx}"
                    )
                    
                    new_date = st.text_input(
                        "Date",
                        value=game.get_date(),
                        key=f"edit_date_{original_idx}"
                    )
                    
                    new_time = st.text_input(
                        "Time",
                        value=game.get_time(),
                        key=f"edit_time_{original_idx}"
                    )
                    
                with col2:
                    # Location fields
                    new_location_descriptor = st.text_input(
                        "Location Descriptor",
                        value=game.get_location_descriptor(),
                        key=f"edit_loc_desc_{original_idx}",
                        help="e.g., Court, Field"
                    )
                    
                    new_location_number = st.number_input(
                        "Location Number",
                        min_value=1,
                        value=game.get_location_number(),
                        key=f"edit_loc_num_{original_idx}"
                    )
                    
                    difficulty_options = ["Open - Just Fun", "Open - Top Gun", "Co-Rec - Just Fun", "Co-Rec - Top Gun", "Womens", "TBD"]
                    current_difficulty = game.get_difficulty()
                    try:
                        difficulty_index = difficulty_options.index(current_difficulty)
                    except ValueError:
                        difficulty_index = 5  # Default to "TBD" if not found
                    
                    new_difficulty = st.selectbox(
                        "Difficulty",
                        difficulty_options,
                        index=difficulty_index,
                        key=f"edit_difficulty_{original_idx}"
                    )
                
                with col3:
                    # Division fields
                    division_options = ["CRJF", "OJF", "OTG", "CRTG", "W", ""]
                    current_division_type = game.get_division_type() or ""
                    try:
                        division_index = division_options.index(current_division_type)
                    except ValueError:
                        division_index = 5  # Default to empty
                    
                    new_division_type = st.selectbox(
                        "Division Type",
                        division_options,
                        index=division_index,
                        key=f"edit_div_type_{original_idx}",
                        help="CRJF=Co-Rec Just Fun, OJF=Open Just Fun, OTG=Open Top Gun, CRTG=Co-Rec Top Gun, W=Womens"
                    )
                    
                    new_division_number = st.text_input(
                        "Division Number",
                        value=game.get_division_number() or "",
                        key=f"edit_div_num_{original_idx}",
                        help="e.g., 01, 02"
                    )
                    
                    col_min, col_max = st.columns(2)
                    with col_min:
                        new_min_refs = st.number_input(
                            "Min Refs",
                            min_value=1,
                            max_value=5,
                            value=game.get_min_refs(),
                            key=f"edit_min_refs_{original_idx}"
                        )
                    with col_max:
                        new_max_refs = st.number_input(
                            "Max Refs",
                            min_value=1,
                            max_value=5,
                            value=game.get_max_refs(),
                            key=f"edit_max_refs_{original_idx}"
                        )
                    
                
                # Action buttons
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button(f"Update Game", key=f"update_{original_idx}"):
                        if new_max_refs >= new_min_refs:
                            # Update game attributes
                            game.set_number(new_number)
                            game.set_date(new_date)
                            game.set_time(new_time)
                            game.set_location_descriptor(new_location_descriptor)
                            game.set_location_number(new_location_number)
                            game.set_difficulty(new_difficulty)
                            game.set_division_type(new_division_type if new_division_type else None)
                            game.set_division_number(new_division_number if new_division_number else None)
                            game.set_min_refs(new_min_refs)
                            game.set_max_refs(new_max_refs)
                            st.session_state['unsaved_game_changes'] = True
                            st.success("Game updated! Use 'Save All Changes' to persist.")
                            st.rerun()
                        else:
                            st.error("Max refs must be >= Min refs")
                with col3:
                    if st.button(f"Delete Game", key=f"delete_{original_idx}"):
                        # Find and remove the game object from the list
                        st.session_state['games'].remove(game)
                        st.session_state['unsaved_game_changes'] = True
                        st.success("Game deleted! Use 'Save All Changes' to persist.")
                        st.rerun()
        
        # Add single game option at bottom
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Add Another Game", width='stretch'):
                st.session_state['show_add_game_form'] = True
                st.rerun()
        
    else:
        st.info("**No games created yet!** Use the tabs above to create games, then they will appear here for editing.")
    
