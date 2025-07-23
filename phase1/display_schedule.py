from Ref import Ref
from Game import Game
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np

def display_by_ref(refs):
    """
    Display schedule with refs as rows and time slots as columns.
    Each cell shows if ref is assigned (1) or available but not assigned (0.5) or not available (0)
    """
    # Get all unique time slots from all refs
    all_time_slots = set()
    for ref in refs:
        all_time_slots.update(ref.availability.keys())
    
    # Sort time slots chronologically
    time_slots = sorted(list(all_time_slots), key=lambda x: sort_time_key(x))
    
    # Create data matrix
    ref_names = [ref.name for ref in refs]
    data = []
    
    for ref in refs:
        row = []
        for time_slot in time_slots:
            # Check if ref has a game at this time slot
            assigned_at_slot = any(game.get_time_slot() == time_slot for game in ref.games)
            
            if assigned_at_slot:
                row.append(1)  # Assigned
            elif ref.availability.get(time_slot, False):
                row.append(0.5)  # Available but not assigned
            else:
                row.append(0)  # Not available
        data.append(row)
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(len(time_slots) * 1.2, len(ref_names) * 0.8))
    
    # Create color map: 0=red (unavailable), 0.5=yellow (available), 1=green (assigned)
    colors = np.array(data)
    cmap = plt.cm.RdYlGn
    im = ax.imshow(colors, cmap=cmap, aspect='auto', vmin=0, vmax=1)
    
    # Set ticks and labels
    ax.set_xticks(range(len(time_slots)))
    ax.set_xticklabels(time_slots, rotation=45, ha='right')
    ax.set_yticks(range(len(ref_names)))
    ax.set_yticklabels(ref_names)
    
    # Add text annotations
    for i in range(len(ref_names)):
        for j in range(len(time_slots)):
            value = data[i][j]
            if value == 1:
                text = "ASSIGNED"
            elif value == 0.5:
                text = "Available"
            else:
                text = "N/A"
            ax.text(j, i, text, ha="center", va="center", fontsize=8, fontweight='bold')
    
    # Add legend
    assigned_patch = mpatches.Patch(color=cmap(1.0), label='Assigned')
    available_patch = mpatches.Patch(color=cmap(0.5), label='Available')
    unavailable_patch = mpatches.Patch(color=cmap(0.0), label='Unavailable')
    ax.legend(handles=[assigned_patch, available_patch, unavailable_patch], 
              bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.title("Referee Schedule - By Ref")
    plt.xlabel("Time Slots")
    plt.ylabel("Referees")
    plt.tight_layout()
    plt.show()

def display_by_game(games):
    """
    Display schedule with time slots as rows and assigned refs as columns.
    Shows which refs are assigned to each game time.
    """
    # Get all unique time slots and refs
    time_slots = list(set(game.get_time_slot() for game in games))
    time_slots = sorted(time_slots, key=lambda x: sort_time_key(x))
    
    # Group games by time slot and collect assigned refs
    games_by_time = {}
    max_refs_per_slot = 0
    
    for game in games:
        time_slot = game.get_time_slot()
        if time_slot not in games_by_time:
            games_by_time[time_slot] = []
        
        # Get ref names (refs are Ref objects with .name attribute)
        ref_names = [ref.name for ref in game.get_refs()]
        games_by_time[time_slot].extend(ref_names)
        max_refs_per_slot = max(max_refs_per_slot, len(games_by_time[time_slot]))
    
    # Create data for visualization
    data = []
    for time_slot in time_slots:
        refs_for_slot = games_by_time.get(time_slot, [])
        # Pad with empty strings to make all rows same length
        while len(refs_for_slot) < max_refs_per_slot:
            refs_for_slot.append("")
        data.append(refs_for_slot)
    
    # Create table visualization
    fig, ax = plt.subplots(figsize=(max_refs_per_slot * 2, len(time_slots) * 0.8))
    
    # Hide axes
    ax.axis('tight')
    ax.axis('off')
    
    # Create table
    table_data = []
    for i, time_slot in enumerate(time_slots):
        row = [time_slot] + data[i]
        table_data.append(row)
    
    # Column headers
    headers = ['Time Slot'] + [f'Ref {i+1}' for i in range(max_refs_per_slot)]
    
    table = ax.table(cellText=table_data, colLabels=headers, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Color code cells
    for i in range(len(time_slots)):
        for j in range(max_refs_per_slot + 1):
            if j == 0:  # Time slot column
                table[(i+1, j)].set_facecolor('#E6E6FA')
            elif j <= len(games_by_time.get(time_slots[i], [])):
                table[(i+1, j)].set_facecolor('#90EE90')  # Light green for assigned
            else:
                table[(i+1, j)].set_facecolor('#FFB6C1')  # Light red for unassigned
    
    plt.title("Game Schedule - By Time Slot")
    plt.tight_layout()
    plt.show()

def sort_time_key(time_slot):
    """Helper function to sort time slots chronologically"""
    try:
        # Parse format like "Monday_6:30"
        day, time = time_slot.split('_')
        
        # Map days to numbers
        day_order = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4}
        
        # Parse time
        time_parts = time.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        
        return (day_order.get(day, 5), hour, minute)
    except:
        return (999, 999, 999)  # Put malformed entries at the end








