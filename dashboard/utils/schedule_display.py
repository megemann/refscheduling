import streamlit as st
import pandas as pd
from datetime import datetime

def display_optimized_schedule(refs, games):
    """
    Display the optimized schedule in a user-friendly format organized by referee.
    
    Args:
        refs: List of Ref objects with optimized assignments
        games: List of Game objects
    """
    st.markdown("### 📅 Optimized Schedule by Referee")
    
    # Check if we have any optimized assignments
    has_optimized = any(ref.get_optimized_games() for ref in refs)
    
    if not has_optimized:
        st.info("ℹ️ No optimized assignments found. Please run the optimization first.")
        return
    
    # Helper function to sort times
    def parse_time_safely(time_str):
        """Parse time string handling various formats"""
        try:
            if 'AM' in time_str.upper() or 'PM' in time_str.upper():
                return datetime.strptime(time_str.upper(), "%I:%M %p").time()
            else:
                if ':' in time_str:
                    return datetime.strptime(time_str, "%H:%M").time()
                else:
                    return datetime.strptime(f"{time_str}:00", "%H:%M").time()
        except:
            return datetime.strptime("12:00", "%H:%M").time()
    
    # Create summary statistics
    st.markdown("#### 📊 Schedule Summary")
    
    total_assignments = sum(len(ref.get_optimized_games()) for ref in refs)
    assigned_refs = len([ref for ref in refs if ref.get_optimized_games()])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Assignments", total_assignments)
    with col2:
        st.metric("Assigned Referees", assigned_refs)
    with col3:
        st.metric("Total Referees", len(refs))
    with col4:
        if assigned_refs > 0:
            avg_games = total_assignments / assigned_refs
            st.metric("Avg Games/Ref", f"{avg_games:.1f}")
        else:
            st.metric("Avg Games/Ref", "0")
    
    # Group assignments by day for better organization
    assignments_by_day = {}
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for ref in refs:
        optimized_games = ref.get_optimized_games()
        if optimized_games:
            for game in optimized_games:
                day = game.get_date()
                if day not in assignments_by_day:
                    assignments_by_day[day] = []
                assignments_by_day[day].append({
                    'ref_name': ref.get_name(),
                    'game_number': game.get_number(),
                    'time': game.get_time(),
                    'location': game.get_location(),
                    'difficulty': game.get_difficulty()
                })
    
    # Sort days
    sorted_days = sorted(assignments_by_day.keys(), 
                        key=lambda x: day_order.index(x) if x in day_order else 999)
    
    # Display schedule by day in tabs
    if sorted_days:
        st.markdown("#### 📅 Schedule by Day")
        day_tabs = st.tabs(sorted_days)
        
        for i, day in enumerate(sorted_days):
            with day_tabs[i]:
                day_assignments = assignments_by_day[day]
                
                # Sort by time
                day_assignments.sort(key=lambda x: parse_time_safely(x['time']))
                
                # Create a DataFrame for better display
                df = pd.DataFrame(day_assignments)
                df = df.rename(columns={
                    'ref_name': 'Referee',
                    'game_number': 'Game #',
                    'time': 'Time',
                    'location': 'Location',
                    'difficulty': 'Difficulty'
                })
                
                # Display the table
                st.dataframe(df, width='stretch', hide_index=True)
                
                # Show summary for this day
                unique_refs = len(set(assignment['ref_name'] for assignment in day_assignments))
                st.caption(f"📊 {len(day_assignments)} games assigned to {unique_refs} referees")
    
    # Display individual referee schedules
    st.markdown("#### 👤 Individual Referee Schedules")
    
    # Create expandable sections for each referee
    refs_with_assignments = [ref for ref in refs if ref.get_optimized_games()]
    refs_without_assignments = [ref for ref in refs if not ref.get_optimized_games()]
    
    # Sort refs alphabetically
    refs_with_assignments.sort(key=lambda x: x.get_name())
    refs_without_assignments.sort(key=lambda x: x.get_name())
    
    # Show referees with assignments first
    for ref in refs_with_assignments:
        optimized_games = ref.get_optimized_games()
        
        with st.expander(f"🟢 {ref.get_name()} ({len(optimized_games)} games)"):
            # Sort games by day and time
            sorted_games = sorted(optimized_games, 
                                key=lambda g: (day_order.index(g.get_date()) if g.get_date() in day_order else 999,
                                             parse_time_safely(g.get_time())))
            
            game_data = []
            for game in sorted_games:
                game_data.append({
                    'Game #': game.get_number(),
                    'Day': game.get_date(),
                    'Time': game.get_time(),
                    'Location': game.get_location(),
                    'Difficulty': game.get_difficulty()
                })
            
            if game_data:
                game_df = pd.DataFrame(game_data)
                st.dataframe(game_df, width='stretch', hide_index=True)
                
                # Show referee stats
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"📧 Email: {ref.get_email()}")
                    st.caption(f"📱 Phone: {ref.get_phone_number()}")
                with col2:
                    st.caption(f"⭐ Experience: {ref.get_experience()}/5")
                    st.caption(f"💪 Effort: {ref.get_effort()}/5")
    
    # Show referees without assignments
    if refs_without_assignments:
        st.markdown("#### ⚪ Referees with No Assignments")
        for ref in refs_without_assignments:
            with st.expander(f"⚪ {ref.get_name()} (0 games)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"📧 Email: {ref.get_email()}")
                    st.caption(f"📱 Phone: {ref.get_phone_number()}")
                with col2:
                    st.caption(f"⭐ Experience: {ref.get_experience()}/5")
                    st.caption(f"💪 Effort: {ref.get_effort()}/5")
                
                st.info("💡 This referee was not assigned any games in the optimization. This could be due to availability constraints, hour limits, or optimization parameters.")


def display_game_coverage(games):
    """
    Display game coverage statistics showing which games are properly staffed.
    
    Args:
        games: List of Game objects
    """
    st.markdown("### 🎯 Game Coverage Analysis")
    
    # Analyze game coverage
    fully_staffed = []
    understaffed = []
    overstaffed = []
    
    for game in games:
        refs = game.get_refs()
        min_refs = game.get_min_refs()
        max_refs = game.get_max_refs()
        
        if len(refs) < min_refs:
            understaffed.append(game)
        elif len(refs) > max_refs:
            overstaffed.append(game)
        else:
            fully_staffed.append(game)
    
    # Show summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Games", len(games))
    with col2:
        st.metric("✅ Fully Staffed", len(fully_staffed))
    with col3:
        st.metric("⚠️ Understaffed", len(understaffed))
    with col4:
        st.metric("🔄 Overstaffed", len(overstaffed))
    
    # Show detailed coverage if there are issues
    if understaffed or overstaffed:
        st.markdown("#### ⚠️ Games Requiring Attention")
        
        if understaffed:
            st.markdown("**🔴 Understaffed Games:**")
            for game in understaffed:
                refs = game.get_refs()
                ref_names = [ref.get_name() for ref in refs] if refs else ["No referees assigned"]
                st.error(f"Game #{game.get_number()}: {game.get_date()} {game.get_time()} - "
                        f"Only {len(refs)}/{game.get_min_refs()} refs assigned. "
                        f"Refs: {', '.join(ref_names)}")
        
        if overstaffed:
            st.markdown("**🟡 Overstaffed Games:**")
            for game in overstaffed:
                refs = game.get_refs()
                ref_names = [ref.get_name() for ref in refs]
                st.warning(f"Game #{game.get_number()}: {game.get_date()} {game.get_time()} - "
                          f"{len(refs)}/{game.get_max_refs()} refs assigned (over limit). "
                          f"Refs: {', '.join(ref_names)}")
    else:
        st.success("🎉 All games are properly staffed!")


def create_schedule_export_data(refs, games):
    """
    Create data structure for schedule export.
    
    Args:
        refs: List of Ref objects with optimized assignments
        games: List of Game objects
        
    Returns:
        Dictionary containing export data
    """
    export_data = {
        'by_referee': [],
        'by_game': [],
        'summary': {}
    }
    
    # Collect data by referee
    for ref in refs:
        optimized_games = ref.get_optimized_games()
        ref_data = {
            'name': ref.get_name(),
            'email': ref.get_email(),
            'phone': ref.get_phone_number(),
            'experience': ref.get_experience(),
            'effort': ref.get_effort(),
            'games': []
        }
        
        for game in optimized_games:
            ref_data['games'].append({
                'game_number': game.get_number(),
                'day': game.get_date(),
                'time': game.get_time(),
                'location': game.get_location(),
                'difficulty': game.get_difficulty()
            })
        
        export_data['by_referee'].append(ref_data)
    
    # Collect data by game
    for game in games:
        refs = game.get_refs()
        game_data = {
            'game_number': game.get_number(),
            'day': game.get_date(),
            'time': game.get_time(),
            'location': game.get_location(),
            'difficulty': game.get_difficulty(),
            'min_refs': game.get_min_refs(),
            'max_refs': game.get_max_refs(),
            'assigned_refs': [ref.get_name() for ref in refs],
            'ref_count': len(refs)
        }
        export_data['by_game'].append(game_data)
    
    # Create summary
    total_assignments = sum(len(ref_data['games']) for ref_data in export_data['by_referee'])
    assigned_refs = len([ref_data for ref_data in export_data['by_referee'] if ref_data['games']])
    
    export_data['summary'] = {
        'total_games': len(games),
        'total_referees': len(refs),
        'total_assignments': total_assignments,
        'assigned_referees': assigned_refs,
        'avg_games_per_ref': total_assignments / assigned_refs if assigned_refs > 0 else 0
    }
    
    return export_data
