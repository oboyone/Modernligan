import math
import yaml
import email
from bs4 import BeautifulSoup
from pathlib import Path
import quopri
import pprint
import os
from glicko2 import Glicko2, WIN, LOSS, DRAW, Glicko_Rating, MU, PHI, SIGMA, TAU

list_of_forbidden_chars = []
yaml.Dumper.ignore_aliases = lambda *args : True

class leaderboards(object):
    def __init__(self):
        self.elo_leaderboard = {}
        self.glicko_leaderboard = {}
        self.modern_ligan_leaderboard = {}
        self.total_matches_leaderboard = {}
        self.total_events_leaderboard = {}
        self.total_draws_leaderboard = {}
        self.event_completed_percentage_leaderboard = {}
        self.game_win_rate_leaderboard = {}
        self.match_win_rate_leaderboard = {}
        self.undefeated_records_leaderboard = {}
        self.undefeated_records_percentage_leaderboard = {}
        self.bye_leaderboard = {}
    def add_player(self, player):
        self.elo_leaderboard[player] = 0
        self.glicko_leaderboard[player] = 0
        self.modern_ligan_leaderboard[player] = 0
        self.total_matches_leaderboard[player] = 0
        self.total_events_leaderboard[player] = 0
        self.total_draws_leaderboard[player] = 0
        self.event_completed_percentage_leaderboard[player] = 0
        self.game_win_rate_leaderboard[player] = 0
        self.match_win_rate_leaderboard[player] = 0
        self.undefeated_records_leaderboard[player] = 0
        self.undefeated_records_percentage_leaderboard[player] = 0
    def update_player(self, player, elo_rating, glicko_rating, modern_ligan_rating, undefeated_records, total_matches_played, total_events_played, total_draws, event_completed_percentage, game_win_rate, match_win_rate, total_byes):
        self.elo_leaderboard[player] = elo_rating
        self.glicko_leaderboard[player] = glicko_rating
        self.modern_ligan_leaderboard[player] = modern_ligan_rating
        self.total_matches_leaderboard[player] = total_matches_played
        self.total_events_leaderboard[player] = total_events_played
        self.total_draws_leaderboard[player] = total_draws
        self.event_completed_percentage_leaderboard[player] = event_completed_percentage
        self.game_win_rate_leaderboard[player] = game_win_rate
        self.match_win_rate_leaderboard[player] = match_win_rate
        self.undefeated_records_leaderboard[player] = undefeated_records
        self.undefeated_records_percentage_leaderboard[player] = (undefeated_records / total_events_played) * 100
        self.bye_leaderboard[player] = total_byes

class Player(object):
    def __init__(self, glicko_rating=None):
        self.name = ''
        self.dates_played = {}
        self.draw_counter = 0
        self.elo_rating = 1500
        self.game_win_rate = 0.0
        self.glicko_rating = glicko_rating if glicko_rating else Glicko2().create_rating()
#        self.glicko_rating = 1500
#        self.glicko_rd = 350
#        self.glicko_vol = 0.06
        self.match_win_rate = 0.0
        self.matches_lost_against = {}
        self.matches_won_against = {}
        self.undefeated_records = 0
        self.modern_ligan_rating = 0
        self.modern_ligan_dates_played = {}
        self.modern_ligan_results = []
        self.total_games_played = 0
        self.total_games_won = 0
        self.total_games_lost = 0
        self.total_matches_played = 0
        self.total_matches_won = 0
        self.total_matches_lost = 0
        self.total_byes = 0
        self.event_completed_percentage = 0.0
        self.undefeated_records_percentage = 0.0
        self.drop_rate = 0.0
    def add_date(self, event_date=''):
        if event_date not in self.dates_played:
            self.dates_played[event_date] = {'won': 0, 'lost': 0, 'drawn': 0, 'played_percentage': 0, 'byes': 0, 'games_won': 0, 'games_lost': 0, 'games_played': 0}

    def add_match(self, event_date='', won=0, lost=0, drawn=0, games_won=0, games_lost=0, byes=0):
        self.dates_played[event_date]['played_percentage'] += 0.25
        self.dates_played[event_date]['games_played'] += games_won + games_lost
        self.dates_played[event_date]['games_won'] += games_won
        self.dates_played[event_date]['games_lost'] += games_lost
        self.dates_played[event_date]['byes'] += byes
        self.dates_played[event_date]['won'] += won
        self.dates_played[event_date]['lost'] += lost
        self.dates_played[event_date]['drawn'] += drawn


    def calculate_new_elo(self, player_rating, opponent_rating, outcome):
        self.elo_rating = calculate_elo_rating(player_rating, opponent_rating, outcome)
    def update_glicko_rating(self, series):
        glicko = Glicko2()
        #print(self.glicko_rating.__repr__(self))
        self.glicko_rating = glicko.rate(self.glicko_rating, series)
#    def calculate_new_glicko(self, player1, player2, outcome):
#        self.glicko_rating, self.glicko_rd, self.glicko_vol = glicko_update(player1.glicko_rating, player1.glicko_rd, player1.glicko_vol, player2.glicko_rating, player2.glicko_rd, outcome)
    def calculate_points(self):
        for event_date in self.dates_played.keys():
            self.total_games_played += self.dates_played.get(event_date)['games_played']
            self.total_games_won += self.dates_played.get(event_date)['games_won']
            self.total_games_lost += self.dates_played.get(event_date)['games_lost']
            self.total_matches_played += self.dates_played.get(event_date).get('won') + self.dates_played.get(event_date).get('drawn') + self.dates_played.get(event_date).get('lost')
            self.draw_counter += self.dates_played.get(event_date).get('drawn')
            self.total_matches_won += self.dates_played.get(event_date)['won']
            self.total_matches_lost += self.dates_played.get(event_date)['lost']
            self.total_byes += self.dates_played.get(event_date)['byes']
            if event_date in self.modern_ligan_dates_played:
                self.modern_ligan_results.append(self.modern_ligan_dates_played.get(event_date).get('won', 0) * 3 + self.modern_ligan_dates_played.get(event_date).get('drawn', 0) * 1)
        self.match_win_rate = self.total_matches_won / self.total_matches_played * 100
        self.game_win_rate = self.total_games_won / self.total_games_played * 100
        self.total_events_played = len(self.dates_played)
        self.modern_ligan_rating = sum(sorted(self.modern_ligan_results, reverse=True)[:8])
        self.event_completed_percentage = (self.total_matches_played / (self.total_events_played * 4)) * 100
        self.undefeated_records_percentage = self.undefeated_records / self.total_events_played * 100
        self.drop_rate = 1 - (((self.total_matches_won + self.total_matches_lost + self.draw_counter + self.total_byes) / 4)/len(self.dates_played))

"""def glicko_update(player_rating, player_rd, player_volatility, opponent_rating, opponent_rd, outcome):
    INITIAL_RATING = 1500
    INITIAL_RD = 100
    INITIAL_VOLATILITY = 0.03
    TAU = 1.0
    EPSILON = 0.000001
    def g(rating, rd, volatility):
        return 1 / (math.sqrt(1 + 3 * (volatility ** 2) * (rd ** 2) / (math.pi ** 2)))
    def E(player_rating, opponent_rating, opponent_rd):
        return 1 / (1 + math.exp(-g(opponent_rating, opponent_rd, INITIAL_VOLATILITY) * (player_rating - opponent_rating)))

    def calculate_new_rd(rd, volatility, phi, v_squared, delta_squared):
        a = math.log(volatility ** 2)
        def f(x):
            return (math.exp(x) * (delta_squared - phi ** 2 - v_squared - math.exp(x))) / (2 * (phi ** 2 + v_squared + math.exp(x)) ** 2) - (x - a) / (TAU ** 2)
        A = a
        if delta_squared > phi ** 2 + v_squared:
            B = math.log(delta_squared - phi ** 2 - v_squared)
        else:
            k = 1
            while f(a - k * math.sqrt(TAU ** 2)) < 0:
                k += 1
            B = a - k * math.sqrt(TAU ** 2)
        f_A = f(A)
        f_B = f(B)
        while abs(B - A) > EPSILON:
            C = A + (A - B) * f_A / (f_B - f_A)
            f_C = f(C)
            if f_C * f_B < 0:
                A = B
                f_A = f_B
            else:
                f_A = f_A / 2
            B = C
            f_B = f_C
        return math.exp(A / 2)

    # Step 1: Convert rating and RD to Glicko-2 scale
    phi = g(player_rating, player_rd, player_volatility)
    
    # Step 2: Compute the estimated variance of the player's rating based only on game outcomes
    v_squared = 1 / (g(opponent_rating, opponent_rd, INITIAL_VOLATILITY) ** 2)
    delta = phi ** 2 * v_squared * g(player_rating, player_rd, player_volatility) * (outcome - E(player_rating, opponent_rating, opponent_rd))
    v_squared_inv = 1 / (phi ** 2 + v_squared)
    delta_squared = delta ** 2
    
    # Step 3: Determine new volatility
    new_volatility = calculate_new_rd(player_rd, player_volatility, phi, v_squared, delta_squared)
    
    # Step 4: Update rating and RD
    new_phi = math.sqrt(phi ** 2 + new_volatility ** 2)
    new_rd = 1 / math.sqrt(v_squared_inv + (1 / new_phi ** 2))
    new_rating = player_rating + (new_rd ** 2) * v_squared_inv * (outcome - E(player_rating, opponent_rating, opponent_rd))
    
    return new_rating, new_rd, new_volatility
"""
def import_scores_round(html_file_name):
    """
    Given the name of an HTML file, this function reads the file and extracts match-up and score information.
    The function takes a single parameter:
    - html_file_name (str): The name of the HTML file to be read.
    
    The function returns a list of dictionaries, where each dictionary represents a match-up between two players.
    Each dictionary contains the following keys:
    - player_one (str): The name of the first player in the match-up.
    - player_two (str): The name of the second player in the match-up.
    - player_one_games_won (int): The number of games won by player_one in the match-up.
    - player_two_games_won (int): The number of games won by player_two in the match-up.
    
    If the HTML file has a .mhtml extension, the function reads the file as an email message and extracts the HTML content.
    If the HTML file has a .html extension, the function reads the file directly as HTML content.
    
    If the HTML file does not have either of the expected extensions, the function raises an Exception with the message 'Error'.
    """
    match_up_list = []
    score_list = []
    if str(html_file_name).endswith('.mhtml'):
        with open(html_file_name, "r", encoding='utf-8') as file:
            message = email.message_from_file(file)
            for part in message.walk():
                if (part.get_content_type() == "text/html"):
                    decoded_content = quopri.decodestring(part.get_payload())
                    soup = BeautifulSoup(decoded_content, 'html.parser')
                    #print(soup)
                    #parsed_data = soup.prettify()
                    players = soup.find_all("span", class_=["team__text no-penalties-text", "dropped"])
                    matches = soup.find_all("div", class_="match-result")
                    for i in range(0, len(players), 2):
                        if i + 1 < len(players):
                            pair = {'player_one': ' '.join(players[i].find_all("span")[0].text.strip().split()), 'player_two': ' '.join(players[i + 1].find_all("span")[0].text.strip().split()), }
                            for character in pair['player_one']:
                                if character.isalpha() == False and character != ' ':
                                    list_of_forbidden_chars.append(character)
                            for character in pair['player_two']:
                                if character.isalpha() == False and character != ' ':
                                    list_of_forbidden_chars.append(character)
                            for character in list_of_forbidden_chars:
                                pair['player_one'] = pair['player_one'].replace(character, '')
                                pair['player_two'] = pair['player_two'].replace(character, '')
                            if pair['player_one'] == 'f h':
                                pair['player_one'] = 'Felix Johansson'
                            if pair['player_two'] == 'f h':
                                pair['player_two'] = 'Felix Johansson'
                            if pair['player_one'].endswith(' '):
                                pair['player_one'] = pair['player_one'][:-1]
                            if pair['player_two'].endswith(' '):
                                pair['player_two'] = pair['player_two'][:-1]
                            if pair['player_one'].startswith(' '):
                                pair['player_one'] = pair['player_one'][1:]
                            if pair['player_two'].startswith(' '):
                                pair['player_two'] = pair['player_two'][1:]
                            match_up_list.append(pair)
                    for match in matches:
                        score1 = int(match.find_all("div", class_="box-score")[0].text.strip())
                        score2 = int(match.find_all("div", class_="box-score")[1].text.strip())
                        score_list.append({'player_one_games_won': score1, 'player_two_games_won': score2,})
        
                    for i in range(0, len(match_up_list)):
                        match_up_list[i]['player_one_games_won'] = score_list[i]['player_one_games_won']
                        match_up_list[i]['player_two_games_won'] = score_list[i]['player_two_games_won']
    elif str(html_file_name).endswith('.html'):
        with open(html_file_name, "r", encoding='utf-8') as file:
            html_content = file.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            players = soup.find_all("span", class_=["team__text no-penalties-text", "dropped"])
            matches = soup.find_all("div", class_="match-result")
            for i in range(0, len(players), 2):
                if i + 1 < len(players):
                    pair = {'player_one': players[i].find_all("span")[0].text.strip(), 'player_two': players[i + 1].find_all("span")[0].text.strip(), }
                    for character in list_of_forbidden_chars:
                        pair['player_one'] = pair['player_one'].replace(character, '')
                        pair['player_one'] = pair['player_one'].replace('  ', ' ')
                        pair['player_two'] = pair['player_two'].replace(character, '')
                        pair['player_two'] = pair['player_two'].replace('  ', ' ')
                    match_up_list.append(pair)
            for match in matches:
                score1 = int(match.find_all("div", class_="box-score")[0].text.strip())
                score2 = int(match.find_all("div", class_="box-score")[1].text.strip())
                score_list.append({'player_one_games_won': score1, 'player_two_games_won': score2,})
            
            for i in range(0, len(match_up_list)):
                match_up_list[i]['player_one_games_won'] = score_list[i]['player_one_games_won']
                match_up_list[i]['player_two_games_won'] = score_list[i]['player_two_games_won']
    else:
        raise Exception('Error, unknown file type!, only .mhtml and .html files are supported')
    return match_up_list

def calculate_elo_rating(player_rating, opponent_rating, outcome):
    """
    Calculate the new Elo rating for a player based on the outcome of a match

    :param player_rating: Elo rating of the player
    :param opponent_rating: Elo rating of the opponent
    :param outcome: The outcome of the match (1 for win, 0 for loss)
    :return: The new Elo rating for the player
    """
    # Calculate the expected score based on player and opponent ratings
    expected_score = 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))
    
    # Calculate the new rating based on the outcome and the expected score
    # The K-factor (32 in this case) determines how much the rating changes after each match
    new_rating = player_rating + 32 * (outcome - expected_score)
    
    return new_rating

def import_events(list_of_dates):
    """
    Imports event data from a list of dates.

    Args:
        list_of_dates (List[str]): A list of dates.

    Returns:
        dict: A dictionary containing the event data.
    """
    # Dictionary to store the event data
    events_dict = {}
    
    # Loop through each date in the list
    for dates in list_of_dates:
        # Initialize a list to store the event data for each date
        event_data = []
        
        # Get the folder path for the date
        folder_path = Path(dates)
        
        # Loop through each file in the folder
        for file_path in folder_path.iterdir():
            # Check if the file is a regular file
            if file_path.is_file():
                # Import the scores for a round
                round_data = import_scores_round(file_path)
                
                # Add the round data to the event data list
                event_data.append(round_data)
        
        # Add the event data to the events dictionary, using the date as the key
        events_dict[dates] = event_data
    
    # Return the events dictionary
    return events_dict

def calculate_stats_in_data(events_data_dict, players_dict):
    for date, rounds in events_data_dict.items():
        round_number = 0
        for round in rounds:
            round_number = round_number + 1
            for match in round:
                player1 = match.get('player_one').title()
                player2 = match.get('player_two').title()
                if player1 not in players_dict:
                    players_dict[player1] = Player()
                    players_dict[player1].name = player1
                if player2 not in players_dict:
                    players_dict[player2] = Player()
                    players_dict[player2].name = player2
                if date not in players_dict[player1].__dict__['dates_played']:
                    players_dict[player1].add_date(date)
                if date not in players_dict[player2].__dict__['dates_played']:
                    players_dict[player2].add_date(date)
                if match.get('player_one_games_won') > match.get('player_two_games_won'):
                    players_dict[player1].calculate_new_elo(players_dict[player1].elo_rating, players_dict[player2].elo_rating, 1)
                    players_dict[player2].calculate_new_elo(players_dict[player2].elo_rating, players_dict[player1].elo_rating, 0)
                    players_dict[player1].update_glicko_rating([(WIN, players_dict[player2].glicko_rating)])
                    players_dict[player2].update_glicko_rating([(LOSS, players_dict[player1].glicko_rating)])
                    #players_dict[player1].calculate_new_glicko(players_dict[player1], players_dict[player2], 1)
                    #players_dict[player2].calculate_new_glicko(players_dict[player2], players_dict[player1], 0)
                    players_dict[player1].add_match(date, 1, 0, 0, match.get('player_one_games_won'), match.get('player_two_games_won'), byes=0 )
                    players_dict[player2].add_match(date, 0, 1, 0, match.get('player_two_games_won'), match.get('player_one_games_won'), byes=0 )
                    players_dict[player1].matches_won_against[players_dict[player2].name] = players_dict[player1].matches_won_against.get(players_dict[player2].name, 0) + 1
                    players_dict[player2].matches_lost_against[players_dict[player1].name] = players_dict[player2].matches_lost_against.get(players_dict[player1].name, 0) + 1
                elif match.get('player_one_games_won') < match.get('player_two_games_won'):
                    players_dict[player1].calculate_new_elo(players_dict[player1].elo_rating, players_dict[player2].elo_rating, 0)
                    players_dict[player2].calculate_new_elo(players_dict[player2].elo_rating, players_dict[player1].elo_rating, 1)
                    players_dict[player1].update_glicko_rating([(LOSS, players_dict[player2].glicko_rating)])
                    players_dict[player2].update_glicko_rating([(WIN, players_dict[player1].glicko_rating)])
                    #players_dict[player1].calculate_new_glicko(players_dict[player1], players_dict[player2], 0)
                    #players_dict[player2].calculate_new_glicko(players_dict[player2], players_dict[player1], 1)
                    players_dict[player1].add_match(date, 0, 1, 0, match.get('player_one_games_won'), match.get('player_two_games_won'), byes=0 )
                    players_dict[player2].add_match(date, 1, 0, 0, match.get('player_two_games_won'), match.get('player_one_games_won'), byes=0 )
                    players_dict[player1].matches_lost_against[players_dict[player2].name] = players_dict[player1].matches_lost_against.get(players_dict[player2].name, 0) + 1
                    players_dict[player2].matches_won_against[players_dict[player1].name] = players_dict[player2].matches_won_against.get(players_dict[player1].name, 0) + 1
                elif match.get('player_one_games_won') == match.get('player_two_games_won'):
                    players_dict[player1].calculate_new_elo(players_dict[player1].elo_rating, players_dict[player2].elo_rating, 0.5)
                    players_dict[player2].calculate_new_elo(players_dict[player2].elo_rating, players_dict[player1].elo_rating, 0.5)
                    players_dict[player1].update_glicko_rating([(DRAW, players_dict[player2].glicko_rating)])
                    players_dict[player2].update_glicko_rating([(DRAW, players_dict[player1].glicko_rating)])
                    #players_dict[player1].calculate_new_glicko(players_dict[player1], players_dict[player2], 0.5)
                    #players_dict[player2].calculate_new_glicko(players_dict[player2], players_dict[player1], 0.5)
                    players_dict[player1].add_match(date, 0, 0, 1, match.get('player_one_games_won'), match.get('player_two_games_won'), byes=0 )
                    players_dict[player2].add_match(date, 0, 0, 1, match.get('player_two_games_won'), match.get('player_one_games_won'), byes=0 )
                else:
                    raise Exception('Error, unknown match result!')
                if round_number == 4:
                    if players_dict[player1].dates_played[date]['won'] + players_dict[player1].dates_played[date]['lost'] + players_dict[player1].dates_played[date]['drawn'] != 4:
                        players_dict[player1].dates_played[date]['byes'] = 1
                    if players_dict[player2].dates_played[date]['won'] + players_dict[player2].dates_played[date]['lost'] + players_dict[player2].dates_played[date]['drawn'] != 4:
                        players_dict[player2].dates_played[date]['byes'] = 1
                    if players_dict[player1].dates_played[date]['lost'] == 0 and players_dict[player1].dates_played[date]['drawn'] == 0:
                        players_dict[player1].undefeated_records += 1
                    if players_dict[player2].dates_played[date]['lost'] == 0 and players_dict[player2].dates_played[date]['drawn'] == 0:
                        players_dict[player2].undefeated_records += 1
                    for player, player_obj in players_dict.items():
                        if date not in player_obj.dates_played:
                            players_dict[player].update_glicko_rating(series=None)

                if date >= modern_ligan_start and date <= modern_ligan_end:
                    players_dict[player1].modern_ligan_dates_played[date] = players_dict[player1].dates_played[date]
                    players_dict[player2].modern_ligan_dates_played[date] = players_dict[player2].dates_played[date]
    calculate_leaderboard_points(players_dict)
    return None

def calculate_leaderboard_points(players_dict):
    for player in players_dict:
        players_dict[player].calculate_points()
        leaderboards.add_player(player)
        leaderboards.update_player(player, elo_rating = players_dict[player].elo_rating, glicko_rating = players_dict[player].glicko_rating.mu, modern_ligan_rating=players_dict[player].modern_ligan_rating, undefeated_records=players_dict[player].undefeated_records, total_matches_played=players_dict[player].total_matches_played,total_events_played= players_dict[player].total_events_played, total_draws=players_dict[player].draw_counter, event_completed_percentage=players_dict[player].event_completed_percentage, game_win_rate=players_dict[player].game_win_rate, match_win_rate=players_dict[player].match_win_rate, total_byes=players_dict[player].total_byes)
        
    return None

def write_data_to_yaml():
    leaderboards_yaml_dict = {"Bye Leaderboard": [], "Draw Leaderboard": [], "Elo Leaderboard": [], "Game Win Percentage Leaderboard": [], "Match Win Percentage Leaderboard": [], "Modern Ligan Leaderboard": [], "Most Played Events Leaderboard": [], "Undefeated Leaderboard": [], "Completed Events Leaderboard": [], "Glicko Rating Leaderboard": [], "Most Played Matches Leaderboard": [], "Drop Rate Leaderboard": []}
    players_yaml_dict = {}
    for player, player_obj in players_dict.items():
        leaderboards_yaml_dict['Bye Leaderboard'].append({player: player_obj.total_byes})
        leaderboards_yaml_dict['Draw Leaderboard'].append({player: player_obj.draw_counter})
        leaderboards_yaml_dict['Elo Leaderboard'].append({player: player_obj.elo_rating})
        leaderboards_yaml_dict['Game Win Percentage Leaderboard'].append({player: player_obj.game_win_rate})
        leaderboards_yaml_dict['Match Win Percentage Leaderboard'].append({player: player_obj.match_win_rate})
        leaderboards_yaml_dict['Modern Ligan Leaderboard'].append({player: player_obj.modern_ligan_rating})
        leaderboards_yaml_dict['Most Played Events Leaderboard'].append({player: player_obj.total_events_played})
        leaderboards_yaml_dict['Undefeated Leaderboard'].append({player: player_obj.undefeated_records})
        leaderboards_yaml_dict['Completed Events Leaderboard'].append({player: player_obj.event_completed_percentage})
        leaderboards_yaml_dict['Glicko Rating Leaderboard'].append({player: player_obj.glicko_rating.mu})
        leaderboards_yaml_dict['Most Played Matches Leaderboard'].append({player: player_obj.total_matches_played})
        leaderboards_yaml_dict['Drop Rate Leaderboard'].append({player: player_obj.drop_rate})
        players_yaml_dict[player] = player_obj.__dict__
        players_yaml_dict[player]['glicko_rating'] = player_obj.glicko_rating.__dict__
    leaderboards_yaml_dict['Bye Leaderboard'] = sorted(leaderboards_yaml_dict['Bye Leaderboard'], key=lambda x: list(x.values())[0], reverse=True)[:8]
    leaderboards_yaml_dict['Draw Leaderboard'] = sorted(leaderboards_yaml_dict['Draw Leaderboard'], key=lambda x: list(x.values())[0], reverse=True)[:8]
    leaderboards_yaml_dict['Elo Leaderboard'] = sorted(leaderboards_yaml_dict['Elo Leaderboard'], key=lambda x: list(x.values())[0], reverse=True)[:8]
    leaderboards_yaml_dict['Game Win Percentage Leaderboard'] = sorted(leaderboards_yaml_dict['Game Win Percentage Leaderboard'], key=lambda x: list(x.values())[0], reverse=True)[:8]
    leaderboards_yaml_dict['Match Win Percentage Leaderboard'] = sorted(leaderboards_yaml_dict['Match Win Percentage Leaderboard'], key=lambda x: list(x.values())[0], reverse=True)[:8]
    leaderboards_yaml_dict['Modern Ligan Leaderboard'] = sorted(leaderboards_yaml_dict['Modern Ligan Leaderboard'], key=lambda x: list(x.values())[0], reverse=True)
    leaderboards_yaml_dict['Most Played Events Leaderboard'] = sorted(leaderboards_yaml_dict['Most Played Events Leaderboard'], key=lambda x: list(x.values())[0], reverse=True)[:8]
    leaderboards_yaml_dict['Undefeated Leaderboard'] = sorted(leaderboards_yaml_dict['Undefeated Leaderboard'], key=lambda x: list(x.values())[0], reverse=True)[:8]
    leaderboards_yaml_dict['Completed Events Leaderboard'] = sorted(leaderboards_yaml_dict['Completed Events Leaderboard'], key=lambda x: list(x.values())[0], reverse=True)[:8]
    leaderboards_yaml_dict['Glicko Rating Leaderboard'] = sorted(leaderboards_yaml_dict['Glicko Rating Leaderboard'], key=lambda x: list(x.values())[0], reverse=True)[:8]
    leaderboards_yaml_dict['Most Played Matches Leaderboard'] = sorted(leaderboards_yaml_dict['Most Played Matches Leaderboard'], key=lambda x: list(x.values())[0], reverse=True)[:8]
    leaderboards_yaml_dict['Drop Rate Leaderboard'] = sorted(leaderboards_yaml_dict['Drop Rate Leaderboard'], key=lambda x: list(x.values())[0], reverse=True)[:8]
    with open('players.yaml', 'w') as outfile:
        yaml.dump(players_yaml_dict, outfile, default_flow_style=False, allow_unicode=True, encoding='utf-8')
    with open('leaderboards.yaml', 'w') as outfile:
        yaml.dump(leaderboards_yaml_dict, outfile, default_flow_style=False, allow_unicode=True, encoding='utf-8')
    return None

def import_event_files():
    list_of_dates = [folder for folder in os.listdir('datafiles') if os.path.isdir(os.path.join('datafiles', folder))]
    events_dict = {}
    
    # Loop through each date in the list
    for dates in list_of_dates:
        # Initialize a list to store the event data for each date
        event_data = []
        
        # Get the folder path for the date
        folder_path = Path("datafiles/" + dates)
        
        # Loop through each file in the folder
        for file_path in folder_path.iterdir():
            # Check if the file is a regular file
            if file_path.is_file():
                # Import the scores for a round
                round_data = import_scores_round(file_path)
                
                # Add the round data to the event data list
                event_data.append(round_data)
        
        # Add the event data to the events dictionary, using the date as the key
        events_dict[dates] = event_data
    
    # Return the events dictionary
    return events_dict


#dates = ['240311', '240318', '240325', '240408']
modern_ligan_start = '240311'
modern_ligan_end = '240408'

events = import_event_files()


players_dict = {}
leaderboards = leaderboards()
calculate_stats_in_data(events, players_dict)
write_data_to_yaml()

