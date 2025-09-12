class Scheduler:
    def __init__(self, refs, games):
        """
        Initialize scheduler with referees and games.
        
        Args:
            refs: List of Ref objects
            games: List of Game objects
        """
        self.refs = refs
        self.games = games
        
        # Optimization parameters (will be set from Schedule Management)
        self.max_hours_per_week = 20
        self.max_hours_per_day = 8
        
        # Constraint weights
        self.weight_hour_balancing = 1.0
        self.weight_skill_combo = 1.0
        self.weight_low_skill_penalty = 1.0
        self.weight_shift_block_penalty = 1.0
        self.weight_effort_bonus = 1.0
    
    def set_parameters(self, params):
        """Set optimization parameters from Schedule Management."""
        self.max_hours_per_week = params.get('max_hours_per_week', 20)
        self.max_hours_per_day = params.get('max_hours_per_day', 8)
        self.weight_hour_balancing = params.get('weight_hour_balancing', 1.0)
        self.weight_skill_combo = params.get('weight_skill_combo', 1.0)
        self.weight_low_skill_penalty = params.get('weight_low_skill_penalty', 1.0)
        self.weight_shift_block_penalty = params.get('weight_shift_block_penalty', 1.0)
        self.weight_effort_bonus = params.get('weight_effort_bonus', 1.0)
    
    def optimize(self):
        """
        Run the optimization algorithm to assign referees to games.
        Currently prints debug information.
        """
        print("=== SCHEDULER DEBUG OUTPUT ===")
        print(f"Total Referees: {len(self.refs)}")
        print(f"Total Games: {len(self.games)}")
        print()
        
        print("=== REFEREES ===")
        for i, ref in enumerate(self.refs):
            print(f"Ref {i+1}: {ref.get_name()}")
            print(f"  - Email: {ref.get_email()}")
            print(f"  - Phone: {ref.get_phone_number()}")
            print(f"  - Experience: {ref.get_experience()}")
            print(f"  - Effort: {ref.get_effort()}")
            print(f"  - Max Hours: {ref.get_max_hours()}")
            print(f"  - Assigned Games: {ref.get_assigned_games()}")
            print(f"  - Availability: {ref.get_availability()}")
            print()
        
        print("=== GAMES ===")
        for i, game in enumerate(self.games):
            print(f"Game {i+1}: #{game.get_number()}")
            print(f"  - Date: {game.get_date()}")
            print(f"  - Time: {game.get_time()}")
            print(f"  - Location: {game.get_location()}")
            print(f"  - Difficulty: {game.get_difficulty()}")
            print(f"  - Min Refs: {game.get_min_refs()}")
            print(f"  - Max Refs: {game.get_max_refs()}")
            print()
        
        print("=== OPTIMIZATION PARAMETERS ===")
        print(f"Max Hours Per Week: {self.max_hours_per_week}")
        print(f"Max Hours Per Day: {self.max_hours_per_day}")
        print(f"Weight Hour Balancing: {self.weight_hour_balancing}")
        print(f"Weight Skill Combo: {self.weight_skill_combo}")
        print(f"Weight Low Skill Penalty: {self.weight_low_skill_penalty}")
        print(f"Weight Shift Block Penalty: {self.weight_shift_block_penalty}")
        print(f"Weight Effort Bonus: {self.weight_effort_bonus}")
        print()
        
        print("=== MANUAL CONSTRAINTS ===")
        manual_assignments = {}
        for ref in self.refs:
            assigned_games = ref.get_assigned_games()
            if assigned_games:
                manual_assignments[ref.get_name()] = assigned_games
        
        if manual_assignments:
            for ref_name, game_numbers in manual_assignments.items():
                print(f"{ref_name}: Games {game_numbers}")
        else:
            print("No manual assignments found.")
        
        print("\n=== OPTIMIZATION COMPLETE ===")
        print("All data successfully accessed for constraint processing.")
        
        return True  # Placeholder for optimization result
