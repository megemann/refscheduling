import streamlit as st
import pandas as pd
import sys
import os

# Add the parent directory to the path to import from phase1
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import utility functions
from dashboard.utils.file_processor import load_availability_data

# Set page config
st.set_page_config(
    page_title="Game Management",
    page_icon="🎮",
    layout="centered"
)

st.title("🎮 Game Management")

# Load availability data
availability_df, has_availability_data = load_availability_data()

if not has_availability_data:
    st.error("🚫 **This step is locked**")
    st.markdown("**You must complete Step 1 first:**")
    st.markdown("1. ❌ Download template")
    st.markdown("2. ❌ Fill referee availability") 
    st.markdown("3. ❌ Upload completed file")
    st.markdown("4. 🔒 Create games")
    st.markdown("5. 🔒 Assign referees")
    st.markdown("6. 🔒 Export schedules")
    
    st.info("👈 Go back to **Step 1: Availability Setup** to get started")
    
    if st.button("⬅️ Go to Availability Setup", use_container_width=True):
        st.switch_page("pages/Availability_Setup.py")
    
else:
    st.success("✅ **Step 1 Complete!** Game management is now available.")
    st.markdown("**Completed Steps:**")
    st.markdown("1. ✅ Download template")
    st.markdown("2. ✅ Fill referee availability") 
    st.markdown("3. ✅ Upload completed file")
    
    # Show available data summary
    st.markdown("### 📊 Available Data Summary:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Referees", len(availability_df))
    with col2:
        st.metric("Time Slots", len(availability_df.columns))
    with col3:
        st.metric("Total Availability", availability_df.sum().sum())

    # Games per time slot input section
    st.markdown("---")
    st.subheader("🎯 Games per Time Slot")
    st.write("Enter the number of games needed for each time slot:")
    
    # Create time slot summary for games input
    time_slot_data = []
    for col in availability_df.columns:
        if '_' in col:
            try:
                day, time = col.split('_', 1)
                count = availability_df[col].sum()
                time_slot_data.append({
                    'Day': day,
                    'Time': time,
                    'Available_Refs': int(count),
                    'Column': col
                })
            except Exception as e:
                continue
    
    if time_slot_data:
        # Sort by day order then by time
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        time_slot_df = pd.DataFrame(time_slot_data)
        time_slot_df['day_sort'] = time_slot_df['Day'].apply(lambda x: day_order.index(x) if x in day_order else 999)
        time_slot_df = time_slot_df.sort_values(['day_sort', 'Time']).drop('day_sort', axis=1)
        
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
                    key=f"games_{row['Column']}",
                    label_visibility="collapsed"
                )
                games_data.append({
                    'Day': row['Day'],
                    'Time': row['Time'],
                    'Available_Refs': row['Available_Refs'],
                    'Games_Needed': num_games
                })
            prev_day = row['Day']
        
        # Show summary of games input
        games_with_refs = [g for g in games_data if g['Games_Needed'] > 0]
        if games_with_refs:
            st.markdown("---")
            st.subheader("📋 Games Summary")
            games_summary_df = pd.DataFrame(games_with_refs)
            st.dataframe(games_summary_df, width='stretch', hide_index=True)
            
            # Calculate total games and required refs
            total_games = sum(g['Games_Needed'] for g in games_with_refs)
            total_refs_needed = total_games * 3  # Assuming 3 refs per game
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Games", total_games)
            with col2:
                st.metric("Refs Needed", total_refs_needed)
            with col3:
                coverage = (total_refs_needed / availability_df.sum().sum() * 100) if availability_df.sum().sum() > 0 else 0
                st.metric("Coverage %", f"{coverage:.1f}%")
            
            # Check for potential issues
            issues = []
            for game in games_with_refs:
                refs_needed = game['Games_Needed'] * 3
                if refs_needed > game['Available_Refs']:
                    issues.append(f"{game['Day']} {game['Time']}: Need {refs_needed} refs, only {game['Available_Refs']} available")
            
            if issues:
                st.warning("⚠️ **Potential Scheduling Issues:**")
                for issue in issues:
                    st.write(f"• {issue}")
            else:
                st.success("✅ All time slots have sufficient referee coverage!")
            
            # Run scheduling button
            st.markdown("---")
            st.subheader("🚀 Run Scheduling Algorithm")
            
            col1, col2 = st.columns(2)
            with col1:
                algorithm_choice = st.selectbox(
                    "Choose Algorithm:",
                    ["Greedy (Fast)", "Optimization (Coming Soon)"],
                    help="Greedy algorithm provides quick results, optimization will be available in Phase 2"
                )
            
            with col2:
                refs_per_game = st.number_input(
                    "Referees per Game:",
                    min_value=1,
                    max_value=5,
                    value=3,
                    help="Number of referees to assign to each game"
                )
            
            if st.button("🎯 Run Scheduling Algorithm", use_container_width=True, type="primary"):
                if algorithm_choice == "Greedy (Fast)":
                    with st.spinner("Running greedy scheduling algorithm..."):
                        # Here you would integrate with your greedy algorithm
                        # For now, show a placeholder
                        st.success("✅ Scheduling completed!")
                        st.info("📋 Algorithm results would appear here")
                        st.markdown("**Next Steps:**")
                        st.markdown("- Review generated schedule")
                        st.markdown("- Make manual adjustments if needed")
                        st.markdown("- Export to Excel for use")
                        
                        # Placeholder for schedule display
                        st.markdown("---")
                        st.subheader("📊 Generated Schedule Preview")
                        st.info("Schedule results will be displayed here once the algorithm is integrated")
                else:
                    st.info("🚧 Optimization algorithm coming in Phase 2!")
            
            # Manual scheduling tools
            st.markdown("---")
            st.subheader("🛠️ Manual Scheduling Tools")
            st.markdown("*These features will be available in Phase 2:*")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**🎛️ Schedule Editor**")
                st.markdown("- Drag and drop referee assignments")
                st.markdown("- Real-time conflict detection")
                st.markdown("- Fairness score tracking")
                
            with col2:
                st.markdown("**📊 Analytics Dashboard**")
                st.markdown("- Referee workload distribution")
                st.markdown("- Coverage gap analysis")
                st.markdown("- Schedule quality metrics")
        
        else:
            st.info("📝 Set the number of games for each time slot above to proceed with scheduling.")
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Availability Setup", use_container_width=True):
            st.switch_page("pages/Availability_Setup.py")
    with col2:
        if st.button("🏠 Back to Main", use_container_width=True):
            st.switch_page("main.py")
