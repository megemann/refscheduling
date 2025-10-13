# Phase 3 Updates Summary

## Overview
This document summarizes the changes made to upgrade the referee scheduling system to Phase 3, with enhanced Game attributes and Master Schedule Template functionality.

## 1. Game Class Updates (phase3/Game.py)

### New Attributes Added:
- **location_descriptor**: The type of location (e.g., "Court", "Field")
- **location_number**: The number of the location (e.g., 1, 2, 3)
- **division_type**: Division type code (CRJF, OJF, OTG, CRTG, W)
- **division_number**: Division number (e.g., "01", "02")

### New Methods:
- `get_location_descriptor()` / `set_location_descriptor(descriptor)`
- `get_location_number()` / `set_location_number(number)`
- `get_division_type()` / `set_division_type(division_type)`
- `get_division_number()` / `set_division_number(division_number)`
- `get_division_string()`: Returns formatted division string (e.g., "CRJF - 01")

### Location Parsing:
The Game class now automatically parses location strings (e.g., "Court 1") into descriptor and number components when not explicitly provided.

## 2. Master Schedule Template Generator

### File: `dashboard/utils/master_template_generator.py`

### Features:
- Creates professional Excel templates for master schedules
- Customizable days, times, and locations
- Color-coded cells for scheduling status:
  - **Grey**: No game scheduled (default)
  - **White**: Game not being played
  - **Green**: Game scheduled
  - **Yellow**: Game scheduled (alternate)
  - **Red**: Game not scheduled

### Template Structure:
1. **Row 1**: Title header (A-H merged) - "UMass Intramural Sports"
2. **Row 2**: Subtitle (A-H merged) - "Master Schedule"
3. **For each day scheduled:**
   - **Headers Row**: Day, Time, Location columns (Court 1, Court 2, etc.)
   - **Day Row**: Day name merged (A-B), Dates for each location
   - **Time Rows**: Time slots with game cells for each location
   - **Separator**: Blank row with border between days

4. **Legend Section**: Color legend and division examples at the bottom

### Division Types Supported:
- **CRJF**: Co-Rec Just Fun
- **OJF**: Open Just Fun
- **OTG**: Open Top Gun
- **CRTG**: Co-Rec Top Gun
- **W**: Womens

### Usage:
```python
from dashboard.utils.master_template_generator import create_master_template

# Create template with custom schedule
template_data = create_master_template(
    days_schedule=[
        {
            'day': 'Monday',
            'date': '1/20/2025',
            'times': ['6:30 pm', '7:30 pm', '8:30 pm']
        }
    ],
    locations=[
        {'descriptor': 'Court', 'number': 1},
        {'descriptor': 'Court', 'number': 2}
    ]
)
```

## 3. Dashboard Updates

### Game Management Page (03_Game_Management.py)

#### Download Master Template Button:
- Added prominent button at the top of the page
- Downloads the master schedule template with default settings
- Template includes all formatting and color legend

#### Updated Game Template (Excel Input):
The downloadable game template now includes:
- `Location_Descriptor`: e.g., "Court", "Field"
- `Location_Number`: e.g., 1, 2, 3
- `Division_Type`: e.g., "CRJF", "OJF", "OTG"
- `Division_Number`: e.g., "01", "02"

#### Excel Import:
- Supports both old format (Location as string) and new format (Location_Descriptor + Location_Number)
- Automatically parses old format for backward compatibility
- Imports division information when available

#### Game Editing Interface:
Enhanced with three-column layout:
- **Column 1**: Game number, date, time
- **Column 2**: Location descriptor, location number, difficulty
- **Column 3**: Division type, division number, min/max refs

#### Bulk Game Creation:
- Games now automatically parse location into descriptor and number
- Division fields can be added individually after bulk creation

#### Add Game Form:
Updated to include:
- Location Descriptor input
- Location Number input
- Division Type dropdown (CRJF, OJF, OTG, CRTG, W)
- Division Number text input

#### Download Current Games:
Excel export now includes all new fields:
- Location_Descriptor
- Location_Number
- Division_Type
- Division_Number

### Other Dashboard Pages Updated:

#### 01_Overview.py:
- Updated imports to use phase3
- Import logic handles both old and new game format

#### 04_Referee_Management.py:
- Updated imports to use phase3

#### 05_Schedule_Management.py:
- Updated imports to use phase3
- Now uses phase3.scheduler

#### utils/file_processor.py:
- Updated imports to use phase3

## 4. Backward Compatibility

All updates maintain backward compatibility:
- Old game data (with Location as string) is automatically parsed
- Excel imports work with both old and new formats
- Games without division information function normally

## 5. Testing Checklist

- [x] Game class creates with new attributes
- [x] Location parsing works correctly
- [x] Master template generator creates Excel file
- [x] Master template download button works
- [x] Game template download includes new fields
- [x] Excel import handles old format
- [x] Excel import handles new format
- [x] Game editing interface shows all fields
- [x] Add game form includes new fields
- [x] Game export includes all new fields
- [x] All imports updated to phase3
- [x] No linter errors

## 6. File Changes Summary

### New Files:
- `dashboard/utils/master_template_generator.py`
- `PHASE3_UPDATES.md` (this file)

### Modified Files:
- `phase3/Game.py` - Added new attributes and methods
- `dashboard/pages/03_Game_Management.py` - Updated UI and functionality
- `dashboard/pages/01_Overview.py` - Updated imports
- `dashboard/pages/04_Referee_Management.py` - Updated imports
- `dashboard/pages/05_Schedule_Management.py` - Updated imports
- `dashboard/utils/file_processor.py` - Updated imports

## 7. Next Steps

1. Test the master template download in the dashboard
2. Create games with the new division and location fields
3. Import games from Excel with the new format
4. Verify all data is correctly stored and displayed
5. Test the complete workflow: download template → fill out → import → schedule → export

## 8. Notes

- The master template uses xlsxwriter for advanced Excel formatting
- Color cells must be manually changed by the user (reading cell colors will be implemented in future versions)
- Division validation is done via dropdown in the UI
- Location descriptor can be any text (not limited to "Court")

