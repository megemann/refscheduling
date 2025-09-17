import streamlit as st
import pandas as pd
import sys
import os
import time
from datetime import datetime

# Add the parent directory to the path to import from phase2
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Set page config
st.set_page_config(
    page_title="Schedule Management",
    page_icon="📊",
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

# Add CSS for page border and table styling
st.markdown("""
<style>
/* Page-wide border for Schedule Management */
.main > div {
    max-width: 95% !important;
    border: 2px solid white !important;
    border-radius: 12px !important;
    padding: 20px !important;
    margin: 10px auto !important;
}
.block-container {
    max-width: 95% !important;
    border: 2px solid white !important;
    border-radius: 12px !important;
    padding: 20px !important;
    margin: 10px auto !important;
}

/* Table styling for better readability */
.stDataFrame, .stTable {
    border: 1px solid white !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

.stDataFrame th, .stTable th {
    border-bottom: 1px solid white !important;
    border-right: 1px solid white !important;
    padding: 8px !important;
    font-weight: 600 !important;
}

.stDataFrame td, .stTable td {
    border-bottom: 1px solid white !important;
    border-right: 1px solid white !important;
    padding: 8px !important;
}

.stDataFrame th:last-child, .stTable th:last-child,
.stDataFrame td:last-child, .stTable td:last-child {
    border-right: none !important;
}

.stDataFrame tr:last-child td, .stTable tr:last-child td {
    border-bottom: none !important;
}

/* Schedule results row styling */
.schedule-row {
    border-bottom: 1px solid white;
    padding: 8px 4px;
    margin-bottom: 4px;
}

.schedule-row:last-child {
    border-bottom: none;
}

/* Individual referee expander styling */
div[data-testid="stExpander"] {
    border-bottom: 1px solid white !important;
    margin-bottom: 8px !important;
    padding-bottom: 8px !important;
}

div[data-testid="stExpander"]:last-child {
    border-bottom: none !important;
}
</style>
""", unsafe_allow_html=True)

st.title("Schedule Management")
st.markdown("View and manage game schedules and referee assignments")

# Initialize unsaved changes tracking
if 'unsaved_schedule_changes' not in st.session_state:
    st.session_state['unsaved_schedule_changes'] = False

# Check for basic requirements and constraint violations before loading the page
constraint_violations = []
game_count = len(st.session_state.get('games', []))
ref_count = len(st.session_state.get('referees', []))

# Check if we have the basic requirements
if game_count == 0:
    st.error("**No games found!**")
    st.markdown("You need to create games before you can manage schedules.")
    st.info("Use the sidebar to navigate to Game Management to create games.")
    st.stop()

if ref_count == 0:
    st.error("**No referees found!**")
    st.markdown("You need to add referees before you can manage schedules.")
    st.info("Use the sidebar to navigate to Referee Management to add referees.")
    st.stop()

# Now check for constraint violations
if 'games' in st.session_state and st.session_state['games'] and 'referees' in st.session_state and st.session_state['referees']:
    # Group games by day + time slot combination
    time_slot_games = {}
    for game in st.session_state['games']:
        # Create a key that combines both day and time
        day_time_key = f"{game.get_date()}_{game.get_time()}"
        if day_time_key not in time_slot_games:
            time_slot_games[day_time_key] = []
        time_slot_games[day_time_key].append(game)

    # Check each day+time slot for constraint violations
    for day_time_slot, games in time_slot_games.items():
        available_refs_at_time = 0
        total_min_refs_needed = 0
        
        # Extract day and time from the key
        day_part, time_part = day_time_slot.split('_', 1)
        
        # Count available referees at this specific day+time slot
        time_columns = st.session_state.get('time_columns', [])
        for ref in st.session_state['referees']:
            if hasattr(ref, 'get_availability'):
                availability = ref.get_availability()
                # Find the exact day+time slot index in time_columns
                for i, time_col in enumerate(time_columns):
                    # Match both day and time in the column name (e.g., "Monday_6:30 PM")
                    if day_part in time_col and time_part in time_col:
                        if isinstance(availability, (list, tuple)) and i < len(availability):
                            if availability[i]:
                                available_refs_at_time += 1
                        break
        
        # Sum up minimum refs needed for all games at this time slot
        for game in games:
            if hasattr(game, 'get_min_refs'):
                total_min_refs_needed += game.get_min_refs()
        
        # Check constraint
        if available_refs_at_time < total_min_refs_needed:
            constraint_violations.append({
                'time_slot': day_time_slot.replace('_', ' at '),  # Format as "Monday at 6:30 PM"
                'available': available_refs_at_time,
                'needed': total_min_refs_needed,
                'games': len(games)
            })

# If there are constraint violations, show error and exit
if constraint_violations:
    st.error("**Cannot proceed with scheduling due to constraint violations!**")
    st.markdown("### Problems Found:")
    
    for violation in constraint_violations:
        st.markdown(f"**{violation['time_slot']}**: Only {violation['available']} refs available, but {violation['needed']} minimum refs needed for {violation['games']} games")
    
    st.markdown("---")
    st.markdown("### Solutions:")
    st.markdown("1. **Reduce number of games** at problematic time slots")
    st.markdown("2. **Add more referees** with availability at those times")
    st.markdown("3. **Move games** to different time slots with more referee availability")
    st.markdown("4. **Reduce minimum referee requirements** for some games")
    
    st.info("Use the sidebar to navigate to Game Management or Referee Management to fix these issues.")
    
    st.stop()  # Stop execution here if there are violations

# If we get here, no constraint violations - show simplified summary
st.success("**All constraints satisfied!** Ready for scheduling.")

st.markdown("---")
st.subheader("Scheduling Workflow")

# Create workflow tabs
workflow_tab1, workflow_tab2, workflow_tab3, workflow_tab4 = st.tabs(["Step 1: Manual Assignments", "Step 2: Parameters", "Step 3: Review & Optimize", "Step 4: Results & Export"])

with workflow_tab1:
    st.markdown("### Manual Referee Assignments")
    st.markdown("Manually assign referees to specific games. This creates hard constraints for the optimizer.")
    
    # Initialize user_constraints in session state if not exists
    # Note: User constraints and hour limits are now stored directly in Ref objects
    # No longer using session state dictionaries for these
    
    # Get all unique days and times from games
    if 'games' in st.session_state and st.session_state['games']:
        # Create a mapping of day-time to games
        day_time_games = {}
        all_days = set()
        all_times = set()
        
        for game in st.session_state['games']:
            day = game.get_date()
            time_slot = game.get_time()
            all_days.add(day)
            all_times.add(time_slot)
            
            if day not in day_time_games:
                day_time_games[day] = {}
            if time not in day_time_games[day]:
                day_time_games[day][time_slot] = []
            
            day_time_games[day][time_slot].append(game)
        
        # Sort days and times with proper day order
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        sorted_days = sorted(all_days, key=lambda x: day_order.index(x) if x in day_order else 999)
        
        def parse_time_safely(time_str):
            """Parse time string handling both '6:30 PM' and '6:30' formats"""
            try:
                # Try with AM/PM first
                return datetime.strptime(time_str, "%I:%M %p").time()
            except ValueError:
                try:
                    # Try without AM/PM (assume 24-hour or just hour:minute)
                    return datetime.strptime(time_str, "%H:%M").time()
                except ValueError:
                    try:
                        # Try with just hour:minute - special logic for 11 vs 11:01+
                        time_obj = datetime.strptime(time_str, "%I:%M")
                        hour = time_obj.hour
                        minute = time_obj.minute
                        
                        # 11:00 = PM, 11:01+ = AM, everything else follows normal rules
                        if hour == 11 and minute == 0:
                            # 11:00 should be PM
                            return time_obj.replace(hour=23).time()
                        elif hour == 11 and minute > 0:
                            # 11:01+ should be AM
                            return time_obj.time()
                        elif hour == 12:
                            # 12:xx should be PM
                            return time_obj.time()
                        else:
                            # Everything else defaults to AM
                            return time_obj.time()
                    except ValueError:
                        # Default fallback
                        return datetime.strptime("12:00", "%H:%M").time()
        
        sorted_times = sorted(all_times, key=parse_time_safely)
        
        # Create assignment table
        if st.session_state.get('referees'):
            st.markdown("#### Assignment Matrix")
            st.markdown("Select games for each referee at each day/time slot.")
            
            
            # Create grid layout by days with full width
            # Calculate optimal column widths for full screen usage
            total_day_cols = len(sorted_days)
            ref_name_width = 2
            hour_limit_width = 1.5
            day_width = (10 - ref_name_width - hour_limit_width) / total_day_cols if total_day_cols > 0 else 1
            col_widths = [ref_name_width] + [day_width]*total_day_cols + [hour_limit_width]
            day_cols = st.columns(col_widths)
            
            # Header row
            with day_cols[0]:
                st.markdown("### Referee")
            for i, day in enumerate(sorted_days):
                with day_cols[i + 1]:
                    st.markdown(f"### {day}")
            with day_cols[-1]:
                st.markdown("### Hour Limit")
            
            # Display matrix with time slots as rows
            for ref_idx, ref in enumerate(st.session_state['referees']):
                # Add white divider line before each referee row (except the first one)
                if ref_idx > 0:
                    st.markdown('<hr style="border: 1px solid white; margin: 8px 0;">', unsafe_allow_html=True)
                
                ref_name = ref.get_name()
                
                # Referee name and hour limit row
                cols = st.columns(col_widths)
                with cols[0]:
                    st.markdown(f"**{ref_name}**")
                for day_idx, day in enumerate(sorted_days):
                    with cols[day_idx + 1]:
                        st.markdown("")  # Empty for referee name row
                with cols[-1]:
                    current_hour_limit = ref.get_max_hours()
                    hour_limit = st.number_input(
                        "Max Hours",
                        min_value=0,
                        max_value=50,
                        value=current_hour_limit,
                        key=f"hour_limit_{ref_name}_{ref_idx}",
                        label_visibility="visible"
                    )
                    if hour_limit != current_hour_limit:
                        ref.set_max_hours(hour_limit)
                        st.session_state['unsaved_schedule_changes'] = True
                
                # Create a row for each time slot
                for time_slot in sorted_times:
                    time_cols = st.columns(col_widths)
                    
                    # Empty column for referee name area
                    with time_cols[0]:
                        st.markdown(f"**{time_slot}**")
                    
                    # Create selection for each day at this time
                    for day_idx, day in enumerate(sorted_days):
                        with time_cols[day_idx + 1]:
                            if day in day_time_games and time_slot in day_time_games[day]:
                                games_at_time = day_time_games[day][time_slot]
                                
                                # Check if ref is available at this time
                                time_columns = st.session_state.get('time_columns', [])
                                is_available = False
                                for i, time_col in enumerate(time_columns):
                                    if day in time_col and time_slot in time_col:
                                        if hasattr(ref, 'get_availability'):
                                            availability = ref.get_availability()
                                            if isinstance(availability, (list, tuple)) and i < len(availability):
                                                if availability[i]:
                                                    is_available = True
                                        break
                                
                                if is_available:
                                    # Create game options for dropdown with location and difficulty
                                    game_options = ["None"]
                                    for game in games_at_time:
                                        location = game.get_location() if hasattr(game, 'get_location') else "Unknown"
                                        difficulty = game.get_difficulty() if hasattr(game, 'get_difficulty') else "Unknown"
                                        game_option = f"G:{game.get_number()} - L:{location} - D:{difficulty}"
                                        game_options.append(game_option)
                                    
                                    # Find current selection
                                    current_selection = "None"
                                    assigned_games = ref.get_assigned_games()
                                    for game in games_at_time:
                                        if game.get_number() in assigned_games:
                                            location = game.get_location() if hasattr(game, 'get_location') else "Unknown"
                                            difficulty = game.get_difficulty() if hasattr(game, 'get_difficulty') else "Unknown"
                                            current_selection = f"G:{game.get_number()} - L:{location} - D:{difficulty}"
                                            break
                                    
                                    try:
                                        current_index = game_options.index(current_selection)
                                    except ValueError:
                                        current_index = 0
                                    
                                    selected = st.selectbox(
                                        f"Game",
                                        game_options,
                                        index=current_index,
                                        key=f"assign_{ref_name}_{day}_{time_slot}_{ref_idx}",
                                        label_visibility="collapsed"
                                    )
                                    
                                    # Update ref assignments based on selection and track changes
                                    current_assigned_games = ref.get_assigned_games()
                                    if selected != "None":
                                        # Extract game number from format "G:{number} - L:{location} - D:{difficulty}"
                                        game_num = int(selected.split("G:")[1].split(" - ")[0])
                                        if game_num not in current_assigned_games:
                                            ref.add_assigned_game(game_num)
                                            st.session_state['unsaved_schedule_changes'] = True
                                    else:
                                        # Remove any games at this time from assignments
                                        for game in games_at_time:
                                            if game.get_number() in current_assigned_games:
                                                ref.remove_assigned_game(game.get_number())
                                                st.session_state['unsaved_schedule_changes'] = True
                                else:
                                    # Show time slot but indicate not available
                                    st.markdown("*(N/A)*")
                            else:
                                # Show time slot but indicate no games
                                st.markdown("*(No games)*")
                    
                    # Empty column for hour limit area
                    with time_cols[-1]:
                        st.markdown("")
        else:
            st.info("No referees found. Please add referees first.")
    else:
        st.info("No games found. Please create games first.")

with workflow_tab2:
    st.markdown("### Optimization Parameters")
    st.markdown("Configure constraints and weights for the scheduling algorithm.")
    
    # Initialize parameters in session state if not exists
    if 'schedule_params' not in st.session_state:
        st.session_state['schedule_params'] = {
            'max_hours_per_week': 15,
            'max_hours_per_day': 6,
            'weight_hour_balancing': 2.5,
            'weight_skill_combo': 2.5,
            'weight_low_skill_penalty': 2.5,
            'weight_shift_block_penalty': 2.5,
            'weight_effort_bonus': 2.5
        }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Hour Constraints")
        
        current_max_hours_week = st.session_state['schedule_params']['max_hours_per_week']
        max_hours_week = st.number_input(
            "Max Hours per Week",
            min_value=1,
            max_value=50,
            value=current_max_hours_week,
            help="Maximum hours any referee can work in a week"
        )
        if max_hours_week != current_max_hours_week:
            st.session_state['schedule_params']['max_hours_per_week'] = max_hours_week
            st.session_state['unsaved_schedule_changes'] = True
        
        current_max_hours_day = st.session_state['schedule_params']['max_hours_per_day']
        max_hours_day = st.number_input(
            "Max Hours per Day",
            min_value=1,
            max_value=24,
            value=current_max_hours_day,
            help="Maximum hours any referee can work in a single day"
        )
        if max_hours_day != current_max_hours_day:
            st.session_state['schedule_params']['max_hours_per_day'] = max_hours_day
            st.session_state['unsaved_schedule_changes'] = True
    
    with col2:
        st.markdown("#### Optimization Weights")
        st.markdown("**Scale: 0-400%** (0%=disable, 100%=baseline, 400%=max emphasis)")
        st.markdown("*Start with 100% for balanced objectives*")
        
        # Helper functions to convert between percentage and underlying scale
        def percentage_to_weight(percentage):
            return percentage / 100.0 * 2.5  # 100% = 2.5, 400% = 10.0
        
        def weight_to_percentage(weight):
            return weight / 2.5 * 100.0  # 2.5 = 100%, 10.0 = 400%
        
        current_hour_balancing = weight_to_percentage(st.session_state['schedule_params']['weight_hour_balancing'])
        weight_hour_balancing_pct = st.slider(
            "Hour Balancing",
            min_value=0.0,
            max_value=400.0,
            value=current_hour_balancing,
            step=5.0,
            format="%.0f%%",
            help="Importance of balancing hours across referees (0%=disable, 100%=baseline, 400%=max emphasis)"
        )
        if weight_hour_balancing_pct != current_hour_balancing:
            st.session_state['schedule_params']['weight_hour_balancing'] = percentage_to_weight(weight_hour_balancing_pct)
            st.session_state['unsaved_schedule_changes'] = True
        
        current_skill_combo = weight_to_percentage(st.session_state['schedule_params']['weight_skill_combo'])
        weight_skill_combo_pct = st.slider(
            "High-Low Skill Combination",
            min_value=0.0,
            max_value=400.0,
            value=current_skill_combo,
            step=5.0,
            format="%.0f%%",
            help="Importance of pairing high and low skill referees (0%=disable, 100%=baseline, 400%=max emphasis)"
        )
        if weight_skill_combo_pct != current_skill_combo:
            st.session_state['schedule_params']['weight_skill_combo'] = percentage_to_weight(weight_skill_combo_pct)
            st.session_state['unsaved_schedule_changes'] = True
        
        current_low_skill_penalty = weight_to_percentage(st.session_state['schedule_params']['weight_low_skill_penalty'])
        weight_low_skill_penalty_pct = st.slider(
            "Low Skill on High Games Penalty",
            min_value=0.0,
            max_value=400.0,
            value=current_low_skill_penalty,
            step=5.0,
            format="%.0f%%",
            help="Penalty for assigning low skill refs to high difficulty games (0%=disable, 100%=baseline, 400%=max emphasis)"
        )
        if weight_low_skill_penalty_pct != current_low_skill_penalty:
            st.session_state['schedule_params']['weight_low_skill_penalty'] = percentage_to_weight(weight_low_skill_penalty_pct)
            st.session_state['unsaved_schedule_changes'] = True
        
        current_shift_block_penalty = weight_to_percentage(st.session_state['schedule_params']['weight_shift_block_penalty'])
        weight_shift_block_penalty_pct = st.slider(
            "Shift Block Penalty",
            min_value=0.0,
            max_value=400.0,
            value=current_shift_block_penalty,
            step=5.0,
            format="%.0f%%",
            help="Penalty for assigning too many consecutive shifts (0%=disable, 100%=baseline, 400%=max emphasis)"
        )
        if weight_shift_block_penalty_pct != current_shift_block_penalty:
            st.session_state['schedule_params']['weight_shift_block_penalty'] = percentage_to_weight(weight_shift_block_penalty_pct)
            st.session_state['unsaved_schedule_changes'] = True
        
        current_effort_bonus = weight_to_percentage(st.session_state['schedule_params']['weight_effort_bonus'])
        weight_effort_bonus_pct = st.slider(
            "High Effort Bonus",
            min_value=0.0,
            max_value=400.0,
            value=current_effort_bonus,
            step=5.0,
            format="%.0f%%",
            help="Bonus for giving more hours to high effort referees (0%=disable, 100%=baseline, 400%=max emphasis)"
        )
        if weight_effort_bonus_pct != current_effort_bonus:
            st.session_state['schedule_params']['weight_effort_bonus'] = percentage_to_weight(weight_effort_bonus_pct)
            st.session_state['unsaved_schedule_changes'] = True

# Show save warning and button if there are unsaved changes
if st.session_state.get('unsaved_schedule_changes', False):
    st.warning("⚠️ You have unsaved schedule configuration changes!")
    if st.button("Save Schedule Configuration", type="primary", width='stretch'):
        st.session_state['unsaved_schedule_changes'] = False
        st.success("Schedule configuration saved successfully!")
        st.rerun()

with workflow_tab3:
    st.markdown("### Configuration Review")
    st.markdown("Review all settings before running the optimizer.")
    
    # Display user constraints from ref objects
    st.markdown("#### Manual Assignments")
    if 'referees' in st.session_state and st.session_state['referees']:
        assignments_found = False
        for ref in st.session_state['referees']:
            assigned_games = ref.get_assigned_games()
            if assigned_games:  # Only show refs with assignments
                st.write(f"**{ref.get_name()}**: Games {', '.join(map(str, assigned_games))}")
                assignments_found = True
        if not assignments_found:
            st.info("No manual assignments made.")
    else:
        st.info("No referees found.")
    
    # Display hour limits from ref objects
    st.markdown("#### Individual Hour Limits")
    if 'referees' in st.session_state and st.session_state['referees']:
        ref_limits_df = pd.DataFrame([
            {'Referee': ref.get_name(), 'Hour Limit': ref.get_max_hours()} 
            for ref in st.session_state['referees']
        ])
        st.dataframe(ref_limits_df, width='stretch', hide_index=True)
    else:
        st.info("No referees found.")
    
    # Display optimization parameters
    st.markdown("#### Optimization Parameters")
    if 'schedule_params' in st.session_state:
        params_df = pd.DataFrame([
            {'Parameter': 'Max Hours per Week', 'Value': st.session_state['schedule_params']['max_hours_per_week']},
            {'Parameter': 'Max Hours per Day', 'Value': st.session_state['schedule_params']['max_hours_per_day']},
            {'Parameter': 'Hour Balancing Weight', 'Value': st.session_state['schedule_params']['weight_hour_balancing']},
            {'Parameter': 'Skill Combo Weight', 'Value': st.session_state['schedule_params']['weight_skill_combo']},
            {'Parameter': 'Low Skill Penalty Weight', 'Value': st.session_state['schedule_params']['weight_low_skill_penalty']},
            {'Parameter': 'Shift Block Penalty Weight', 'Value': st.session_state['schedule_params']['weight_shift_block_penalty']},
            {'Parameter': 'Effort Bonus Weight', 'Value': st.session_state['schedule_params']['weight_effort_bonus']}
        ])
        st.dataframe(params_df, width='stretch', hide_index=True)
    else:
        st.info("No parameters configured.")
    
    # Summary counts
    st.markdown("#### Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        manual_assignments = 0
        if 'referees' in st.session_state:
            manual_assignments = sum(len(ref.get_assigned_games()) for ref in st.session_state['referees'])
        st.metric("Manual Assignments", manual_assignments)
    
    with col2:
        total_refs = len(st.session_state.get('referees', []))
        st.metric("Total Referees", total_refs)
    
    with col3:
        total_games = len(st.session_state.get('games', []))
        st.metric("Total Games", total_games)
    
    # Optimization button
    st.markdown("---")
    st.markdown("#### 🚀 Run Optimization")
    st.markdown("Ready to optimize? This will use all your constraints and parameters to create the best possible schedule.")
    
    # Initialize optimization state
    if 'optimization_running' not in st.session_state:
        st.session_state['optimization_running'] = False
    if 'optimization_start_time' not in st.session_state:
        st.session_state['optimization_start_time'] = None
    
    # Max wait time: 4 minutes = 240 seconds
    MAX_WAIT_TIME = 240
    
    if st.button("Optimize Schedule", type="primary", width='stretch'):
        if 'referees' in st.session_state and 'games' in st.session_state:
            # Clean up any existing progress file
            try:
                import os
                if os.path.exists('optimization_progress.json'):
                    os.remove('optimization_progress.json')
            except:
                pass
            
            # Start optimization process
            st.session_state['optimization_running'] = True
            st.session_state['optimization_start_time'] = time.time()
            st.session_state['optimization_started'] = False
            st.rerun()
        else:
            st.error("Please ensure both referees and games are loaded before optimizing.")
    
    # Show optimization status if active
    if st.session_state.get('optimization_running', False):
        
        # Calculate time information
        start_time = st.session_state['optimization_start_time']
        elapsed_time = time.time() - start_time
        completion_time = start_time + MAX_WAIT_TIME
        
        # Convert completion time to readable format
        from datetime import datetime
        completion_datetime = datetime.fromtimestamp(completion_time)
        completion_str = completion_datetime.strftime("%I:%M:%S %p")
        
        # Display optimization information
        st.markdown("### 🚀 Optimization in Progress")
        
        # Create centered container for spinner
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Custom CSS for bigger spinner
            st.markdown("""
            <style>
            .big-spinner {
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 30px;
            }
            .big-spinner .stSpinner > div {
                width: 80px !important;
                height: 80px !important;
                border-width: 4px !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Big spinner with custom message
            with st.spinner(f"Optimizing schedule... Max runtime: 4 minutes"):
                # Show completion time info
                st.markdown(f"""
                <div style="text-align: center; margin-top: 20px; padding: 15px; background-color: #1f1f1f; border-radius: 8px; border: 1px solid #444;">
                    <h4 style="color: #ffffff; margin: 0;">⏰ Estimated Completion</h4>
                    <p style="color: #00ff00; font-size: 1.2em; margin: 10px 0;">{completion_str}</p>
                    <p style="color: #cccccc; font-size: 0.9em; margin: 0;">Max runtime: 4 minutes 30 seconds</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Check if we should run optimization
        if not st.session_state.get('optimization_started', False):
            st.session_state['optimization_started'] = True
            st.rerun()  # Restart to show progress immediately
        
        # If optimization has started but not run yet, run it now
        if st.session_state.get('optimization_started', False) and not st.session_state.get('optimization_executed', False):
            st.session_state['optimization_executed'] = True
            
            st.info("🚀 Running optimization algorithm...")
            
            try:
                # Import scheduler
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
                from phase2.scheduler import Scheduler
                
                # Create scheduler instance
                scheduler = Scheduler(st.session_state['referees'], st.session_state['games'])
                
                # Set parameters if available
                if 'schedule_params' in st.session_state:
                    scheduler.set_parameters(st.session_state['schedule_params'])
                
                # Run optimization with progress indication
                with st.spinner("Running optimization algorithm..."):
                    result = scheduler.optimize()
                
                # Clean up progress file
                try:
                    import os
                    if os.path.exists('optimization_progress.json'):
                        os.remove('optimization_progress.json')
                except:
                    pass
                
                # Reset optimization state
                st.session_state['optimization_running'] = False
                st.session_state['optimization_started'] = False
                st.session_state['optimization_executed'] = False
                st.session_state['optimization_start_time'] = None
                
                if isinstance(result, dict) and result.get('success'):
                    # Update session state with optimized results
                    st.session_state['referees'] = result['refs']  # Updated referee objects with assignments
                    st.session_state['optimization_complete'] = True
                    st.session_state['optimization_assignments'] = result['assignments']
                    
                    st.success("✅ Optimization completed successfully!")
                    st.info("Navigate to the 'Results & Export' tab to view the schedule and export to Excel.")
                    st.rerun()  # Refresh to show new results
                else:
                    error_msg = result.get('error', 'Unknown error') if isinstance(result, dict) else 'Optimization failed'
                    st.error(f"❌ Optimization failed: {error_msg}")
                    st.info("Check the console/terminal for detailed debug output.")
            except Exception as e:
                # Clean up progress file on error
                try:
                    import os
                    if os.path.exists('optimization_progress.json'):
                        os.remove('optimization_progress.json')
                except:
                    pass
                
                # Reset optimization state on error
                st.session_state['optimization_running'] = False
                st.session_state['optimization_started'] = False
                st.session_state['optimization_executed'] = False
                st.session_state['optimization_start_time'] = None
                st.error(f"❌ Error during optimization: {str(e)}")
        else:
            # Show spinner while optimization runs
            pass  # Spinner will be shown from the with st.spinner block

with workflow_tab4:
    st.markdown("### Results & Export")
    
    # Check if optimization has been completed
    if st.session_state.get('optimization_complete', False):
        st.success("Optimization completed! Results are ready for review.")
        
        # Import display utilities
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from utils.schedule_display import display_optimized_schedule, display_game_coverage
        from utils.schedule_to_excel import generate_schedule_from_session_state
        
        # Display the optimized schedule
        display_optimized_schedule(st.session_state['referees'], st.session_state['games'])
        
        st.markdown("---")
        
        # Display game coverage analysis
        display_game_coverage(st.session_state['games'])
        
        st.markdown("---")
        
        # Export functionality
        st.markdown("### Export Schedule")
        st.markdown("Export your optimized schedule to Excel format for sharing and printing.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                # Generate Excel file
                output_path = generate_schedule_from_session_state(st.session_state)
                
                # Read the file for download
                with open(output_path, 'rb') as file:
                    excel_data = file.read()
                
                # Provide direct download button
                st.download_button(
                    label="Export to Excel",
                    data=excel_data,
                    file_name="referee_schedule.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    width='stretch'
                )
                
            except Exception as e:
                st.error(f"Error generating Excel file: {str(e)}")
        
        with col2:
            if st.button("Re-run Optimization", width='stretch'):
                # Clear optimization results to allow re-running
                st.session_state['optimization_complete'] = False
                if 'optimization_assignments' in st.session_state:
                    del st.session_state['optimization_assignments']
                st.info("Navigate back to 'Step 3: Review' to re-run the optimization.")
                st.rerun()
        
        # Show raw assignment data if needed (for debugging)
        if st.checkbox("Show Raw Assignment Data", help="Display the raw optimization results for debugging"):
            if 'optimization_assignments' in st.session_state:
                assignments = st.session_state['optimization_assignments']
                st.markdown("#### Raw Assignment Data")
                st.json(assignments)
            else:
                st.info("No raw assignment data available.")
    
    else:
        st.info("No optimization results yet. Complete the optimization in 'Step 3: Review' to see results here.")
        
        # Show current manual assignments if any
        manual_assignments = []
        if 'referees' in st.session_state:
            for ref in st.session_state['referees']:
                assigned_games = ref.get_assigned_games()
                if assigned_games:
                    manual_assignments.extend([
                        {
                            'Referee': ref.get_name(),
                            'Game #': game_num,
                            'Assignment Type': 'Manual'
                        }
                        for game_num in assigned_games
                    ])
        
        if manual_assignments:
            st.markdown("#### Current Manual Assignments")
            manual_df = pd.DataFrame(manual_assignments)
            st.dataframe(manual_df, width='stretch', hide_index=True)
        else:
            st.markdown("#### Current Manual Assignments")
            st.info("No manual assignments made yet.")

st.markdown("---")
st.subheader("Data Summary")

# Simple counts and metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Games", game_count)

with col2:
    st.metric("Total Referees", ref_count)

with col3:
    total_min_refs = sum(game.get_min_refs() for game in st.session_state['games'])
    st.metric("Min Refs Needed", total_min_refs)

with col4:
    time_columns = st.session_state.get('time_columns', [])
    total_availability = 0
    for ref in st.session_state['referees']:
        if hasattr(ref, 'get_availability'):
            availability = ref.get_availability()
            if isinstance(availability, (list, tuple)):
                total_availability += sum(availability)
    st.metric("Total Availability", total_availability)
