import streamlit as st
import pandas as pd
import sys
import os


# Add the parent directory to the path to import from phase1
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import utility functions
from dashboard.utils.file_processor import load_availability_data
from phase2.Ref import Ref

# Set page config
st.set_page_config(
    page_title="Referee Management",
    page_icon="👥",
    layout="centered"
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

st.title("👥 Referee Management")
st.markdown("Manage referee profiles, skills, and preferences")

# Referee Data Management Tabs
tab1, tab2, tab3 = st.tabs(["👥 Current Referees", "📊 Excel Import/Export", "➕ Add Referee"])

with tab2:
    st.markdown("#### 📊 Excel Import/Export")
    st.write("Download a template, upload referee data, or export current referee information.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 📥 Download Template")
        if st.button("📥 Download Referee Template", width='stretch'):
            import io
            
            # Create sample referee data template
            sample_data = {
                'Referee_Name': ['John Smith', 'Jane Doe', 'Mike Johnson'],
                'Email': ['john.smith@email.com', 'jane.doe@email.com', 'mike.johnson@email.com'],
                'Phone': ['(555) 123-4567', '(555) 987-6543', '(555) 456-7890'],
                'Experience': [3, 5, 2],
                'Effort': [4, 5, 3],
                'Monday_6:30 PM': [1, 0, 1],
                'Monday_7:30 PM': [1, 1, 0],
                'Tuesday_6:30 PM': [0, 1, 1],
                'Tuesday_7:30 PM': [1, 1, 1],
                'Wednesday_6:30 PM': [1, 0, 0],
                'Wednesday_7:30 PM': [0, 1, 1]
            }
            
            template_df = pd.DataFrame(sample_data)
            
            # Create download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                template_df.to_excel(writer, sheet_name='Referees', index=False)
            
            st.download_button(
                label="📥 Download Template",
                data=output.getvalue(),
                file_name="referee_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col2:
        st.markdown("##### 📤 Export Current Data")
        if 'referees' in st.session_state and st.session_state['referees']:
            if st.button("📤 Export Current Referees", width='stretch'):
                import io
                
                # Create referee data for export
                export_data = []
                time_columns = st.session_state.get('time_columns', [])
                
                for ref in st.session_state['referees']:
                    ref_data = {
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
                                ref_data[col] = availability[i]
                            else:
                                ref_data[col] = 0
                    
                    export_data.append(ref_data)
                
                export_df = pd.DataFrame(export_data)
                
                # Create download
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    export_df.to_excel(writer, sheet_name='Referees', index=False)
                
                st.download_button(
                    label="📤 Download Current Data",
                    data=output.getvalue(),
                    file_name="current_referees.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_current_refs"
                )
        else:
            st.info("No referee data to export")
    
    st.markdown("---")
    st.markdown("##### 📂 Upload Referee Data")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose Excel file",
        type=['xlsx', 'xls'],
        help="Upload a completed referee template or existing referee data"
    )
    
    if uploaded_file is not None:
        try:
            refs_df = pd.read_excel(uploaded_file)
            st.success(f"✅ Loaded {len(refs_df)} referees from Excel")
            st.dataframe(refs_df, width='stretch')
            
            if st.button("➕ Import Referees", width='stretch', type="primary"):
                imported_count = 0
                new_referees = []
                
                # Get time columns (availability columns)
                time_columns = [col for col in refs_df.columns 
                              if col not in ['Referee_Name', 'Email', 'Phone', 'Experience', 'Effort']]
                
                for _, row in refs_df.iterrows():
                    # Get availability data
                    availability = []
                    for col in time_columns:
                        if col in refs_df.columns:
                            availability.append(int(row[col]) if pd.notna(row[col]) else 0)
                        else:
                            availability.append(0)
                    
                    # Create new referee
                    new_ref = Ref(
                        name=str(row['Referee_Name']),
                        availability=availability,
                        email=str(row['Email']) if pd.notna(row['Email']) else '',
                        phone_number=str(row['Phone']) if pd.notna(row['Phone']) and 'Phone' in refs_df.columns else '',
                        experience=int(row['Experience']) if pd.notna(row['Experience']) else 3
                    )
                    
                    # Set effort if available
                    if hasattr(new_ref, 'set_effort') and 'Effort' in refs_df.columns:
                        try:
                            new_ref.set_effort(int(row['Effort']) if pd.notna(row['Effort']) else 3)
                        except:
                            pass
                    
                    new_referees.append(new_ref)
                    imported_count += 1
                
                # Store in session state
                st.session_state['referees'] = new_referees
                st.session_state['time_columns'] = time_columns
                
                st.success(f"✅ Imported {imported_count} referees successfully!")
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error reading Excel file: {e}")
    
    st.info("💡 **Tip:** Download the template first, fill it out with referee details and availability (1=available, 0=not available), then upload it here.")

with tab3:
    st.markdown("#### ➕ Add New Referee")
    st.write("Manually add a single referee with availability information.")
    
    with st.form("add_referee_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            ref_name = st.text_input("Referee Name", placeholder="Enter full name")
            ref_email = st.text_input("Email", placeholder="referee@email.com")
            ref_phone = st.text_input("Phone", placeholder="(555) 123-4567")
        
        with col2:
            ref_experience = st.number_input("Experience (1-5)", min_value=1, max_value=5, value=3)
            ref_effort = st.number_input("Effort (1-5)", min_value=1, max_value=5, value=3)
        
        st.markdown("##### Availability")
        st.write("Select time slots when this referee is available:")
        
        # Get time columns from existing data or create default ones
        time_columns = st.session_state.get('time_columns', [
            'Monday_6:30 PM', 'Monday_7:30 PM', 'Tuesday_6:30 PM', 'Tuesday_7:30 PM',
            'Wednesday_6:30 PM', 'Wednesday_7:30 PM', 'Thursday_6:30 PM', 'Thursday_7:30 PM'
        ])
        
        availability = []
        cols_per_row = 3
        for i in range(0, len(time_columns), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(time_columns):
                    time_slot = time_columns[i + j]
                    with col:
                        available = st.checkbox(time_slot.replace('_', ' '), key=f"avail_{i+j}")
                        availability.append(1 if available else 0)
        
        if st.form_submit_button("➕ Add Referee", width='stretch'):
            if ref_name:
                new_ref = Ref(
                    name=ref_name,
                    availability=availability,
                    email=ref_email,
                    phone_number=ref_phone,
                    experience=ref_experience
                )
                
                # Set effort
                if hasattr(new_ref, 'set_effort'):
                    try:
                        new_ref.set_effort(ref_effort)
                    except:
                        pass
                
                # Add to session state
                if 'referees' not in st.session_state:
                    st.session_state['referees'] = []
                if 'time_columns' not in st.session_state:
                    st.session_state['time_columns'] = time_columns
                
                st.session_state['referees'].append(new_ref)
                st.success(f"✅ Added referee: {ref_name}")
                st.rerun()
            else:
                st.error("❌ Please enter a referee name")

with tab1:
    st.markdown("#### 👥 Current Referees")

    # Auto-load referee data if availability exists but referees don't
    if ('referees' not in st.session_state or not st.session_state['referees']):
        try:
            availability_df, has_data = load_availability_data()
            if has_data:
                st.info("🔄 Loading referee data from availability file...")
                referees = []
                time_columns = list(availability_df.columns)
                
                for ref_name in availability_df.index:
                    availability = availability_df.loc[ref_name].tolist()
                    # Create Ref with minimal info (name from index, availability from matrix)
                    ref_obj = Ref(ref_name.replace('_', ' '), availability, "", "")
                    referees.append(ref_obj)
                
                # Store in session state
                st.session_state['referees'] = referees
                st.session_state['time_columns'] = time_columns
                st.success(f"✅ Loaded {len(referees)} referees!")
                st.rerun()
        except Exception as e:
            st.warning(f"⚠️ Could not load referee data: {str(e)}")

    # Check if we have referee data in session state
    if 'referees' in st.session_state and st.session_state['referees']:
        referees = st.session_state['referees']
        time_columns = st.session_state.get('time_columns', [])
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Referees", len(referees))
        with col2:
            if time_columns:
                total_availability = sum(sum(ref.get_availability() if hasattr(ref, 'get_availability') else [0]) for ref in referees)
                st.metric("Total Availability", total_availability)
        with col3:
            avg_experience = sum(ref.get_experience() if hasattr(ref, 'get_experience') else 3 for ref in referees) / len(referees)
            st.metric("Avg Experience", f"{avg_experience:.1f}")
        
        st.markdown("---")
        st.markdown(f"##### 📋 Referee List ({len(referees)} total)")
        
        # Display each referee in markdown format
        for i, ref in enumerate(referees, 1):
            try:
                # Use a container for each referee for better layout
                with st.container():
                    cols = st.columns([2, 2, 2, 1, 1, 1])
                    with cols[0]:
                        name = ref.get_name() if hasattr(ref, 'get_name') else str(ref)
                        st.markdown(f"**{name}**")
                    with cols[1]:
                        email = ref.get_email() if hasattr(ref, 'get_email') else "No email"
                        st.markdown(f"📧 {email}")
                    with cols[2]:
                        phone = ref.get_phone_number() if hasattr(ref, 'get_phone_number') else "No phone"
                        st.markdown(f"📞 {phone}")
                    with cols[3]:
                        # Experience input (1-5 scale, default to current value if exists)
                        current_exp = 3
                        if hasattr(ref, 'get_experience'):
                            try:
                                current_exp = min(5, max(1, int(ref.get_experience() or 3)))
                            except:
                                current_exp = 3
                        
                        experience = st.number_input(
                            f"Experience (1-5)",
                            min_value=1, max_value=5,
                            value=current_exp,
                            key=f"exp_{i}",
                            help="1 = Beginner, 5 = Expert"
                        )
                        if hasattr(ref, 'set_experience'):
                            try:
                                ref.set_experience(experience)
                            except:
                                pass
                    with cols[4]:
                        # Effort input (1-5 scale, default to current value if exists)
                        current_effort = 3
                        if hasattr(ref, 'get_effort'):
                            try:
                                current_effort = min(5, max(1, int(ref.get_effort() or 3)))
                            except:
                                current_effort = 3
                        
                        effort = st.number_input(
                            f"Effort (1-5)",
                            min_value=1, max_value=5,
                            value=current_effort,
                            key=f"eff_{i}",
                            help="1 = Low effort, 5 = High effort"
                        )
                        if hasattr(ref, 'set_effort'):
                            try:
                                ref.set_effort(effort)
                            except:
                                pass
                    with cols[5]:
                        # Remove referee button
                        if st.button("➖", key=f"remove_{i}", help="Remove referee"):
                            # Remove referee from session state and rerun
                            st.session_state['referees'].pop(i-1)
                            st.rerun()
            except Exception as e:
                st.error(f"Error displaying referee {i}: {e}")

    else:
        st.info("📋 **No referee data found**")
        st.markdown("### To load referee data:")
        st.markdown("1. Go to **Availability Setup** and upload referee availability")
        st.markdown("2. Or use the **Excel Import/Export** tab to upload referee data")
        st.markdown("3. Or use the **Add Referee** tab to add referees manually")
        
        if st.button("⬅️ Go to Availability Setup", width='stretch'):
            st.switch_page("pages/Availability_Setup.py")

