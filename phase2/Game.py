class Game:
    def __init__(self, date, time, number, difficulty, location, min_refs=1, max_refs=2):
        self.__date = date
        self.__time = time
        self.__number = number
        self.__difficulty = difficulty  # Maps to a division type
        self.__refs = []  # List of assigned referees
        self.__location = location
        self.__min_refs = min_refs
        self.__max_refs = max_refs

    def get_date(self):
        return self.__date

    def set_date(self, date):
        self.__date = date

    def get_time(self):
        return self.__time

    def set_time(self, time):
        self.__time = time

    def get_number(self):
        return self.__number

    def set_number(self, number):
        self.__number = number

    def get_difficulty(self):
        return self.__difficulty

    def set_difficulty(self, difficulty):
        self.__difficulty = difficulty

    def get_refs(self):
        return self.__refs

    def set_refs(self, refs):
        self.__refs = refs if refs is not None else []

    def add_ref(self, ref):
        """Add a referee to this game"""
        if ref not in self.__refs:
            self.__refs.append(ref)

    def remove_ref(self, ref):
        """Remove a referee from this game"""
        if ref in self.__refs:
            self.__refs.remove(ref)

    def get_location(self):
        return self.__location

    def set_location(self, location):
        self.__location = location

    def get_min_refs(self):
        return self.__min_refs

    def set_min_refs(self, min_refs):
        self.__min_refs = max(0, min_refs)  # Ensure non-negative

    def get_max_refs(self):
        return self.__max_refs

    def set_max_refs(self, max_refs):
        self.__max_refs = max(1, max_refs)  # Ensure at least 1

    def is_fully_staffed(self):
        """Check if game has enough referees (at least min_refs)"""
        return len(self.__refs) >= self.__min_refs

    def is_overstaffed(self):
        """Check if game has too many referees (more than max_refs)"""
        return len(self.__refs) > self.__max_refs

    def can_add_ref(self):
        """Check if another referee can be added to this game"""
        return len(self.__refs) < self.__max_refs

    def get_ref_count(self):
        """Get current number of assigned referees"""
        return len(self.__refs)

    def __str__(self):
        ref_names = [str(ref) for ref in self.__refs] if self.__refs else ["No refs assigned"]
        return f"Game {self.__number}: {self.__date} at {self.__time}, {self.__location}, Difficulty: {self.__difficulty}, Refs: {', '.join(ref_names)} ({len(self.__refs)}/{self.__min_refs}-{self.__max_refs})"

    def __repr__(self):
        return f"Game(date='{self.__date}', time='{self.__time}', number={self.__number}, difficulty={self.__difficulty}, location='{self.__location}', min_refs={self.__min_refs}, max_refs={self.__max_refs}, refs={len(self.__refs)})"
