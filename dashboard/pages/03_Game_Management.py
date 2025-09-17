import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, time

# Add the parent directory to the path to import from phase1
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import utility functions
from dashboard.utils.file_processor import load_availability_data

# Import Game class
try:
    from phase2.Game import Game
except ImportError:
    st.error("Could not import Game class. Please ensure phase2/Game.py exists.")
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

    # Game Management Section
    st.markdown("---")
    st.subheader("Game Management")
    
    # Create subtabs for different game creation methods
    tab1, tab2, tab3 = st.tabs(["Bulk Creation", "Excel Input", "Fusion Parser"])
    
    with tab1:
        st.markdown("#### Bulk Game Creation")
        st.write("Create multiple games quickly using the existing time slot interface, then customize details individually.")
        
        # Default settings for bulk creation
        col1, col2 = st.columns(2)
        with col1:
            default_min_refs = st.number_input(
                "Default Min Refs",
                min_value=1,
                max_value=5,
                value=2,
                help="Default minimum referees for all games"
            )
        with col2:
            default_max_refs = st.number_input(
                "Default Max Refs", 
                min_value=1,
                max_value=5,
                value=3,
                help="Default maximum referees for all games"
            )
        
        if default_max_refs < default_min_refs:
            st.warning("Max refs must be >= Min refs")
        
        # Move the existing bulk creation logic here
        st.write("Enter the number of games needed for each time slot:")
        
        # Create time slot summary for games input
        time_slot_data = []
        for col in availability_df.columns:
            if '_' in col:
                try:
                    day, time_str = col.split('_', 1)
                    count = availability_df[col].sum()
                    time_slot_data.append({
                        'Day': day,
                        'Time': time_str,
                        'Available_Refs': int(count),
                        'Column': col
                    })
                except Exception as e:
                    continue

        if time_slot_data and default_max_refs >= default_min_refs:
            # Sort by day order then by time
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            time_slot_df = pd.DataFrame(time_slot_data)
            time_slot_df['day_sort'] = time_slot_df['Day'].apply(lambda x: day_order.index(x) if x in day_order else 999)
            
            # Parse time strings for proper sorting (earliest time first)
            def parse_time_for_sort(time_str):
                """Convert time string to comparable format for sorting"""
                try:
                    from datetime import datetime
                    # Parse time string like "6:30 PM" or "10:30 AM"
                    time_obj = datetime.strptime(time_str, "%I:%M %p")
                    return time_obj.time()
                except:
                    # If parsing fails, return a default time for sorting
                    return datetime.strptime("12:00 PM", "%I:%M %p").time()
            
            time_slot_df['time_sort'] = time_slot_df['Time'].apply(parse_time_for_sort)
            time_slot_df = time_slot_df.sort_values(['day_sort', 'time_sort']).drop(['day_sort', 'time_sort'], axis=1)
        
            # Create input fields for each time slot
            games_data = []
            prev_day = None
            for idx, row in time_slot_df.iterrows():
                # Insert a border when the day changes (but not before the first day)
                if prev_day is not None and row['Day'] != prev_day:
                    st.markdown('<hr style="border-top: 2px solid #bbb; margin: 0.5em 0;">', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                with col1:
                    st.write(f"**{row['Day']}**")
                with col2:
                    st.write(f"{row['Time']}")
                with col3:
                    st.write(f"{row['Available_Refs']} refs available")
                with col4:
                    num_games = st.number_input(
                        "Games",
                        min_value=0,
                        max_value=10,
                        value=0,
                        key=f"bulk_games_{row['Column']}",
                        label_visibility="collapsed"
                    )
                    games_data.append({
                        'Day': row['Day'],
                        'Time': row['Time'],
                        'Available_Refs': row['Available_Refs'],
                        'Games_Needed': num_games,
                        'Column': row['Column']
                    })
                prev_day = row['Day']
        
            # Create games button
            if st.button("Create Bulk Games", width='stretch', type="primary"):
                games_to_create = [g for g in games_data if g['Games_Needed'] > 0]
                if games_to_create:
                    games_created = 0
                    next_game_number = len(st.session_state['games']) + 1
                    
                    # Sort games_to_create by day and time to ensure earliest time first
                    def parse_time_for_creation(time_str):
                        """Convert time string to comparable format for creation order"""
                        try:
                            from datetime import datetime
                            time_obj = datetime.strptime(time_str, "%I:%M %p")
                            return time_obj.time()
                        except:
                            return datetime.strptime("12:00 PM", "%I:%M %p").time()
                    
                    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    games_to_create_sorted = sorted(games_to_create, key=lambda x: (
                        day_order.index(x['Day']) if x['Day'] in day_order else 999,
                        parse_time_for_creation(x['Time'])
                    ))
                    
                    for game_slot in games_to_create_sorted:
                        for game_num in range(game_slot['Games_Needed']):
                            new_game = Game(
                                date=game_slot['Day'],  # Will need to be updated individually
                                time=game_slot['Time'],
                                number=next_game_number,
                                difficulty="TBD",  # To be determined individually
                                location="TBD",  # To be determined individually
                                min_refs=default_min_refs,
                                max_refs=default_max_refs
                            )
                            st.session_state['games'].append(new_game)
                            next_game_number += 1
                            games_created += 1
                    
                    st.session_state['unsaved_game_changes'] = True
                    st.success(f"Created {games_created} games! Scroll down to customize individual game details. Use 'Save All Changes' to persist.")
                    st.rerun()
                else:
                    st.warning("Please set at least one game for a time slot.")
    
    with tab2:
        st.markdown("#### Excel Input")
        st.write("Upload a pre-filled Excel file with game details, or download a template to fill out.")
        
        # Download template button
        if st.button("Download Game Template", width='stretch'):
            # Create sample Excel template
            import pandas as pd
            import io
            
            sample_data = {
                'Game_Number': [1, 2, 3],
                'Date': ['2024-01-15', '2024-01-15', '2024-01-16'],
                'Time': ['6:30 PM', '7:30 PM', '6:30 PM'],
                'Location': ['Boyden Ct 1', 'Boyden Ct 2', 'Boyden Ct 1'],
                'Difficulty': ['Open - Top Gun', 'Open - Just Fun', 'Co-Rec - Just Fun'],
                'Min_Refs': [2, 2, 2],
                'Max_Refs': [3, 3, 3]
            }
            
            template_df = pd.DataFrame(sample_data)
            
            # Create download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                template_df.to_excel(writer, sheet_name='Games', index=False)
            
            st.download_button(
                label="Download Template",
                data=output.getvalue(),
                file_name="game_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose Excel file",
            type=['xlsx', 'xls'],
            help="Upload the completed game template"
        )
        
        if uploaded_file is not None:
            try:
                games_df = pd.read_excel(uploaded_file)
                st.success(f"Loaded {len(games_df)} games from Excel")
                st.dataframe(games_df, width='stretch')
                
                if st.button("Import Games", width='stretch', type="primary"):
                    # Clear existing games when importing
                    st.session_state['games'] = []
                    imported_count = 0
                    for _, row in games_df.iterrows():
                        new_game = Game(
                            date=str(row['Date']),
                            time=str(row['Time']),
                            number=int(row['Game_Number']),
                            difficulty=str(row['Difficulty']),
                            location=str(row['Location']),
                            min_refs=int(row['Min_Refs']),
                            max_refs=int(row['Max_Refs'])
                        )
                        st.session_state['games'].append(new_game)
                        imported_count += 1
                    
                    st.session_state['unsaved_game_changes'] = True
                    st.success(f"Imported {imported_count} games successfully! Use 'Save All Changes' to persist.")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error reading Excel file: {e}")
        
        st.info("**Tip:** Download the template first, fill it out with your game details, then upload it here.")
    
    with tab3:
        st.markdown("#### Fusion Text Parser")
        st.write("🚧 **Work in Progress** - Parse game data from Fusion website text")
        
        st.info("This feature will allow you to paste text from the Fusion website and automatically create games.")
        
        # Text input for fusion data
        fusion_text = st.text_area(
            "Paste Fusion text here:",
            placeholder="""O-TG 01
Sundays 9:30 pm @ Boyden Ct 4
Sundays 9:30 pm @ Boyden Ct 5
1 free agent
5/5 teams""",
            height=200,
            help="Paste the text block from Fusion website"
        )
        
        if fusion_text and st.button("Parse Fusion Text", width='stretch'):
            st.warning("🚧 Parser not yet implemented. This will be available in a future update.")
            st.code(fusion_text, language="text")
    
    # Show Add Game Form (outside tabs)
    if st.session_state.get('show_add_game_form', False):
        with st.form("add_game_form", clear_on_submit=True):
            st.markdown("#### Add New Game")
            
            # Game details inputs
            col1, col2 = st.columns(2)
            
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
                
                # Location
                location = st.text_input(
                    "Location",
                    value="Boyden Ct 1",
                    help="Court or field where game will be played"
                )
            
            with col2:
                # Date (using day of week for now)
                game_date = st.date_input(
                    "Date",
                    value=datetime.now().date(),
                    help="Specific date for this game"
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
                            location=location,
                            min_refs=min_refs,
                            max_refs=max_refs
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
            # Download current games as Excel
            import pandas as pd
            import io
            
            games_data = []
            for game in st.session_state['games']:
                games_data.append({
                    'Game_Number': game.get_number(),
                    'Date': game.get_date(),
                    'Time': game.get_time(),
                    'Location': game.get_location(),
                    'Difficulty': game.get_difficulty(),
                    'Min_Refs': game.get_min_refs(),
                    'Max_Refs': game.get_max_refs(),
                })
            
            games_df = pd.DataFrame(games_data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                games_df.to_excel(writer, sheet_name='Games', index=False)
            
            st.download_button(
                label="Download Games Excel",
                data=output.getvalue(),
                file_name="current_games.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_current_games"
            )
        
        # Sort games by game number
        sorted_games_with_index = sorted(
            enumerate(st.session_state['games']), 
            key=lambda x: x[1].get_number()
        )
        
        # Game editing interface
        for display_idx, (original_idx, game) in enumerate(sorted_games_with_index):
            with st.expander(f"Game #{game.get_number()} - {game.get_date()} {game.get_time()}", expanded=False):
                col1, col2 = st.columns(2)
                
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
                    
                    new_location = st.text_input(
                        "Location",
                        value=game.get_location(),
                        key=f"edit_location_{original_idx}"
                    )
                
                with col2:
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
                            game.set_location(new_location)
                            game.set_difficulty(new_difficulty)
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
    
