class Game:
    def __init__(self, id, date, time): #need to add league
        self.id = id
        self.date = date
        self.time = time
        self.refs = []  # array of type refs

    def is_full(self):
        return len(self.refs) >= 3
    
    def can_be_played(self, ref):
        return len(self.refs) > 1
    
    def add_ref(self, ref):
        if not self.is_full():
            self.refs.append(ref)
        else:
            raise Exception("Game is full")
    
    def get_time_slot(self):
        return f"{self.date}_{self.time}"
    
    def get_refs(self):
        return self.refs

    def __str__(self):
        return f"Game: {self.id}, Date: {self.date}, Time: {self.time}, Refs: {self.refs}"
    
