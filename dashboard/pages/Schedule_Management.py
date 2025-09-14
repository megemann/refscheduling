import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# Add the parent directory to the path to import from phase2
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Set page config
st.set_page_config(
    page_title="Schedule Management",
    page_icon="📅",
    layout="centered"
)

st.title("📅 Schedule Management")
st.markdown("View and manage game schedules and referee assignments")

# Check for basic requirements and constraint violations before loading the page
constraint_violations = []
game_count = len(st.session_state.get('games', []))
ref_count = len(st.session_state.get('referees', []))

# Check if we have the basic requirements
if game_count == 0:
    st.error("🚫 **No games found!**")
    st.markdown("You need to create games before you can manage schedules.")
    st.info("💡 Use the sidebar to navigate to Game Management to create games.")
    st.stop()

if ref_count == 0:
    st.error("🚫 **No referees found!**")
    st.markdown("You need to add referees before you can manage schedules.")
    st.info("💡 Use the sidebar to navigate to Referee Management to add referees.")
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
    st.error("🚫 **Cannot proceed with scheduling due to constraint violations!**")
    st.markdown("### ⚠️ Problems Found:")
    
    for violation in constraint_violations:
        st.markdown(f"**{violation['time_slot']}**: Only {violation['available']} refs available, but {violation['needed']} minimum refs needed for {violation['games']} games")
    
    st.markdown("---")
    st.markdown("### 💡 Solutions:")
    st.markdown("1. **Reduce number of games** at problematic time slots")
    st.markdown("2. **Add more referees** with availability at those times")
    st.markdown("3. **Move games** to different time slots with more referee availability")
    st.markdown("4. **Reduce minimum referee requirements** for some games")
    
    st.info("💡 Use the sidebar to navigate to Game Management or Referee Management to fix these issues.")
    
    st.stop()  # Stop execution here if there are violations

# If we get here, no constraint violations - show simplified summary
st.success("✅ **All constraints satisfied!** Ready for scheduling.")

st.markdown("---")
st.subheader("🔄 Scheduling Workflow")

# Create workflow tabs
workflow_tab1, workflow_tab2, workflow_tab3, workflow_tab4 = st.tabs(["Step 1: Manual Assignments", "Step 2: Parameters", "Step 3: Review & Optimize", "Step 4: Results & Export"])

with workflow_tab1:
    st.markdown("### 📅 Manual Referee Assignments")
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
            time = game.get_time()
            all_days.add(day)
            all_times.add(time)
            
            if day not in day_time_games:
                day_time_games[day] = {}
            if time not in day_time_games[day]:
                day_time_games[day][time] = []
            
            day_time_games[day][time].append(game)
        
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
            
            # Add CSS for grid styling - Dark mode and full width
            st.markdown("""
            <style>
            .main > div {
                max-width: 100% !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
            .block-container {
                max-width: 100% !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
            .grid-container {
                width: 100%;
                border: 2px solid #4a4a4a;
                border-collapse: collapse;
            }
            .grid-cell {
                border: 1px solid #4a4a4a !important;
                padding: 8px !important;
                margin: 0 !important;
                background-color: #2b2b2b !important;
                color: white !important;
            }
            .grid-header {
                border: 2px solid #4a4a4a !important;
                padding: 8px !important;
                margin: 0 !important;
                background-color: #1a1a1a !important;
                color: white !important;
                font-weight: bold;
                text-align: center;
            }
            .grid-ref-name {
                border: 1px solid #4a4a4a !important;
                padding: 8px !important;
                margin: 0 !important;
                background-color: #333333 !important;
                color: white !important;
                font-weight: bold;
            }
            div[data-testid="column"] {
                border-right: 1px solid #4a4a4a;
                padding: 4px;
                background-color: #2b2b2b;
            }
            div[data-testid="column"]:last-child {
                border-right: 2px solid #4a4a4a;
            }
            /* Style the selectboxes for dark mode */
            .stSelectbox > div > div {
                background-color: #2b2b2b !important;
                color: white !important;
                border: 1px solid #4a4a4a !important;
            }
            /* Style the number inputs for dark mode */
            .stNumberInput > div > div > input {
                background-color: #2b2b2b !important;
                color: white !important;
                border: 1px solid #4a4a4a !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Create grid layout by days with full width
            # Calculate optimal column widths for full screen usage
            total_day_cols = len(sorted_days)
            ref_name_width = 2
            hour_limit_width = 1.5
            day_width = (10 - ref_name_width - hour_limit_width) / total_day_cols if total_day_cols > 0 else 1
            col_widths = [ref_name_width] + [day_width]*total_day_cols + [hour_limit_width]
            day_cols = st.columns(col_widths)
            
            # Header row with borders
            with day_cols[0]:
                st.markdown('<div class="grid-header">Referee</div>', unsafe_allow_html=True)
            for i, day in enumerate(sorted_days):
                with day_cols[i + 1]:
                    st.markdown(f'<div class="grid-header">{day}</div>', unsafe_allow_html=True)
            with day_cols[-1]:
                st.markdown('<div class="grid-header">Hour Limit</div>', unsafe_allow_html=True)
            
            # Display each referee
            for ref_idx, ref in enumerate(st.session_state['referees']):
                ref_name = ref.get_name()
                
                # Create columns for this referee row with same widths as header
                cols = st.columns(col_widths)
                
                # Referee name column with border
                with cols[0]:
                    st.markdown(f'<div class="grid-ref-name">{ref_name}</div>', unsafe_allow_html=True)
                
                # Day columns
                for day_idx, day in enumerate(sorted_days):
                    with cols[day_idx + 1]:
                        st.markdown('<div class="grid-cell">', unsafe_allow_html=True)
                        
                        # For each time slot in this day, create a selection
                        for time in sorted_times:
                            if day in day_time_games and time in day_time_games[day]:
                                games_at_time = day_time_games[day][time]
                                
                                # Check if ref is available at this time
                                time_columns = st.session_state.get('time_columns', [])
                                is_available = False
                                for i, time_col in enumerate(time_columns):
                                    if day in time_col and time in time_col:
                                        if hasattr(ref, 'get_availability'):
                                            availability = ref.get_availability()
                                            if isinstance(availability, (list, tuple)) and i < len(availability):
                                                if availability[i]:
                                                    is_available = True
                                        break
                                
                                if is_available:
                                    # Create game options for dropdown
                                    game_options = ["None"] + [f"Game #{game.get_number()}" for game in games_at_time]
                                    
                                    # Find current selection
                                    current_selection = "None"
                                    assigned_games = ref.get_assigned_games()
                                    for game in games_at_time:
                                        if game.get_number() in assigned_games:
                                            current_selection = f"Game #{game.get_number()}"
                                            break
                                    
                                    try:
                                        current_index = game_options.index(current_selection)
                                    except ValueError:
                                        current_index = 0
                                    
                                    selected = st.selectbox(
                                        f"{time}",
                                        game_options,
                                        index=current_index,
                                        key=f"assign_{ref_name}_{day}_{time}_{ref_idx}",
                                        label_visibility="visible"
                                    )
                                    
                                    # Update ref assignments based on selection
                                    if selected != "None":
                                        game_num = int(selected.split("#")[1].split()[0])
                                        ref.add_assigned_game(game_num)
                                    else:
                                        # Remove any games at this time from assignments
                                        for game in games_at_time:
                                            ref.remove_assigned_game(game.get_number())
                                else:
                                    # Show time slot but indicate not available
                                    st.markdown(f'<small style="color: #888888;">~~{time}~~ (N/A)</small>', unsafe_allow_html=True)
                            else:
                                # Show time slot but indicate no games
                                st.markdown(f'<small style="color: #888888;">~~{time}~~ (No games)</small>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Hour limit column with border
                with cols[-1]:
                    st.markdown('<div class="grid-cell">', unsafe_allow_html=True)
                    hour_limit = st.number_input(
                        "Max Hours",
                        min_value=0,
                        max_value=50,
                        value=ref.get_max_hours(),
                        key=f"hour_limit_{ref_name}_{ref_idx}",
                        label_visibility="visible"
                    )
                    ref.set_max_hours(hour_limit)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No referees found. Please add referees first.")
    else:
        st.info("No games found. Please create games first.")

with workflow_tab2:
    st.markdown("### ⚙️ Optimization Parameters")
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
        
        max_hours_week = st.number_input(
            "Max Hours per Week",
            min_value=1,
            max_value=50,
            value=st.session_state['schedule_params']['max_hours_per_week'],
            help="Maximum hours any referee can work in a week"
        )
        st.session_state['schedule_params']['max_hours_per_week'] = max_hours_week
        
        max_hours_day = st.number_input(
            "Max Hours per Day",
            min_value=1,
            max_value=24,
            value=st.session_state['schedule_params']['max_hours_per_day'],
            help="Maximum hours any referee can work in a single day"
        )
        st.session_state['schedule_params']['max_hours_per_day'] = max_hours_day
    
    with col2:
        st.markdown("#### Optimization Weights")
        st.markdown("**Scale: 0-10** (0=disable, 2.5=baseline, 10=max emphasis)")
        st.markdown("*Start with 2.5 for balanced objectives*")
        
        weight_hour_balancing = st.slider(
            "Hour Balancing",
            min_value=0.0,
            max_value=10.0,
            value=st.session_state['schedule_params']['weight_hour_balancing'],
            step=0.2,
            help="Importance of balancing hours across referees (0=disable, 2.5=baseline, 10=max emphasis)"
        )
        st.session_state['schedule_params']['weight_hour_balancing'] = weight_hour_balancing
        
        weight_skill_combo = st.slider(
            "High-Low Skill Combination",
            min_value=0.0,
            max_value=10.0,
            value=st.session_state['schedule_params']['weight_skill_combo'],
            step=0.2,
            help="Importance of pairing high and low skill referees (0=disable, 2.5=baseline, 10=max emphasis)"
        )
        st.session_state['schedule_params']['weight_skill_combo'] = weight_skill_combo
        
        weight_low_skill_penalty = st.slider(
            "Low Skill on High Games Penalty",
            min_value=0.0,
            max_value=10.0,
            value=st.session_state['schedule_params']['weight_low_skill_penalty'],
            step=0.2,
            help="Penalty for assigning low skill refs to high difficulty games (0=disable, 2.5=baseline, 10=max emphasis)"
        )
        st.session_state['schedule_params']['weight_low_skill_penalty'] = weight_low_skill_penalty
        
        weight_shift_block_penalty = st.slider(
            "Shift Block Penalty",
            min_value=0.0,
            max_value=10.0,
            value=st.session_state['schedule_params']['weight_shift_block_penalty'],
            step=0.2,
            help="Penalty for assigning too many consecutive shifts (0=disable, 2.5=baseline, 10=max emphasis)"
        )
        st.session_state['schedule_params']['weight_shift_block_penalty'] = weight_shift_block_penalty
        
        weight_effort_bonus = st.slider(
            "High Effort Bonus",
            min_value=0.0,
            max_value=10.0,
            value=st.session_state['schedule_params']['weight_effort_bonus'],
            step=0.2,
            help="Bonus for giving more hours to high effort referees (0=disable, 2.5=baseline, 10=max emphasis)"
        )
        st.session_state['schedule_params']['weight_effort_bonus'] = weight_effort_bonus

with workflow_tab3:
    st.markdown("### 📋 Configuration Review")
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
    
    if st.button("🔄 Optimize Schedule", type="primary", width='stretch'):
        if 'referees' in st.session_state and 'games' in st.session_state:
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
                
                # Run optimization
                with st.spinner("Running optimization..."):
                    result = scheduler.optimize()
                
                if isinstance(result, dict) and result.get('success'):
                    # Update session state with optimized results
                    st.session_state['referees'] = result['refs']  # Updated referee objects with assignments
                    st.session_state['optimization_complete'] = True
                    st.session_state['optimization_assignments'] = result['assignments']
                    
                    st.success("✅ Optimization completed successfully!")
                    st.info("📊 Navigate to the 'Results & Export' tab to view the schedule and export to Excel.")
                    st.rerun()  # Refresh to show new results
                else:
                    error_msg = result.get('error', 'Unknown error') if isinstance(result, dict) else 'Optimization failed'
                    st.error(f"❌ Optimization failed: {error_msg}")
                    st.info("💡 Check the console/terminal for detailed debug output.")
            except Exception as e:
                st.error(f"❌ Error during optimization: {str(e)}")
        else:
            st.error("❌ Please ensure both referees and games are loaded before optimizing.")

with workflow_tab4:
    st.markdown("### 📊 Results & Export")
    
    # Check if optimization has been completed
    if st.session_state.get('optimization_complete', False):
        st.success("✅ Optimization completed! Results are ready for review.")
        
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
        st.markdown("### 📤 Export Schedule")
        st.markdown("Export your optimized schedule to Excel format for sharing and printing.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Export to Excel", type="primary", width='stretch'):
                try:
                    # Generate Excel file
                    output_path = generate_schedule_from_session_state(st.session_state)
                    
                    # Read the file for download
                    with open(output_path, 'rb') as file:
                        excel_data = file.read()
                    
                    # Provide download button
                    st.download_button(
                        label="💾 Download Schedule.xlsx",
                        data=excel_data,
                        file_name="referee_schedule.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    st.success("✅ Excel file generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating Excel file: {str(e)}")
        
        with col2:
            if st.button("🔄 Re-run Optimization", width='stretch'):
                # Clear optimization results to allow re-running
                st.session_state['optimization_complete'] = False
                if 'optimization_assignments' in st.session_state:
                    del st.session_state['optimization_assignments']
                st.info("💡 Navigate back to 'Step 3: Review' to re-run the optimization.")
                st.rerun()
        
        # Show raw assignment data if needed (for debugging)
        if st.checkbox("🔍 Show Raw Assignment Data", help="Display the raw optimization results for debugging"):
            if 'optimization_assignments' in st.session_state:
                assignments = st.session_state['optimization_assignments']
                st.markdown("#### Raw Assignment Data")
                st.json(assignments)
            else:
                st.info("No raw assignment data available.")
    
    else:
        st.info("🔄 No optimization results yet. Complete the optimization in 'Step 3: Review' to see results here.")
        
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
            st.markdown("#### 📋 Current Manual Assignments")
            manual_df = pd.DataFrame(manual_assignments)
            st.dataframe(manual_df, width='stretch', hide_index=True)
        else:
            st.markdown("#### 📋 Current Manual Assignments")
            st.info("No manual assignments made yet.")

st.markdown("---")
st.subheader("📊 Data Summary")

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
