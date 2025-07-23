import pandas as pd

# Generate all time slots
games = []
for day in ['M', 'Tu', 'W', 'Th']:
    for time in ['630', '730', '830', '930']:
        games.append(f'{day}{time}')

# Create a dictionary of availability patterns for each ref
time_dicts = {
    'week_all': [1] * len(games),
    'all': [1,1,1,1],
    'no630': [0,1,1,1],
    'no730': [1,0,1,1],
    'no830': [1,1,0,1],
    'no930': [1,1,1,0],
    '630730': [1,1,0,0],
    '630830': [1,0,1,0],
    '630930': [1,0,0,1],
    '730930': [0,1,0,1],
    '730830': [0,1,1,0],
    '830930': [0,0,1,1],
    '630': [1,0,0,0],
    '730': [0,1,0,0],
    '830': [0,0,1,0],
    '930': [0,0,0,1],
    'none': [0,0,0,0]
}

# From the availbility file
avail_dict = {
    'ref1': time_dicts['all'] * 3 + time_dicts['no730'],
    'ref2': time_dicts['no630'] * 4,
    'ref3': time_dicts['none'] * 3 + time_dicts['no630'],
    'ref4': time_dicts['no930'] + time_dicts['all'] * 3,
    'ref5': time_dicts['no630'] * 4, 
    'ref6': (time_dicts['all'] + time_dicts['none']) * 2,
    'ref7': time_dicts['no630'] + time_dicts['no930'] + time_dicts['no630'] + time_dicts['630'],
    'ref8': time_dicts['630730'] + time_dicts['all'] + time_dicts['630'] + time_dicts['all'],
    'ref9': (time_dicts['no630'] + time_dicts['all']) * 2,
    'ref10': time_dicts['week_all'],
    'ref11': time_dicts['all'] * 2 + time_dicts['none'] +  time_dicts['all'],
    'ref12': time_dicts['all'] * 3 + time_dicts['no930'],
    'ref13': time_dicts['all'] * 3 + time_dicts['630730'],
    'ref14': time_dicts['none'] * 2 + time_dicts['all'] * 2,
    'ref15': time_dicts['all'] * 3 + time_dicts['none'], 
    'ref16': time_dicts['none'] + time_dicts['all'] * 2 + time_dicts['630'],
    'ref17': time_dicts['all'] * 3 + time_dicts['630730'],
    'ref18': time_dicts['no830'] + time_dicts['830930'] + time_dicts['none'] + time_dicts['all'],
    'ref19': time_dicts['all'] * 2 + time_dicts['none'] + time_dicts['630730'],
    'ref20': time_dicts['all'] + time_dicts['no630'] + time_dicts['all'] * 2,
    'ref21': time_dicts['all'] * 3 + time_dicts['none'],
    'ref22': time_dicts['all'] + time_dicts['no630'] + time_dicts['no730']  + time_dicts['630730'],
    'ref23': time_dicts['all'] + time_dicts['no630'] + time_dicts['all'] + time_dicts['830930'],
    'ref24': time_dicts['all'] * 3 + time_dicts['630'],
    'ref25': time_dicts['no630'] + time_dicts['all'] + time_dicts['no630'] + time_dicts['none'], 
    'ref26': time_dicts['all'] + time_dicts['no730'] + time_dicts['no630'] + time_dicts['none'],
    'ref27': time_dicts['all'] * 2 + time_dicts['no630'] + time_dicts['all'],
    'ref28': time_dicts['no730'] + time_dicts['all'] * 3,
    'ref29': time_dicts['week_all'],
    'ref30': time_dicts['all'] * 3 + time_dicts['630730'], 
    'ref31': time_dicts['no730'] + time_dicts['630'] + time_dicts['none'] * 2,
    'ref32': time_dicts['none'] + time_dicts['all'] + time_dicts['no930'] + time_dicts['none'],
    'ref33': time_dicts['all'] * 3 + time_dicts['none'],
    'ref34': time_dicts['930'] + time_dicts['no630'] + time_dicts['all'] * 2,
    'ref35': (time_dicts['no630'] + time_dicts['all']) * 2 
}

# Create a list of all time slots (Monday through Thursday, 6:30-9:30)
time_slots = []
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
times = ['6:30', '7:30', '8:30', '9:30']

for day in days:
    for time in times:
        time_slots.append(f"{day}_{time}")

# Create the dataframe with refs as rows and time slots as columns
ref_availability = {}

for ref_name, availability_pattern in avail_dict.items():
    ref_availability[ref_name] = availability_pattern

# Convert to DataFrame
availability_df = pd.DataFrame.from_dict(ref_availability, orient='index', columns=time_slots)
availability_df.to_csv('DATA/BB2025Phase1Convert.csv')