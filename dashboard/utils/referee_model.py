import pandas as pd
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Referee:
    """Referee data model for session state management"""
    name: str
    email: str = ""
    phone: str = ""
    shirt_size: str = ""
    team_info: str = ""
    availability: List[int] = None  # Binary list: 1 = available, 0 = not available
    experience: int = 1  # 1-5 scale (to be added later)
    effort: int = 3  # 1-5 scale (to be added later)
    
    def __post_init__(self):
        if self.availability is None:
            self.availability = []
    
    def get_availability_count(self) -> int:
        """Get total number of available time slots"""
        return sum(self.availability) if self.availability else 0
    
    def is_available_at_slot(self, slot_index: int) -> bool:
        """Check if referee is available at specific time slot"""
        if 0 <= slot_index < len(self.availability):
            return bool(self.availability[slot_index])
        return False
    
    def get_display_name(self) -> str:
        """Get a clean display name"""
        return self.name.replace('_', ' ').title()

def create_referee_list_from_excel(df, time_columns: List[str]) -> List[Referee]:
    """
    Extract referee information from Excel format and create Referee objects
    
    Excel columns expected:
    0: Name
    1: Shirt Size  
    2: Phone
    3: Email
    4: Team Name/Time Playing
    5+: Availability time slots
    """
    referees = []
    
    for idx, row in df.iterrows():
        # Skip header rows (rows 0 and 1 contain headers)
        if idx < 2:
            continue
            
        # Check for DONE marker to stop processing
        if str(row.iloc[0]).strip().upper() == 'DONE':
            break
            
        # Skip if no name or example row
        name_cell = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
        if not name_cell or name_cell.startswith('(EXAMPLE)') or name_cell == '':
            continue
        
        # Extract basic information
        name = name_cell
        shirt_size = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) and len(str(row.iloc[1]).strip()) > 0 else ""
        phone = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) and len(str(row.iloc[2]).strip()) > 0 else ""
        email = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) and len(str(row.iloc[3]).strip()) > 0 else ""
        team_info = str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) and len(str(row.iloc[4]).strip()) > 0 else ""
        
        # Extract availability (binary array)
        availability = [0] * len(time_columns)
        time_col_start = 5  # After basic info columns
        
        for slot_idx in range(min(len(time_columns), len(df.columns) - time_col_start)):
            col_idx = time_col_start + slot_idx
            if col_idx < len(row):
                cell_value = row.iloc[col_idx]
                # Handle checkbox values: True, TRUE, 1, ✓ = available
                if cell_value in [True, 'TRUE', 'True', 1, '1', '✓']:
                    availability[slot_idx] = 1
        
        # Create referee object
        referee = Referee(
            name=name,
            email=email,
            phone=phone,
            shirt_size=shirt_size,
            team_info=team_info,
            availability=availability
        )
        
        referees.append(referee)
    
    return referees

def get_availability_matrix_from_referees(referees: List[Referee], time_columns: List[str]) -> pd.DataFrame:
    """
    Convert referee list back to availability matrix format for MILP
    Returns DataFrame with referee names as index and time slots as columns
    """
    availability_data = {}
    
    for referee in referees:
        # Use original name format for compatibility
        ref_key = referee.name.replace(' ', '_').replace(',', '').replace('.', '').replace('(', '').replace(')', '')
        availability_data[ref_key] = referee.availability
    
    return pd.DataFrame.from_dict(availability_data, orient='index', columns=time_columns)
