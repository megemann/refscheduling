
## Current Features
- Availability input (w/ t-shirt size, phone number, email, etc.)
- Simple greedy algorithm with no interface
- General simplified classes
- Outputting a final schedule to excel
  
## New Features

### Ref Class
Must have
1. Ref.Name
2. Ref.email
3. Ref.phone_number
4. Ref.Experience
5. Ref.Effort
6. Ref.Availability (is_available)

### Game Class
Must have
1. Game.Date
2. Game.Time
3. Game.Number
4. Game.Difficulty (Maps to a division type)
5. Game.Refs
6. Game.Location
7. Game.MIN_REFS
8. Game.MAX_REFS

### Functionality
- Skill input for ref
- Effort input for ref
- Division difficulty linking with games
- Game Schedule input
- Master Document for fast input
- Pre-Optimization validation checking (like cant cover one game)
- Automated Reminders for Shifts / Games

### Pages
- Availabilty template with coverage statistics when inputted
- Ref assignment page, excel input, altering of skill and effort levels available
- Game assignment page, excel input, altering of game difficulties 
- Parameters page - tune parameters (min refs, max refs, max hours per day/week, etc. )
- Optimization page - tune weights of objective, explain criteria, show post-optimization scores
- Schedule output / editor page - prior to outputting as excel, allow for any changes to schedule (drag and drop / select)
> Integrate the last two so we can set shifts before optimization in stone

## Future Ideas 
- Integrate with fusion
- Adaptive difficulty detection throughout the season
- Playoff support
- Better interfaces
- Persistant file storage and databases
- Coverage checker
- Playing time consideration
- Payroll integration
- Reoccuring schedules
- Enhanced constraints
- Enhanced ref stats with YOG and Thursday fairness