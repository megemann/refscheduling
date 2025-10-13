class Ref:
    def __init__(self, name, availability, email, phone_number, experience=3, effort=3):
        self.__name = name
        self.__availability = availability  # List or dict of availability (0/1 or bool)
        self.__email = email
        self.__phone_number = phone_number
        self.__experience = experience  # 1-5 scale
        self.__effort = effort  # 1-5 scale
        # Scheduling-specific attributes (set only in Schedule Management)
        self.__max_hours = 20  # Default max hours per week
        self.__assigned_games = []  # List of game numbers manually assigned

    def get_availability(self):
        return self.__availability

    def get_email(self):
        return self.__email

    def get_phone_number(self):
        return self.__phone_number

    def get_name(self):
        return self.__name

    def get_experience(self):
        return self.__experience

    def set_experience(self, experience):
        # Clamp to 1-5 range
        self.__experience = max(1, min(5, experience))

    def get_effort(self):
        return self.__effort

    def set_effort(self, effort):
        # Clamp to 1-5 range
        self.__effort = max(1, min(5, effort))
    
    def get_experience_normalized(self):
        """Get experience as 0-1 scale for optimization"""
        return (self.__experience - 1) / 4.0  # Convert 1-5 to 0-1
    
    def get_effort_normalized(self):
        """Get effort as 0-1 scale for optimization"""
        return (self.__effort - 1) / 4.0  # Convert 1-5 to 0-1
    
    # Scheduling-specific methods
    def get_max_hours(self):
        """Get maximum hours this ref can work per week"""
        return self.__max_hours
    
    def set_max_hours(self, max_hours):
        """Set maximum hours this ref can work per week"""
        self.__max_hours = max(0, max_hours)  # Ensure non-negative
    
    def get_assigned_games(self):
        """Get list of manually assigned game numbers"""
        return self.__assigned_games.copy()  # Return copy to prevent external modification
    
    def set_assigned_games(self, game_numbers):
        """Set list of manually assigned game numbers"""
        self.__assigned_games = list(game_numbers) if game_numbers else []
    
    def add_assigned_game(self, game_number):
        """Add a game number to assigned games"""
        if game_number not in self.__assigned_games:
            self.__assigned_games.append(game_number)
    
    def remove_assigned_game(self, game_number):
        """Remove a game number from assigned games"""
        if game_number in self.__assigned_games:
            self.__assigned_games.remove(game_number)
    
    def clear_assigned_games(self):
        """Clear all manually assigned games"""
        self.__assigned_games = []
    
    # Optimized assignment methods
    def set_optimized_games(self, games):
        """Set list of Game objects assigned by optimizer"""
        self.__optimized_games = games if games else []
    
    def get_optimized_games(self):
        """Get list of Game objects assigned by optimizer"""
        return getattr(self, '_Ref__optimized_games', [])
    
    def add_optimized_game(self, game):
        """Add a Game object to optimized assignments"""
        if not hasattr(self, '_Ref__optimized_games'):
            self.__optimized_games = []
        if game not in self.__optimized_games:
            self.__optimized_games.append(game)
    
    def clear_optimized_games(self):
        """Clear all optimized game assignments"""
        self.__optimized_games = []

    def __str__(self):
        return f"Ref: {self.__name}, Email: {self.__email}, Phone: {self.__phone_number}"