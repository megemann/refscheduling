class Ref:
    def __init__(self, name, availability): #define max games 
        self.name = name
        self.availability = availability # dict, key is time slot
        self.games = []

    def is_available(self, game):
        time_slot = game.get_time_slot()
        
        if not self.availability.get(time_slot, False):
            return False
        
        # Check if ref already has a game at this time
        for existing_game in self.games:
            if existing_game.get_time_slot() == game.get_time_slot():
                return False
        
        return True
    
    def total_slots_left(self):
        return sum(self.availability.values()) - len(self.games)
    
    def get_games_scheduled(self):
        return len(self.games)

    
    def add_game(self, game):
        if self.is_available(game):
            self.games.append(game)
        else:
            raise Exception("Ref is not available for this game")
        
    def __str__(self):
        return f"Ref: {self.name}, Games: {self.games}"
        