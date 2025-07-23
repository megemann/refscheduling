import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DATA.load_availability import load_availability_csv

from Ref import Ref
from Game import Game

from math import floor

from display_schedule import display_by_ref, display_by_game
from schedule_to_excel import schedule_to_excel

def __main__():
    
    # Load availability data from CSV
    csv_path = 'C:/Users/16073/refscheduling/DATA/phase1/BB2025Phase1Convert.csv'
    availability = load_availability_csv(csv_path)

    games = define_games(availability)  # Set breakpoint here
    refs = define_refs(availability)

    print(games[0])
    print(refs[0])

    run_balanced_greedy(games, refs)

    display_by_ref(refs)
    display_by_game(games)

    schedule_to_excel(refs)

def run_balanced_greedy(games, refs):
    """
    Run Greedy based on selecting the ref with the fewest games scheduled
    Args:
        games: list of games
        refs: list of refs
    Returns:
        None

    If ref has games under balanced games threshold, add all refs to their games
    Ensure that each game is full by scheduling all refs to the game if there are the min refs available to work the game
    Select each ref by the fewest games available as a tie breaker
    """

    unfilled_games = [game for game in games]
    compatible_refs = [ref for ref in refs]

    # Get availability numbers by day
    availablity_by_day = {}
    for ref in refs:
        for day in ref.availability.keys():
            if ref.availability[day]:
                if day not in availablity_by_day:
                    availablity_by_day[day] = 0
                availablity_by_day[day] += 1

    refs_left_at_time = {}
    for game in games:
        time_slot = game.get_time_slot()
        if time_slot not in refs_left_at_time:
            refs_left_at_time[time_slot] = 12

    def add_ref_to_game(game, ref, unfilled_games, refs_left_at_time, availablity_by_day):
        'Handle all the logic of adding a ref to a game'
        #add game to the ref
        ref.add_game(game)

        #add ref to the game, and if its full, remove it from the list of unfilled games
        game.add_ref(ref)
        if game.is_full():
            unfilled_games.remove(game)

        #update the refs left at time and availability by day
        refs_left_at_time[game.get_time_slot()] -= 1
        if refs_left_at_time[game.get_time_slot()] == 0:
            del refs_left_at_time[game.get_time_slot()]

        availablity_by_day[game.get_time_slot()] -= 1
        if availablity_by_day[game.get_time_slot()] == 0:
            del availablity_by_day[game.get_time_slot()]

    # If ref has less or equal to availibility than a certain threshold, add all refs to their games
    balanced_games_threshold = floor(len(games) / 12) # Made off of observations. We can change this to an estimation
    for ref in compatible_refs:
        if ref.total_slots_left() <= balanced_games_threshold: #at the beginning, so if refs has less than 5 games of availbilty
            for game in unfilled_games:
                if ref.is_available(game):
                    add_ref_to_game(game, ref, unfilled_games, refs_left_at_time, availablity_by_day)

    while len(unfilled_games) > 0:
        # If any game has only min refs available to work the game, schedule all refs to the game
        for key in refs_left_at_time.keys():
            if refs_left_at_time[key] == availablity_by_day[key]:
                for ref in compatible_refs:
                    if ref.is_available(game):
                        add_ref_to_game(game, ref, unfilled_games, refs_left_at_time, availablity_by_day)
                        
        # Find list of refs with the fewest games scheduled
        min_num_games = min(ref.get_games_scheduled() for ref in compatible_refs)
        min_refs = [ref for ref in compatible_refs if ref.get_games_scheduled() == min_num_games]
        if len(min_refs) == 1:
            min_ref = min_refs[0]
        else:
            # Find the ref with the least total availability remaining
            min_ref = min(min_refs, key=lambda ref: ref.total_slots_left())

        #find the game with the least refs available to work the game, that min_ref is available to work
        available_games = []
        for game in unfilled_games:
            if min_ref.is_available(game):
                available_games.append(game)

        if len(available_games) == 0:
            #remove the ref from the list of compatible refs
            compatible_refs.remove(min_ref)
            continue

        # Find the time slot with the least availability
        unfilled_time_slots = {game.get_time_slot() for game in available_games}
        min_availability_time = min(unfilled_time_slots, key=lambda slot: availablity_by_day.get(slot, 0))
        min_game = next(game for game in unfilled_games if game.get_time_slot() == min_availability_time)

        add_ref_to_game(min_game, min_ref, unfilled_games, refs_left_at_time, availablity_by_day)





def run_availability_greedy(games, refs):
    """
    Run Greedy algorithm based on least availability per game
    Args:
        games: list of games
        refs: list of refs
    Returns:
        None

    Guarantees termination as long as there are at least 12 available refs at all times.
    - No time limits or hours balancing, simply selects the ref with the least availability remaining to rbreak tie
    """
    
    unfilled_games = games

    # Get availability numbers by day
    availibility_by_day = {}
    for ref in refs:
        for day in ref.availability.keys():
            if ref.availability[day]:
                if day not in availibility_by_day:
                    availibility_by_day[day] = 0
                availibility_by_day[day] += 1

    # While there are unfilled games
    while len(unfilled_games) > 0: 

        # Find the time slot with the least availability
        unfilled_time_slots = {game.get_time_slot() for game in unfilled_games}
        min_availability_time = min(unfilled_time_slots, key=lambda slot: availibility_by_day.get(slot, 0))
        min_game = next(game for game in unfilled_games if game.get_time_slot() == min_availability_time)
        
        # Find the refs that are available to work the game
        availibile_refs = []
        for ref in refs:
            if ref.is_available(min_game):
                availibile_refs.append(ref)

        # Find the ref with the least total availability remaining
        min_ref = min(availibile_refs, key=lambda ref: ref.total_slots_left())

        # Add the game to the ref
        min_ref.add_game(min_game)

        # Add the ref to the game
        min_game.add_ref(min_ref)

        # If the game is full, remove it from the list of unfilled games
        if min_game.is_full():
            unfilled_games.remove(min_game)

        # Update the availability by day
        availibility_by_day[min_game.get_time_slot()] -= 1
        if availibility_by_day[min_game.get_time_slot()] == 0:
            del availibility_by_day[min_game.get_time_slot()]


def define_games(availability):
    
    # Generate games array with 4 games per time slot
    games = []

    # Get time slots from the availability data (using first ref as reference)
    first_ref_schedule = list(availability.values())[0]
    time_slots = list(first_ref_schedule.keys())

    # Create 4 games for each time slot
    game_id = 1
    for time_slot in time_slots:
        # Parse the time slot format "Day_Time" (e.g., "Monday_6:30")
        day, time = time_slot.split('_')
        
        for game_num in range(1, 5):  # Create 4 games per time slot
            game = Game(game_id, day, time)
            games.append(game)
            game_id += 1

    return games

def define_refs(availability):
    # Print the dictionary
    refs = []

    for ref, schedule in availability.items():
        refs.append(Ref(ref, schedule))

    return refs

if __name__ == "__main__":
    __main__()



