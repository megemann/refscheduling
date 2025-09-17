import streamlit as st
import pandas as pd
import sys
import os

# Add the parent directory to the path to import from phase1
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Set page config
st.set_page_config(
    page_title="Overview - Referee Scheduling",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add CSS for optimized layout and compact navigation
st.markdown("""
<style>
.main > div {
    max-width: 95% !important;
}
.block-container {
    max-width: 95% !important;
    padding-top: 1rem !important;
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

# Title and description
st.title("Referee Scheduling System - Overview")
st.markdown("### Automated referee scheduling with optimization")


# Master Excel Upload - available at the beginning
st.markdown("---")
st.subheader("Quick Start: Upload Complete Dataset")
st.markdown("Have a complete dataset? Upload your master Excel file to get started instantly.")

uploaded_master_file = st.file_uploader(
    "Choose Master Excel file (with Referees and Games sheets)",
    type=['xlsx', 'xls'],
    help="Upload a master file with both Referees and Games sheets to import everything at once",
    key="master_upload_quick"
)

if uploaded_master_file is not None:
    try:
        import pandas as pd
        # Read both sheets
        excel_file = pd.ExcelFile(uploaded_master_file)
        
        if 'Referees' in excel_file.sheet_names and 'Games' in excel_file.sheet_names:
            refs_df = pd.read_excel(uploaded_master_file, sheet_name='Referees')
            games_df = pd.read_excel(uploaded_master_file, sheet_name='Games')
            
            st.success(f"Found {len(refs_df)} referees and {len(games_df)} games")
            
            col_ref, col_game = st.columns(2)
            with col_ref:
                st.write("**Referees Preview:**")
                st.dataframe(refs_df.head(3), width='stretch')
            with col_game:
                st.write("**Games Preview:**")
                st.dataframe(games_df.head(3), width='stretch')
            
            if st.button("Import Complete Dataset", width='stretch', type="primary", key="quick_import"):
                # Import referees
                from phase2.Ref import Ref
                new_referees = []
                time_columns = [col for col in refs_df.columns 
                              if col not in ['Referee_Name', 'Email', 'Phone', 'Experience', 'Effort']]
                
                for _, row in refs_df.iterrows():
                    availability = []
                    for col in time_columns:
                        if col in refs_df.columns:
                            availability.append(int(row[col]) if pd.notna(row[col]) else 0)
                        else:
                            availability.append(0)
                    
                    new_ref = Ref(
                        name=str(row['Referee_Name']),
                        availability=availability,
                        email=str(row['Email']) if pd.notna(row['Email']) else '',
                        phone_number=str(row['Phone']) if pd.notna(row['Phone']) and 'Phone' in refs_df.columns else '',
                        experience=int(row['Experience']) if pd.notna(row['Experience']) else 3
                    )
                    
                    if hasattr(new_ref, 'set_effort') and 'Effort' in refs_df.columns:
                        try:
                            new_ref.set_effort(int(row['Effort']) if pd.notna(row['Effort']) else 3)
                        except:
                            pass
                    
                    new_referees.append(new_ref)
                
                # Import games
                from phase2.Game import Game
                new_games = []
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
                    new_games.append(new_game)
                
                # Clear existing data and update session state
                st.session_state['referees'] = new_referees
                st.session_state['time_columns'] = time_columns
                st.session_state['games'] = new_games
                # Reset unsaved changes flags since we're importing fresh data
                st.session_state['unsaved_ref_changes'] = False
                st.session_state['unsaved_game_changes'] = False
                
                # Also create the availability CSV for backwards compatibility
                ref_matrix = {}
                for ref in new_referees:
                    ref_name = ref.get_name().replace(' ', '_').replace(',', '').replace('.', '').replace('(', '').replace(')', '')
                    if hasattr(ref, 'get_availability'):
                        ref_matrix[ref_name] = ref.get_availability()
                
                if ref_matrix:
                    availability_df = pd.DataFrame.from_dict(ref_matrix, orient='index', columns=time_columns)
                    availability_df.to_csv('DATA/Convert.csv')
                
                st.success(f"Imported {len(new_referees)} referees and {len(new_games)} games successfully!")
                st.rerun()
                
        else:
            st.error("Excel file must contain both 'Referees' and 'Games' sheets")
            
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")

# Check if availability data exists
try:
    import pandas as pd
    availability_df = pd.read_csv('DATA/Convert.csv', index_col=0)
    has_availability_data = len(availability_df) > 0
except:
    has_availability_data = False

# Check for games and referees in session state
has_games = 'games' in st.session_state and len(st.session_state.get('games', [])) > 0
has_referees = 'referees' in st.session_state and len(st.session_state.get('referees', [])) > 0
optimization_complete = st.session_state.get('optimization_complete', False)

# Show workflow progress
st.markdown("---")
st.subheader("⚡ Workflow Progress")

# Calculate progress
total_steps = 4
steps_completed = 0
current_step_name = ""

if has_availability_data:
    steps_completed = 1
    current_step_name = "Availability Setup Complete"
    
    if has_games:
        steps_completed = 2
        current_step_name = "Games Created"
        
        if has_referees:
            steps_completed = 3
            current_step_name = "Referees Loaded"
            
            if optimization_complete:
                steps_completed = 4
                current_step_name = "Optimization Complete"
            else:
                current_step_name = "Ready for Scheduling"
        else:
            current_step_name = "Need Referee Details"
    else:
        current_step_name = "Need Games"
else:
    current_step_name = "Need Availability Data"

# Calculate percentage
progress_percent = (steps_completed / total_steps) * 100

# Display progress bar
col1, col2 = st.columns([3, 1])
with col1:
    st.progress(progress_percent / 100, text=f"{current_step_name}")
with col2:
    st.metric("Progress", f"{steps_completed}/{total_steps} ({progress_percent:.0f}%)")

# Show optimization results if complete
if optimization_complete and has_referees and has_games:
    st.success("**Optimization Complete!** Your schedule is ready.")
    
    total_assignments = sum(len(ref.get_optimized_games()) for ref in st.session_state['referees'])
    assigned_refs = len([ref for ref in st.session_state['referees'] if ref.get_optimized_games()])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Assignments", total_assignments)
    with col2:
        st.metric("Assigned Referees", assigned_refs)
    with col3:
        if assigned_refs > 0:
            avg_games = total_assignments / assigned_refs
            st.metric("Avg Games/Ref", f"{avg_games:.1f}")
        else:
            st.metric("Avg Games/Ref", "0")
    with col4:
        if st.button("📈 View Full Schedule", type="primary"):
            st.switch_page("pages/05_Schedule_Management.py")

# Master Excel Download - only show when both refs and games exist
if has_availability_data and has_games and has_referees:
    st.markdown("---")
    st.subheader("Export Complete Dataset")
    st.markdown("Download your complete dataset for backup or sharing.")
    
    import pandas as pd
    import io
    
    # Create master Excel with both referees and games
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        
        # Sheet 1: Referees
        if st.session_state.get('referees'):
            ref_data = []
            time_columns = st.session_state.get('time_columns', [])
            
            for ref in st.session_state['referees']:
                ref_row = {
                    'Referee_Name': ref.get_name() if hasattr(ref, 'get_name') else str(ref),
                    'Email': ref.get_email() if hasattr(ref, 'get_email') else '',
                    'Phone': ref.get_phone_number() if hasattr(ref, 'get_phone_number') else '',
                    'Experience': ref.get_experience() if hasattr(ref, 'get_experience') else 3,
                    'Effort': ref.get_effort() if hasattr(ref, 'get_effort') else 3
                }
                
                # Add availability data
                if hasattr(ref, 'get_availability'):
                    availability = ref.get_availability()
                    for i, col in enumerate(time_columns):
                        if i < len(availability):
                            ref_row[col] = availability[i]
                        else:
                            ref_row[col] = 0
                
                ref_data.append(ref_row)
            
            ref_df = pd.DataFrame(ref_data)
            ref_df.to_excel(writer, sheet_name='Referees', index=False)
        
        # Sheet 2: Games
        if st.session_state.get('games'):
            game_data = []
            for game in st.session_state['games']:
                game_data.append({
                    'Game_Number': game.get_number(),
                    'Date': game.get_date(),
                    'Time': game.get_time(),
                    'Location': game.get_location(),
                    'Difficulty': game.get_difficulty(),
                    'Min_Refs': game.get_min_refs(),
                    'Max_Refs': game.get_max_refs()
                })
            
            game_df = pd.DataFrame(game_data)
            game_df.to_excel(writer, sheet_name='Games', index=False)
    
    st.download_button(
        label="Download Master Excel",
        data=output.getvalue(),
        file_name="master_schedule_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width='stretch',
        type="primary"
    )

st.markdown("---")
st.markdown("*Use the sidebar to navigate between different sections*")
