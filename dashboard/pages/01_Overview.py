import streamlit as st
import pandas as pd
import sys
import os
import io

# Add the parent directory to the path to import from phase1
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Set page config
st.set_page_config(
    page_title="Quick Start - Referee Scheduling",
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

/* Custom box styling */
.info-box {
    padding: 20px;
    border-radius: 10px;
    border: 2px solid rgba(255, 255, 255, 0.2);
    margin: 10px 0;
    background-color: rgba(255, 255, 255, 0.05);
}

.workflow-step {
    padding: 15px;
    border-left: 4px solid #4CAF50;
    margin: 10px 0;
    background-color: rgba(76, 175, 80, 0.1);
}
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("Quick Start")
st.markdown("### Get started with referee scheduling")


# Workflow Directions
st.markdown("---")
st.subheader("How It Works")
st.markdown("""
This system helps you create optimized referee schedules using a step-by-step workflow.
""")

workflow_directions = """
<div class="info-box">
<h4>Standard Workflow</h4>
<p><strong>For new projects or updating data:</strong></p>
<ol>
    <li><strong>Availability Setup:</strong> Upload referee availability data (Excel/CSV format)</li>
    <li><strong>Game Management:</strong> Upload your master game schedule or create games manually</li>
    <li><strong>Referee Management:</strong> Review referee info, edit availability, adjust experience/effort levels</li>
    <li><strong>Schedule Management:</strong> Run the optimizer and export your final schedule</li>
</ol>
<p><em>Use the sidebar navigation to access each section.</em></p>
</div>
"""
st.markdown(workflow_directions, unsafe_allow_html=True)

st.markdown("---")
st.subheader("Re-Import Previous Session")
st.markdown("If you have a master input file from a previous session, upload it here to restore your work.")

uploaded_master_file = st.file_uploader(
    "Upload Master Input File",
    type=['xlsx', 'xls'],
    help="Upload a master file with both 'Referees' and 'Games' sheets from a previous session",
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
                from phase3.Ref import Ref
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
                from phase3.Game import Game
                new_games = []
                for _, row in games_df.iterrows():
                    # Handle both old and new format
                    if 'Location_Descriptor' in games_df.columns and 'Location_Number' in games_df.columns:
                        location_descriptor = str(row['Location_Descriptor'])
                        location_number = int(row['Location_Number'])
                        location = f"{location_descriptor} {location_number}"
                    elif 'Location' in games_df.columns:
                        location = str(row['Location'])
                        location_descriptor = None
                        location_number = None
                    else:
                        location = "Court 1"
                        location_descriptor = None
                        location_number = None
                    
                    # Handle division fields
                    division_type = None
                    division_number = None
                    if 'Division_Type' in games_df.columns:
                        div_val = row.get('Division_Type', '')
                        division_type = str(div_val) if div_val and str(div_val) != '' and str(div_val) != 'nan' else None
                    if 'Division_Number' in games_df.columns:
                        div_num_val = row.get('Division_Number', '')
                        division_number = str(div_num_val) if div_num_val and str(div_num_val) != '' and str(div_num_val) != 'nan' else None
                    
                    new_game = Game(
                        date=str(row['Date']),
                        time=str(row['Time']),
                        number=int(row['Game_Number']),
                        difficulty=str(row['Difficulty']),
                        location=location,
                        min_refs=int(row['Min_Refs']),
                        max_refs=int(row['Max_Refs']),
                        location_descriptor=location_descriptor,
                        location_number=location_number,
                        division_type=division_type,
                        division_number=division_number
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
    availability_df = pd.read_csv('DATA/Convert.csv', index_col=0)
    has_availability_data = len(availability_df) > 0
except:
    has_availability_data = False

# Check for games and referees in session state
has_games = 'games' in st.session_state and len(st.session_state.get('games', [])) > 0
has_referees = 'referees' in st.session_state and len(st.session_state.get('referees', [])) > 0
optimization_complete = st.session_state.get('optimization_complete', False)

# Show optimization results if complete
if optimization_complete and has_referees and has_games:
    st.markdown("---")
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
        if st.button("View Full Schedule", type="primary"):
            st.switch_page("pages/05_Schedule_Management.py")

# Export current data - only show when both refs and games exist
if has_availability_data and has_games and has_referees:
    st.markdown("---")
    st.subheader("Export Master Input File")
    st.markdown("Download your current data as a master input file. Use this file to restore your session later or share your configuration.")
    
    # Create master Excel with both referees and games
    def create_export_file():
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
                        'Location_Descriptor': game.get_location_descriptor(),
                        'Location_Number': game.get_location_number(),
                        'Difficulty': game.get_difficulty(),
                        'Division_Type': game.get_division_type() or '',
                        'Division_Number': game.get_division_number() or '',
                        'Min_Refs': game.get_min_refs(),
                        'Max_Refs': game.get_max_refs()
                    })
                
                game_df = pd.DataFrame(game_data)
                game_df.to_excel(writer, sheet_name='Games', index=False)
        
        return output.getvalue()
    
    st.download_button(
        label="Download Master Input File",
        data=create_export_file(),
        file_name="master_input_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        type="primary"
    )
    st.info("This file contains all your referees, games, and configuration. Keep it safe for future sessions.")

st.markdown("---")
st.markdown("### Navigation")
st.markdown("""
- Use the **sidebar** to navigate between different sections
- Follow the workflow in order: Availability Setup > Game Management > Referee Management > Schedule Management
- Export your master input file regularly to save your progress
- To start a new session with existing data, re-import your master input file from the top of this page
""")
