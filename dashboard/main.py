import streamlit as st
import sys
import os

# Add the parent directory to the path to import from phase1
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Set page config
st.set_page_config(
    page_title="Referee Scheduling System",
    page_icon="🏀",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Add CSS for wider container
st.markdown("""
<style>
.main > div {
    max-width: 85% !important;
}
.block-container {
    max-width: 85% !important;
}
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🏀 Referee Scheduling System")
st.markdown("### Automated referee scheduling with optimization")

# Master Excel Upload - available at the beginning
st.markdown("---")
st.subheader("📂 Quick Start: Upload Complete Dataset")
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
            
            st.success(f"✅ Found {len(refs_df)} referees and {len(games_df)} games")
            
            col_ref, col_game = st.columns(2)
            with col_ref:
                st.write("**Referees Preview:**")
                st.dataframe(refs_df.head(3), width='stretch')
            with col_game:
                st.write("**Games Preview:**")
                st.dataframe(games_df.head(3), width='stretch')
            
            if st.button("➕ Import Complete Dataset", width='stretch', type="primary", key="quick_import"):
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
                
                # Update session state
                st.session_state['referees'] = new_referees
                st.session_state['time_columns'] = time_columns
                st.session_state['games'] = new_games
                
                # Also create the availability CSV for backwards compatibility
                ref_matrix = {}
                for ref in new_referees:
                    ref_name = ref.get_name().replace(' ', '_').replace(',', '').replace('.', '').replace('(', '').replace(')', '')
                    if hasattr(ref, 'get_availability'):
                        ref_matrix[ref_name] = ref.get_availability()
                
                if ref_matrix:
                    availability_df = pd.DataFrame.from_dict(ref_matrix, orient='index', columns=time_columns)
                    availability_df.to_csv('DATA/Convert.csv')
                
                st.success(f"✅ Imported {len(new_referees)} referees and {len(new_games)} games successfully!")
                st.rerun()
                
        else:
            st.error("❌ Excel file must contain both 'Referees' and 'Games' sheets")
            
    except Exception as e:
        st.error(f"❌ Error reading Excel file: {e}")

# Main navigation
st.markdown("---")
st.subheader("📋 Quick Start Guide")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Step 1: Availability Setup**
    - Download template
    - Fill referee availability
    - Upload completed file
    """)
    if st.button("🔗 Go to Availability Setup", width='stretch'):
        st.switch_page("pages/Availability_Setup.py")

with col2:
    st.markdown("""
    **Step 2: Game Management**
    - Create games
    - Manage referee details
    - Set game requirements
    """)
    if st.button("🔗 Go to Game Management", width='stretch'):
        st.switch_page("pages/Game_Management.py")

with col3:
    st.markdown("""
    **Step 3: Schedule Management**
    - View all games
    - View all referees
    - Manage assignments
    """)
    if st.button("🔗 Go to Schedule Management", width='stretch'):
        st.switch_page("pages/Schedule_Management.py")

st.markdown("---")

# System status
st.subheader("📈 System Status")

# Check if availability data exists
try:
    import pandas as pd
    availability_df = pd.read_csv('DATA/Convert.csv', index_col=0)
    has_availability_data = len(availability_df) > 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Referees", len(availability_df))
    with col2:
        st.metric("Time Slots", len(availability_df.columns))
    with col3:
        st.metric("Total Availability", availability_df.sum().sum())
    
    st.success("✅ Availability data loaded successfully!")
    
except:
    has_availability_data = False
    st.info("📋 No availability data found. Please start with Step 1: Availability Setup")

# Check for games and referees in session state
has_games = 'games' in st.session_state and len(st.session_state.get('games', [])) > 0
has_referees = 'referees' in st.session_state and len(st.session_state.get('referees', [])) > 0

# Show workflow progress
st.markdown("---")
st.subheader("🔄 Workflow Progress")

if has_availability_data:
    st.markdown("✅ **Step 1:** Availability data ready")
    if has_games:
        st.markdown("✅ **Step 2:** Games created")
        if has_referees:
            st.markdown("✅ **Step 3:** Referees loaded")
            st.markdown("🔄 **Step 4:** Ready for scheduling")
        else:
            st.markdown("🔄 **Step 3:** Load referee details")
    else:
        st.markdown("🔄 **Step 2:** Create games")
else:
    st.markdown("🔄 **Step 1:** Set up availability data")
    st.markdown("⏳ **Step 2:** Waiting for Step 1 completion")

# Master Excel Download - only show when both refs and games exist
if has_availability_data and has_games and has_referees:
    st.markdown("---")
    st.subheader("📥 Export Complete Dataset")
    st.markdown("Download your complete dataset for backup or sharing.")
    
    if st.button("📥 Download Master Excel", width='stretch', type="primary"):
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
            label="📥 Download Complete Dataset",
            data=output.getvalue(),
            file_name="master_schedule_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

st.markdown("---")
st.markdown("*Navigate using the sidebar to access specific features*")
