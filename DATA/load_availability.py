import pandas as pd

def load_availability_csv(csv_path):
    """
    Load availability from CSV into dict format.
    CSV should have refs as rows and columns like 'Monday_630', 'Tuesday_730', etc.
    Returns: {ref_name: {day_time: bool}}
    """
    df = pd.read_csv(csv_path, index_col=0)
    
    # Find columns that match day_time pattern
    day_time_cols = [col for col in df.columns if '_' in col]
    
    availability = {}
    for ref in df.index:
        availability[ref] = {}
        for col in day_time_cols:
            availability[ref][col] = bool(df.loc[ref, col])
    
    return availability

def get_available_refs(day_time, availability):
    """Get list of refs available for a specific day_time"""
    return [ref for ref, schedule in availability.items() 
            if schedule.get(day_time, False)] 