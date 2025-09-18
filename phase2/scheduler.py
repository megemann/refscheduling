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
        

        # Start Pyomo Code
        
        import pyomo.environ as pyo
        from pyomo.environ import RangeSet, Constraint
        import numpy as np
        from pyomo.opt import SolverFactory

        refs = self.refs
        model = pyo.ConcreteModel()

        # Get the unique set of days and times from all games
        unique_days = set()
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        unique_times = set()
        games_per_time = {}

        for game in self.games:
            day = game.get_date()
            time = game.get_time()
            unique_days.add(day)
            unique_times.add(time)
            # Use (day, time) as the key to count games at the same time
            key = (day, time)
            if key not in games_per_time:
                games_per_time[key] = 0
            games_per_time[key] += 1

        # Find the maximum number of games occurring at the same time
        max_games_in_hour = max(games_per_time.values()) if games_per_time else 1

        # Validate input dimensions before creating the decision variable
        num_refs = len(self.refs)
        num_days = len(unique_days)
        num_times = len(unique_times)
        if num_refs == 0 or num_days == 0 or num_times == 0 or max_games_in_hour == 0:
            raise ValueError("Cannot create decision variables: refs, days, times, or games per hour is zero.")

        model.x = pyo.Var( # x_{r,d,h,g}
            range(num_refs),
            range(num_days),
            range(num_times),
            range(max_games_in_hour),
            within=pyo.Binary
        )
        model.R = pyo.RangeSet(0, num_refs - 1)
        model.D = pyo.RangeSet(0, num_days - 1)
        model.H = pyo.RangeSet(0, num_times - 1)
        model.G = pyo.RangeSet(0, max_games_in_hour - 1)

        def is_available(r, d, h): # rule of a_{r,d,h}
            availability = refs[r].get_availability()
            return availability[d*num_times + h] #offset by day and get hour index

        def get_ref_experience(r): # REx_r
            return refs[r].get_experience()

        def get_ref_effort(r): #E_r
            return refs[r].get_effort()

        def get_ref_max_weekly_hours(r):
            return refs[r].get_max_hours()

        def game_to_index(game):
            """
            Convert a Game object to its (d, h, g) indices.
            
            Args:
                game: Game object to convert
                
            Returns:
                tuple: (d, h, g) indices, or None if game not found
            """
            if not game:
                return None
                
            # Sort days and times (same as get_game_info)
            sorted_days = sorted(unique_days, key=lambda day: days_order.index(day) if day in days_order else 999)
            
            def parse_time_for_sort(time_str):
                from datetime import datetime
                try:
                    if ':' in time_str:
                        return datetime.strptime(time_str, "%H:%M").time()
                    else:
                        return datetime.strptime(f"{time_str}:00", "%H:%M").time()
                except:
                    return datetime.strptime("12:00", "%H:%M").time()
            
            sorted_times = sorted(unique_times, key=parse_time_for_sort)
            
            # Find day index
            target_day = game.get_date()
            try:
                d = sorted_days.index(target_day)
            except ValueError:
                return None  # Day not found
            
            # Find hour index  
            target_time = game.get_time()
            try:
                h = sorted_times.index(target_time)
            except ValueError:
                return None  # Time not found
            
            # Find game index at this day/time
            games_at_time = []
            for g_candidate in self.games:
                if g_candidate.get_date() == target_day and g_candidate.get_time() == target_time:
                    games_at_time.append(g_candidate)
            
            # Sort games by their number (same as get_game_info)
            games_at_time.sort(key=lambda g: g.get_number())
            
            # Find the position of our target game
            try:
                g = games_at_time.index(game)
            except ValueError:
                return None  # Game not found in the list
            
            return (d, h, g)

        def get_game_info(d, h, g):
            """
            Return the Game object at (d, h, g) if it exists, else return None.
            d: day index
            h: time index
            g: game index at that day/time
            """
            # Sort days and times
            sorted_days = sorted(unique_days, key=lambda day: days_order.index(day) if day in days_order else 999)

            def parse_time_for_sort(time_str):
                from datetime import datetime
                try:
                    if ':' in time_str:
                        return datetime.strptime(time_str, "%H:%M").time()
                    else:
                        return datetime.strptime(f"{time_str}:00", "%H:%M").time()
                except:
                    return datetime.strptime("12:00", "%H:%M").time()

            sorted_times = sorted(unique_times, key=parse_time_for_sort)

            # Check if indices are valid
            if d >= len(sorted_days) or h >= len(sorted_times):
                return None

            target_day = sorted_days[d]
            target_time = sorted_times[h]

            # Find all games at this day/time
            games_at_time = []
            for game in self.games:
                if game.get_date() == target_day and game.get_time() == target_time:
                    games_at_time.append(game)

            # Sort games by their number (lowest number = 0th game)
            games_at_time.sort(key=lambda game: game.get_number())

            if g >= len(games_at_time):
                return None

            return games_at_time[g]

        # For compatibility, provide wrappers
        def get_game_difficulty(d, h, g):
            """Return the difficulty of the game at (d, h, g), or 0 if no game exists."""
            game = get_game_info(d, h, g)
            if not game:
                return 0
            difficulty_str = game.get_difficulty()
            try:
                return float(difficulty_str)
            except ValueError:
                difficulty_map = {
                    "Open - Just Fun": 4,
                    "Open - Top Gun": 5,
                    "Co-Rec - Just Fun": 1,
                    "Co-Rec - Top Gun": 4,
                    "Womens": 3,
                    "TBD": 3
                }
                return difficulty_map.get(difficulty_str, 3)

        def is_game_scheduled(d, h, g):
            """Return 1 if a game exists at (d, h, g), else 0."""
            return 1 if get_game_info(d, h, g) else 0

        # Handles both scheduled and number of refs
        def get_max_refs(d, h, g):
            game = get_game_info(d, h, g)
            if not game:
                return 0
            return game.get_max_refs()

        def get_min_refs(d, h, g):
            game = get_game_info(d, h, g)
            if not game:
                return 0
            return game.get_min_refs()
            
        # Hard Constraints 
        def rule1(model, r, d, h):
            """No referee can be assigned to more than one game per hour."""
            return sum(model.x[r, d, h, g] for g in model.G) <= 1
        model.rule1_constraint = Constraint(
            model.R, model.D, model.H, rule=rule1
        )

        def rule2(model, r, d):
            """No referee can work more than max_hours_per_day in a night."""
            return sum(
                sum(model.x[r, d, h, g] for g in model.G)
                for h in model.H
            ) <= self.max_hours_per_day
        model.rule2_constraint = Constraint(
            model.R, model.D, rule=rule2
        )

        def rule3(model, r):
            """No referee can be scheduled more than the designated hours a week."""
            return sum(
                sum(
                    sum(model.x[r, d, h, g] for g in model.G)
                    for h in model.H
                )
                for d in model.D
            ) <= min(self.max_hours_per_week, get_ref_max_weekly_hours(r))
        model.rule3_constraint = Constraint(
            model.R, rule=rule3
        )

        def rule4(model, r, d, h, g):
            """
            No referee can be scheduled during a time they have no availability.
            """
            # is_available should return 0 or 1
            avail = is_available(r, d, h)
            # Defensive: if avail is not 0 or 1, treat as unavailable
            if not isinstance(avail, int):
                try:
                    avail = int(avail)
                except Exception:
                    print('Excepted')
                    avail = 0
            return model.x[r, d, h, g] <= avail
        model.rule4_constraint = Constraint(
            model.R, model.D, model.H, model.G, rule=rule4
        )

        def rule5_min(model, d, h, g):
            """Each scheduled game must have at least MIN_REF assigned."""
            if not is_game_scheduled(d, h, g):
                return pyo.Constraint.Skip
            refs_assigned = sum(model.x[r, d, h, g] for r in model.R)
            return refs_assigned >= get_min_refs(d, h, g)
        model.rule5_min_constraint = pyo.Constraint(
            model.D, model.H, model.G, rule=rule5_min
        )
        
        def rule5_max(model, d, h, g):
            """Each scheduled game must have no more than MAX_REF assigned."""
            if not is_game_scheduled(d, h, g):
                return pyo.Constraint.Skip
            refs_assigned = sum(model.x[r, d, h, g] for r in model.R)
            return refs_assigned <= get_max_refs(d, h, g)
        model.rule5_max_constraint = pyo.Constraint(
            model.D, model.H, model.G, rule=rule5_max
        )

        def rule6(model, r, d, h, g):
            """Referees can only work games that are scheduled."""
            return model.x[r, d, h, g] <= is_game_scheduled(d, h, g)
        model.rule6_constraint = Constraint(
            model.R, model.D, model.H, model.G, rule=rule6
        )

        # Helper function to find game by number
        def find_game_by_number(game_number):
            for game in self.games:
                if game.get_number() == game_number:
                    return game
            return None
        
        # User Defined Constraints

        # Create a ConstraintList to hold manual assignment constraints
        model.c1 = pyo.ConstraintList()

        for ref_idx, ref in enumerate(refs):
            for game_number in ref.get_assigned_games():
                game = find_game_by_number(game_number)
                indices = game_to_index(game)
                if indices is not None:
                    d, h, g = indices
                    # Force assignment: x[ref_idx, d, h, g] == 1
                    model.c1.add(model.x[ref_idx, d, h, g] == 1)
                else:
                    print(f"Warning: Could not map game number {game_number} to indices for manual assignment.")
        
        #Objective

        n = len(refs) # N

        def ref_total_hours(model, r): #h_i
            # Triple sum over d, h, g for referee r
            return sum(
                sum(
                    sum(model.x[r, d, h, g] for g in model.G)
                    for h in model.H
                )
                for d in model.D
            )

        def ref_mean_hours(model): # h-bar_i
            return sum(ref_total_hours(model, r) for r in model.R) / n

        # Define set C = refs not at their cap (static evaluation)
        # C = refs where max_hours > mean_max_hours - 3
        all_max_hours = [get_ref_max_weekly_hours(r) for r in range(num_refs)]
        mean_max_hours = sum(all_max_hours) / len(all_max_hours)
        threshold = mean_max_hours - 3
        C_set = [r for r in range(num_refs) if get_ref_max_weekly_hours(r) > threshold]
        
        print(f"Mean max hours: {mean_max_hours:.2f}, Threshold: {threshold:.2f}")
        print(f"Refs not at cap (C): {len(C_set)} out of {num_refs}")

        # Create auxiliary variables d_i >= 0 for each referee
        model.d = pyo.Var(model.R, within=pyo.NonNegativeReals)

        # Add constraints for d_i >= h_i - h_bar and d_i >= h_bar - h_i, only for refs in C
        def d_lower_bound_1(model, r):
            if r not in C_set:
                return pyo.Constraint.Skip
            h_i = ref_total_hours(model, r)
            h_bar = ref_mean_hours(model)
            return model.d[r] >= h_i - h_bar
        model.d_lower_1 = pyo.Constraint(model.R, rule=d_lower_bound_1)

        def d_lower_bound_2(model, r):
            if r not in C_set:
                return pyo.Constraint.Skip
            h_i = ref_total_hours(model, r)
            h_bar = ref_mean_hours(model)
            return model.d[r] >= h_bar - h_i
        model.d_lower_2 = pyo.Constraint(model.R, rule=d_lower_bound_2)
        
        # Calculate all normalization constants as fixed values
        
        # Calculate mean effort across all refs (constant)
        all_ref_efforts = [get_ref_effort(r) for r in C_set] if C_set else [1]
        MEAN_EFFORT = sum(all_ref_efforts) / len(all_ref_efforts) if all_ref_efforts else 1.0
        
        # Calculate expected mean hours (constant - based on total games distributed)
        total_games = len(self.games)
        expected_total_assignments = total_games * 2  # Assuming ~2 refs per game on average
        MEAN_HOURS = expected_total_assignments / len(C_set) if C_set else 1.0
        
        # Calculate mean skill across all refs (constant)
        all_ref_experiences = [get_ref_experience(r) for r in model.R]
        MEAN_SKILL = sum(all_ref_experiences) / len(all_ref_experiences) if all_ref_experiences else 3.0
        
        # Calculate mean difficulty across all games (constant)
        all_game_difficulties = []
        for dd in model.D:
            for hh in model.H:
                for gg in model.G:
                    all_game_difficulties.append(get_game_difficulty(dd, hh, gg))
        MEAN_DIFFICULTY = sum(all_game_difficulties) / len(all_game_difficulties) if all_game_difficulties else 3.0
        
        # Calculate additional normalizers
        max_possible_starts = len(refs) * len(set(game.get_date() for game in self.games))  
        TB_NORMALIZER = max_possible_starts * 0.3 if max_possible_starts > 0 else 1.0
        
        max_skill_diff = 4.0  # Max experience is 5, min is 1: 5-1=4
        max_possible_pairs = len(refs) * (len(refs) - 1) / 2  # All possible ref pairs
        expected_active_pairs = max_possible_pairs * 0.6  # Expect 650% of pairs to be active

        COMBO_NORMALIZER = max_skill_diff * expected_active_pairs if expected_active_pairs > 0 else 1.0
        
        # Target baseline for all normalized objectives (when weights = 1.0, objectives should be around this value)
        # Scale: 0-10 for weight control, starting at 2.5 baseline for balanced objectives
        TARGET_BASELINE = 2.5  # All objectives will be scaled to be around 2.5 when balanced
        WEIGHT_SCALE_MAX = 10.0  # Maximum meaningful weight value (provides 0-10 scale)
        
        # Calculate normalizers to achieve the target baseline
        # Each normalizer is adjusted so the typical objective value = TARGET_BASELINE
        EFFORT_NORMALIZER = (MEAN_EFFORT * MEAN_HOURS) / TARGET_BASELINE
        BALANCING_NORMALIZER = 1.0 / TARGET_BASELINE  # Balancing typically ranges 0-3, target 2.5
        SKILL_NORMALIZER = MEAN_SKILL / TARGET_BASELINE 
        TB_NORMALIZER = TB_NORMALIZER / TARGET_BASELINE  # Adjust shift block normalizer 
        COMBO_NORMALIZER = COMBO_NORMALIZER / TARGET_BASELINE  # Adjust combo normalizer
        
        print(f"=== NORMALIZATION CONSTANTS (Baseline: {TARGET_BASELINE}, Scale: 0-{WEIGHT_SCALE_MAX}) ===")
        print(f"Mean Effort: {MEAN_EFFORT:.3f}")
        print(f"Expected Mean Hours: {MEAN_HOURS:.3f}")
        print(f"Mean Skill: {MEAN_SKILL:.3f}")
        print(f"Mean Difficulty: {MEAN_DIFFICULTY:.3f}")
        print(f"Effort Normalizer: {EFFORT_NORMALIZER:.3f}")
        print(f"Skill Normalizer: {SKILL_NORMALIZER:.3f}")
        print(f"Time Block Normalizer: {TB_NORMALIZER:.3f}")
        print(f"Skill Combo Normalizer: {COMBO_NORMALIZER:.3f}")
        print(f"All objectives target ~{TARGET_BASELINE} when weights = 1.0")
        print(f"Weight scale: 0-{WEIGHT_SCALE_MAX} (0=disable, {TARGET_BASELINE}=baseline, {WEIGHT_SCALE_MAX}=max emphasis)")
        print()

        # Define the balancing penalty b(x) = (1/|C|) * sum_{i in C} d_i
        def balancing_penalty(model):
            if len(C_set) == 0:
                return 0
            return (1.0 / (len(C_set) * BALANCING_NORMALIZER)) * sum(model.d[r] for r in C_set)

         # Define effort objective e(x) = (1/|C|) * sum_{i in C} (E_i * h_i) / EFFORT_NORMALIZER
        def effort_objective(model):
            if len(C_set) == 0:
                return 0
            return (1.0 / (len(C_set) * EFFORT_NORMALIZER)) * sum(
                (get_ref_effort(r) * ref_total_hours(model, r))
                for r in C_set
            )

        # Create auxiliary variables for shift blocks
        model.start = pyo.Var(model.R, model.D, model.H, within=pyo.Binary)
        
        # Shift block constraints
        def start_constraint_1(model, r, d, h):
            """start_{r,d,h} >= sum_g x_{r,d,h,g} - sum_g x_{r,d,h-1,g}"""
            current_hour = sum(model.x[r, d, h, g] for g in model.G)
            if h == 0:  # First hour of day - no previous hour
                prev_hour = 0
            else:
                prev_hour = sum(model.x[r, d, h-1, g] for g in model.G)
            return model.start[r, d, h] >= current_hour - prev_hour
        model.start_constraint_1 = pyo.Constraint(model.R, model.D, model.H, rule=start_constraint_1)
        
        def start_constraint_2(model, r, d, h):
            """start_{r,d,h} <= sum_g x_{r,d,h,g}"""
            return model.start[r, d, h] <= sum(model.x[r, d, h, g] for g in model.G)
        model.start_constraint_2 = pyo.Constraint(model.R, model.D, model.H, rule=start_constraint_2)
        
        def start_constraint_3(model, r, d, h):
            """start_{r,d,h} <= 1 - sum_g x_{r,d,h-1,g}"""
            if h == 0:  # First hour of day
                return model.start[r, d, h] <= 1  # No constraint from previous hour
            else:
                prev_hour = sum(model.x[r, d, h-1, g] for g in model.G)
                return model.start[r, d, h] <= 1 - prev_hour
        model.start_constraint_3 = pyo.Constraint(model.R, model.D, model.H, rule=start_constraint_3)
        
        # Time block penalty tb(x) = (1/TB_NORMALIZER) * sum_r sum_d sum_h start_{r,d,h}
        def time_block_penalty(model):
            return (1.0 / TB_NORMALIZER) * sum(
                sum(
                    sum(model.start[r, d, h] for h in model.H)
                    for d in model.D
                )
                for r in model.R
            )

        # Create auxiliary variables for skill pair combinations
        model.y = pyo.Var(model.R, model.R, model.D, model.H, model.G, within=pyo.Binary)
        # Skill pair constraints y_{i,j,d,h,g}
        def y_constraint_1(model, i, j, d, h, g):
            """y_{i,j,d,h,g} <= x_{i,d,h,g}"""
            if i >= j:  # Only for i < j
                return pyo.Constraint.Skip
            return model.y[i, j, d, h, g] <= model.x[i, d, h, g]
        model.y_constraint_1 = pyo.Constraint(model.R, model.R, model.D, model.H, model.G, rule=y_constraint_1)
        
        def y_constraint_2(model, i, j, d, h, g):
            """y_{i,j,d,h,g} <= x_{j,d,h,g}"""
            if i >= j:  # Only for i < j
                return pyo.Constraint.Skip
            return model.y[i, j, d, h, g] <= model.x[j, d, h, g]
        model.y_constraint_2 = pyo.Constraint(model.R, model.R, model.D, model.H, model.G, rule=y_constraint_2)
        
        def y_constraint_3(model, i, j, d, h, g):
            """y_{i,j,d,h,g} >= x_{i,d,h,g} + x_{j,d,h,g} - 1"""
            if i >= j:  # Only for i < j
                return pyo.Constraint.Skip
            return model.y[i, j, d, h, g] >= model.x[i, d, h, g] + model.x[j, d, h, g] - 1
        model.y_constraint_3 = pyo.Constraint(model.R, model.R, model.D, model.H, model.G, rule=y_constraint_3)
        
        # Skill combination bonus p(x)
        L = len(self.games)  # Total number of games
        def skill_combination_bonus(model):
            if L == 0 or COMBO_NORMALIZER == 0:
                return 0
            return (1.0 / COMBO_NORMALIZER) * sum(
                sum(
                    sum(
                        sum(
                            sum(
                                ((get_ref_experience(i) - get_ref_experience(j)) * model.y[i, j, d, h, g] 
                                if get_ref_experience(i) >= get_ref_experience(j) 
                                else (get_ref_experience(j) - get_ref_experience(i)) * model.y[i, j, d, h, g])
                                for j in model.R if j > i
                            )
                            for i in model.R
                        )
                        for g in model.G
                    )
                    for h in model.H
                )
                for d in model.D
            )

        # Create auxiliary variables for skill deficit penalty
        model.u = pyo.Var(model.D, model.H, model.G, within=pyo.NonNegativeReals)
        
        # Skill deficit constraints (use constant mean values calculated above)
        def skill_deficit_constraint(model, d, h, g):
            """
            u_{d,h,g} >= (GEx_{d,h,g} / MEAN_DIFFICULTY) * sum_i x_{i,d,h,g} - sum_i (REx_i / MEAN_SKILL) * x_{i,d,h,g}
            """
            game_difficulty = get_game_difficulty(d, h, g)
            refs_assigned = sum(model.x[r, d, h, g] for r in model.R)
            skill_sum = sum((get_ref_experience(r) / MEAN_SKILL) * model.x[r, d, h, g] for r in model.R)
            return model.u[d, h, g] >= (game_difficulty / MEAN_DIFFICULTY) * refs_assigned - skill_sum
        model.skill_deficit_constraint = pyo.Constraint(model.D, model.H, model.G, rule=skill_deficit_constraint)
        
        # Skill penalty s(x) = (1/SKILL_NORMALIZER) * sum_{d,h,g} u_{d,h,g}
        def skill_penalty(model):
            if L == 0 or SKILL_NORMALIZER == 0:
                return 0
            return (1.0 / (L * SKILL_NORMALIZER)) * sum(
                sum(sum(model.u[d, h, g] for g in model.G) for h in model.H)
                for d in model.D
            )

        # Final Objective Function
        def objective_function(model):
            return (
                self.weight_effort_bonus * effort_objective(model) -
                self.weight_hour_balancing * balancing_penalty(model) -
                self.weight_low_skill_penalty * skill_penalty(model) -
                self.weight_shift_block_penalty * time_block_penalty(model) +
                self.weight_skill_combo * skill_combination_bonus(model)
            )
        
        model.objective = pyo.Objective(rule=objective_function, sense=pyo.maximize)

        print('=== MODEL CONSTRUCTION COMPLETE ===')
        print(f"Model size: {num_refs} refs × {num_days} days × {num_times} times × {max_games_in_hour} games")
        print('Now solving with Gurobi...')
        
        # Solve with Gurobi
        try:
            
            solver = SolverFactory('gurobi')
            solver.options['OutputFlag'] = 1
            solver.options['TimeLimit']  = 240
            solver.options['MIPGap']     = 0.05
            
            
            # Add callback for progress tracking
            import json
            import os
            
            def gurobi_callback(cb_m, cb_where):
                """Gurobi callback to track optimization progress"""
                try:
                    if cb_where == gurobipy.GRB.Callback.MIP:
                        # Get progress information
                        objbnd = cb_m.cbGet(gurobipy.GRB.Callback.MIP_OBJBND)
                        objbst = cb_m.cbGet(gurobipy.GRB.Callback.MIP_OBJBST)
                        solcnt = cb_m.cbGet(gurobipy.GRB.Callback.MIP_SOLCNT)
                        runtime = cb_m.cbGet(gurobipy.GRB.Callback.RUNTIME)
                        
                        # Calculate percentage progress (approximate)
                        if objbnd != float('inf') and objbst != float('inf') and objbnd != 0:
                            gap = abs(objbst - objbnd) / abs(objbnd)
                            progress = max(0, min(95, (1 - gap) * 100))  # Cap at 95%
                        else:
                            progress = min(95, (runtime / 600) * 100)  # Time-based progress, cap at 95%
                        
                        # Write progress to file
                        progress_data = {
                            'progress': progress,
                            'runtime': runtime,
                            'solutions_found': solcnt,
                            'best_objective': objbst if objbst != float('inf') else None,
                            'bound': objbnd if objbnd != float('inf') else None
                        }
                        
                        with open('optimization_progress.json', 'w') as f:
                            json.dump(progress_data, f)
                            
                except Exception as e:
                    # Don't let callback errors crash the optimization
                    pass
            
            # Try to set callback if using Gurobi directly
            try:
                import gurobipy
                solver.options['LogToConsole'] = 1
                # Note: Callback through Pyomo is limited, but we'll try
                results = solver.solve(model, tee=True)
            except ImportError:
                # Fallback if gurobipy not available
                results = solver.solve(model, tee=True)


            
            # If infeasible, use Gurobi's IIS analysis
            if (results.solver.termination_condition == pyo.TerminationCondition.infeasible):
                print("\n=== GUROBI INFEASIBILITY ANALYSIS ===")
                print("Computing Irreducible Inconsistent Subsystem (IIS)...")
                
                try:
                    # Access the Gurobi model directly for IIS
                    gurobi_model = solver._solver_model
                    gurobi_model.computeIIS()
                    
                    print("\nInfeasible constraints:")
                    for c in gurobi_model.getConstrs():
                        if c.IISConstr:
                            print(f"  - {c.ConstrName}")
                    
                    print("\nInfeasible bounds:")
                    for v in gurobi_model.getVars():
                        if v.IISLB:
                            print(f"  - {v.VarName} lower bound")
                        if v.IISUB:
                            print(f"  - {v.VarName} upper bound")
                    
                    # Write IIS to file
                    gurobi_model.write("infeasible_model.ilp")
                    print("\n✅ IIS written to 'infeasible_model.ilp'")
                    
                except Exception as e:
                    print(f"❌ Could not compute IIS: {e}")
                    print("This may happen if using Gurobi through Pyomo interface")
                
                return False
            
            print(f"\n=== SOLVER RESULTS ===")
            print(f"Solver status: {results.solver.status}")
            print(f"Termination condition: {results.solver.termination_condition}")
            
            # Check if solution was found
            if (results.solver.termination_condition == pyo.TerminationCondition.optimal or 
                results.solver.termination_condition == pyo.TerminationCondition.feasible or
                results.solver.termination_condition == pyo.TerminationCondition.maxTimeLimit):
                
                print(f"Final objective value: {pyo.value(model.objective):.4f}")
                
                # Print individual objective component values (before weighting)
                print(f"\n=== INDIVIDUAL OBJECTIVE COMPONENTS (PRE-WEIGHTED) ===")
                
                try:
                    # Calculate individual components using the same functions
                    effort_value = pyo.value(effort_objective(model))
                    balancing_penalty_value = pyo.value(balancing_penalty(model))
                    skill_penalty_value = pyo.value(skill_penalty(model))
                    time_block_penalty_value = pyo.value(time_block_penalty(model))
                    skill_combination_value = pyo.value(skill_combination_bonus(model))
                    
                    print(f"Effort Objective (scaled to baseline {TARGET_BASELINE}): {effort_value:.4f}")
                    print(f"Hour Balancing Penalty (scaled to baseline {TARGET_BASELINE}): {balancing_penalty_value:.4f}")
                    print(f"Low Skill Penalty (scaled to baseline {TARGET_BASELINE}): {skill_penalty_value:.4f}")
                    print(f"Shift Block Penalty (scaled to baseline {TARGET_BASELINE}): {time_block_penalty_value:.4f}")
                    print(f"Skill Combination Bonus (scaled to baseline {TARGET_BASELINE}): {skill_combination_value:.4f}")
                    
                    print(f"\n=== SCALING ANALYSIS ===")
                    print(f"Target Baseline: {TARGET_BASELINE}")
                    print(f"Range when weights=1.0: {min(effort_value, balancing_penalty_value, skill_penalty_value, time_block_penalty_value, skill_combination_value):.3f} - {max(effort_value, balancing_penalty_value, skill_penalty_value, time_block_penalty_value, skill_combination_value):.3f}")
                    ratio = max(effort_value, balancing_penalty_value, skill_penalty_value, time_block_penalty_value, skill_combination_value) / min(effort_value, balancing_penalty_value, skill_penalty_value, time_block_penalty_value, skill_combination_value) if min(effort_value, balancing_penalty_value, skill_penalty_value, time_block_penalty_value, skill_combination_value) > 0 else float('inf')
                    print(f"Max/Min Ratio: {ratio:.2f}x (lower is better for balanced scaling)")
                    
                    print(f"\n=== NORMALIZATION FACTORS USED ===")
                    print(f"Effort Normalizer: {EFFORT_NORMALIZER:.3f}")
                    print(f"Balancing Normalizer: {BALANCING_NORMALIZER:.3f}")
                    print(f"Skill Normalizer: {SKILL_NORMALIZER:.3f}")
                    print(f"Time Block Normalizer: {TB_NORMALIZER:.3f}")
                    print(f"Skill Combo Normalizer: {COMBO_NORMALIZER:.3f}")
                    
                    print(f"\n=== WEIGHTED OBJECTIVE COMPONENTS ===")
                    print(f"Effort Objective × {self.weight_effort_bonus} = {effort_value * self.weight_effort_bonus:.4f}")
                    print(f"Hour Balancing Penalty × {self.weight_hour_balancing} = {-balancing_penalty_value * self.weight_hour_balancing:.4f}")
                    print(f"Low Skill Penalty × {self.weight_low_skill_penalty} = {-skill_penalty_value * self.weight_low_skill_penalty:.4f}")
                    print(f"Shift Block Penalty × {self.weight_shift_block_penalty} = {-time_block_penalty_value * self.weight_shift_block_penalty:.4f}")
                    print(f"Skill Combination Bonus × {self.weight_skill_combo} = {skill_combination_value * self.weight_skill_combo:.4f}")
                    
                    # Verify the calculation
                    calculated_objective = (
                        self.weight_effort_bonus * effort_value -
                        self.weight_hour_balancing * balancing_penalty_value -
                        self.weight_low_skill_penalty * skill_penalty_value -
                        self.weight_shift_block_penalty * time_block_penalty_value +
                        self.weight_skill_combo * skill_combination_value
                    )
                    print(f"\nCalculated total: {calculated_objective:.4f}")
                    print(f"Solver reported: {pyo.value(model.objective):.4f}")
                    
                except Exception as e:
                    print(f"❌ Could not calculate individual objective values: {e}")
                
                # Process solution and assign refs to games
                def _process_solution_local(model, get_game_info):
                    """Process the optimization solution and assign refs to games (local version)"""
                    print("\n=== PROCESSING SOLUTION ===")
                    
                    # Clear all existing optimized assignments
                    for ref in self.refs:
                        ref.clear_optimized_games()
                    for game in self.games:
                        game.set_refs([])  # Clear existing assignments
                    
                    assignments = []
                    total_assignments = 0
                    
                    # Go through all decision variables and find assignments (x[r,d,h,g] = 1)
                    for r in model.R:
                        for d in model.D:
                            for h in model.H:
                                for g in model.G:
                                    if pyo.value(model.x[r, d, h, g]) > 0.5:  # Binary variable = 1
                                        # Get the actual game object
                                        game = get_game_info(d, h, g)
                                        if game:
                                            ref = self.refs[r]
                                            
                                            # Assign ref to game and game to ref
                                            game.add_ref(ref)
                                            ref.add_optimized_game(game)
                                            
                                            assignments.append({
                                                'ref_name': ref.get_name(),
                                                'game_number': game.get_number(),
                                                'day': game.get_date(),
                                                'time': game.get_time(),
                                                'location': game.get_location(),
                                                'difficulty': game.get_difficulty()
                                            })
                                            total_assignments += 1
                    
                    # Print optimization metrics
                    print("\n=== OPTIMIZATION METRICS ===")
                    ref_hours = {}
                    for ref in self.refs:
                        ref_hours[ref.get_name()] = len(ref.get_optimized_games())
                    
                    if ref_hours:
                        avg_hours = sum(ref_hours.values()) / len(ref_hours)
                        max_hours = max(ref_hours.values())
                        min_hours = min(ref_hours.values())
                        print(f"Average hours per ref: {avg_hours:.2f}")
                        print(f"Hours range: {min_hours} - {max_hours}")
                        
                        # Show hour distribution
                        print("\nHour distribution:")
                        for ref_name, hours in sorted(ref_hours.items(), key=lambda x: x[1], reverse=True):
                            print(f"  {ref_name}: {hours} hours")
                    
                    print("\n=== SOLUTION PROCESSING COMPLETE ===")
                    
                    return assignments

                assignments = _process_solution_local(model, get_game_info)
                # Optionally: Save assignments to a file for further analysis
                
                # Return the updated referee objects and assignments for dashboard integration
                return {'success': True, 'refs': self.refs, 'assignments': assignments}
            else:
                print("❌ No optimal solution found!")
                print("Check constraints - model may be infeasible")
                return {'success': False, 'error': 'No optimal solution found'}
                
        except Exception as e:
            print(f"❌ Solver error: {e}")
            return {'success': False, 'error': str(e)}
    
    
    
