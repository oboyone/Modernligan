import email
from bs4 import BeautifulSoup
import os
from pathlib import Path
import yaml
import quopri

list_of_forbidden_chars = ['🔥']
yaml.Dumper.ignore_aliases = lambda *args : True

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

def read_data():
    """
    Reads player and date data from YAML files.

    :return: Tuple of player data and date list.
    :rtype: tuple
    """
    print("Reading data from YAML files...")
    try:
        with open('data.yaml', encoding='utf-8') as data_file, open('dates.yaml', encoding='utf-8') as dates_file:
            player_data = yaml.safe_load(data_file) or {}
            date_data = yaml.safe_load(dates_file) or []
            print("Data read from YAML files successfully.")
    except FileNotFoundError:
        print("Error: File 'data.yaml' or 'dates.yaml' not found!")
        raise FileNotFoundError("File 'data.yaml' or 'dates.yaml' not found!")
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        raise yaml.YAMLError("Error parsing YAML:", e)
    print("Processing player data...")
    player_data = {player[key]: value for player in player_data.get('players', []) for key, value in player.items()} if 'players' in player_data else {}
    print("Processing date list...")
    all_date_list = date_data.get('dates')
    date_list = [date for date in date_data.get('dates') if date not in (date_data.get('parsed_dates') or [])]
    print("Data processing completed.")
    print(f"Player data: {player_data}")
    print(f"List of dates to parse: {date_list}")
    print(f"Already Parsed dates: {date_data.get('parsed_dates')}")
    return player_data, date_list, all_date_list

def write_data(data, leaderboards, dates, all_dates):
    """
    Writes player and date data to YAML files.

    :param data: Dictionary of player data.
    :type data: dict
    :param dates: List of dates.
    :type dates: list
    """
    if data is None:
        raise ValueError("data cannot be None")
    if dates is None:
        raise ValueError("parsed_dates cannot be None")
    if all_dates is None:
        raise ValueError("dates cannot be None")
    parsed_dates = {'dates': all_dates, 'parsed_dates': all_dates}
    if len(dates) > 0:
        with open('data.yaml', 'w', encoding='utf-8') as data_file:
            yaml.dump(data, data_file, encoding='utf-8', allow_unicode=True)
        with open('dates.yaml', 'w', encoding='utf-8') as dates_file:
            yaml.dump(parsed_dates, dates_file, encoding='utf-8', allow_unicode=True)
        with open('leaderboards.yaml', 'w', encoding='utf-8') as leaderboards_file:
            yaml.dump(leaderboards, leaderboards_file, encoding='utf-8', allow_unicode=True)
    else:
        pass


def calculate_elo_rating(player_rating, opponent_rating, outcome):
    """
    Calculate the new Elo rating for a player based on the outcome of a match

    :param player_rating: Elo rating of the player
    :param opponent_rating: Elo rating of the opponent
    :param outcome: The outcome of the match (1 for win, 0 for loss)
    :return: The new Elo rating for the player
    """
    expected_score = 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))
    new_rating = player_rating + 32 * (outcome - expected_score)
    return new_rating

def keys_exists(element, *keys):
    '''
    Check if *keys (nested) exists in `element` (dict).
    '''
    if not isinstance(element, dict):
        raise AttributeError('keys_exists() expects dict as first argument.')
    if len(keys) == 0:
        raise AttributeError('keys_exists() expects at least two arguments, one given.')

    _element = element
    for key in keys:
        try:
            _element = _element[key]
        except KeyError:
            return False
    return True

def calculate_elo_in_data(events_data_dict):
    for date, rounds in events_data_dict.items():
        round_number = 0
        for round in rounds:
            round_number = round_number + 1
            for match in round:
                # Initialize ratings if not present
                if match.get('player_one').title() not in player_data_dict:
                    player_data_dict[match.get('player_one').title()] = {'elo_rating': 1500, 'draw_counter': 0, 'matches_won_against':{}, 'matches_lost_against':{}, 'dates_played':{date:{'wins': 0, 'losses': 0, 'draws': 0, 'byes': 0}}, 'undefeated_records': 0}
                if match.get('player_two').title() not in player_data_dict:
                    player_data_dict[match.get('player_two').title()] = {'elo_rating': 1500, 'draw_counter': 0, 'matches_won_against':{}, 'matches_lost_against':{}, 'dates_played':{date:{'wins': 0, 'losses': 0, 'draws': 0, 'byes': 0}}, 'undefeated_records': 0}
                if not keys_exists(player_data_dict[match.get('player_one').title()].get('dates_played'), date):
                    player_data_dict[match.get('player_one').title()]['dates_played'][date] = {'wins': 0, 'losses': 0, 'draws': 0, 'byes': 0}
                if not keys_exists(player_data_dict[match.get('player_two').title()].get('dates_played'), date):
                    player_data_dict[match.get('player_two').title()]['dates_played'][date] = {'wins': 0, 'losses': 0, 'draws': 0, 'byes': 0}
                # Update ratings based on match outcome
                if match.get('player_one_games_won') == 2 or match.get('player_one_games_won') == '2':
                    player_data_dict[match.get('player_one').title()]['elo_rating'] = calculate_elo_rating(
                        float(player_data_dict[match.get('player_one').title()]['elo_rating']),
                        float(player_data_dict[match.get('player_two').title()]['elo_rating']),
                        1
                    )
                    player_data_dict[match.get('player_two').title()]['elo_rating'] = calculate_elo_rating(
                        float(player_data_dict[match.get('player_two').title()]['elo_rating']),
                        float(player_data_dict[match.get('player_one').title()]['elo_rating']),
                        0
                    )
                    if player_data_dict[match.get('player_one').title()].get('matches_won_against').get(match.get('player_two').title()):
                        player_data_dict[match.get('player_one').title()]['matches_won_against'][match.get('player_two').title()] += 1
                    else: 
                        player_data_dict[match.get('player_one').title()]['matches_won_against'][match.get('player_two').title()] = 1
                    if player_data_dict[match.get('player_two').title()].get('matches_lost_against').get(match.get('player_one').title()):
                        player_data_dict[match.get('player_two').title()]['matches_lost_against'][match.get('player_one').title()] += 1
                    else: 
                        player_data_dict[match.get('player_two').title()]['matches_lost_against'][match.get('player_one').title()] = 1
                    player_data_dict[match.get('player_one').title()]['dates_played'][date]['wins'] += 1
                    player_data_dict[match.get('player_two').title()]['dates_played'][date]['losses'] += 1                                                                    
                elif match.get('player_two_games_won') == 2 or match.get('player_two_games_won') == '2':
                    player_data_dict[match.get('player_one').title()]['elo_rating'] = calculate_elo_rating(
                        float(player_data_dict[match.get('player_one').title()]['elo_rating']),
                        float(player_data_dict[match.get('player_two').title()]['elo_rating']),
                        0
                    )
                    player_data_dict[match.get('player_two').title()]['elo_rating'] = calculate_elo_rating(
                        float(player_data_dict[match.get('player_two').title()]['elo_rating']),
                        float(player_data_dict[match.get('player_one').title()]['elo_rating']),
                        1
                    )
                    if player_data_dict[match.get('player_one').title()].get('matches_lost_against').get(match.get('player_two').title()):
                        player_data_dict[match.get('player_one').title()]['matches_lost_against'][match.get('player_two').title()] += 1
                    else: 
                        player_data_dict[match.get('player_one').title()]['matches_lost_against'][match.get('player_two').title()] = 1
                    if player_data_dict[match.get('player_two').title()].get('matches_won_against').get(match.get('player_one').title()):
                        player_data_dict[match.get('player_two').title()]['matches_won_against'][match.get('player_one').title()] += 1
                    else: 
                        player_data_dict[match.get('player_two').title()]['matches_won_against'][match.get('player_one').title()] = 1
                    player_data_dict[match.get('player_one').title()]['dates_played'][date]['losses'] += 1
                    player_data_dict[match.get('player_two').title()]['dates_played'][date]['wins'] += 1

                else:
                    player_data_dict[match.get('player_one').title()]['elo_rating'] = calculate_elo_rating(
                        float(player_data_dict[match.get('player_one').title()]['elo_rating']),
                        float(player_data_dict[match.get('player_two').title()]['elo_rating']),
                        0.5
                    )
                    player_data_dict[match.get('player_two').title()]['elo_rating'] = calculate_elo_rating(
                        float(player_data_dict[match.get('player_two').title()]['elo_rating']),
                        float(player_data_dict[match.get('player_one').title()]['elo_rating']),
                        0.5
                    )
                    if player_data_dict[match.get('player_one').title()].get('draw_counter'):
                        player_data_dict[match.get('player_one').title()]['draw_counter'] += 1
                    else:
                        player_data_dict[match.get('player_one').title()]['draw_counter'] = 1
                    if player_data_dict[match.get('player_two').title()].get('draw_counter'):
                        player_data_dict[match.get('player_two').title()]['draw_counter'] += 1
                    else:
                        player_data_dict[match.get('player_two').title()]['draw_counter'] = 1
                    player_data_dict[match.get('player_one').title()]['dates_played'][date]['draws'] += 1
                    player_data_dict[match.get('player_two').title()]['dates_played'][date]['draws'] += 1
                if round_number == 4:
                    if player_data_dict[match.get('player_one').title()].get('dates_played').get(date).get('losses') == 0 and player_data_dict[match.get('player_one').title()].get('dates_played').get(date).get('draws') == 0:
                        player_data_dict[match.get('player_one').title()]['undefeated_records'] += 1
                    if player_data_dict[match.get('player_two').title()].get('dates_played').get(date).get('losses') == 0 and player_data_dict[match.get('player_two').title()].get('dates_played').get(date).get('draws') == 0:
                        player_data_dict[match.get('player_two').title()]['undefeated_records'] += 1
                    if player_data_dict[match.get('player_one').title()].get('dates_played').get(date).get('wins') + player_data_dict[match.get('player_one').title()].get('dates_played').get(date).get('losses') + player_data_dict[match.get('player_one').title()].get('dates_played').get(date).get('draws') != 4:
                        player_data_dict[match.get('player_one').title()]['dates_played'][date]['byes'] += 1
                    if player_data_dict[match.get('player_two').title()].get('dates_played').get(date).get('wins') + player_data_dict[match.get('player_two').title()].get('dates_played').get(date).get('losses') + player_data_dict[match.get('player_one').title()].get('dates_played').get(date).get('draws') != 4:
                        player_data_dict[match.get('player_two').title()]['dates_played'][date]['byes'] += 1

def calculate_leaderboards(player_data_dict):
    def modern_ligan_points(list_of_events):
        points_list = []
        for event in list_of_events:
            points = event.get('wins') * 3 + event.get('draws') * 1
            points_list.append(points)
        points_list = sorted(points_list, reverse=True)
        if len(points_list) > 8:
            points_list = points_list[:8]
        standings_value = sum(points_list)
        return standings_value
    def count_byes(list_of_events):
        byes = 0
        for event in list_of_events:
            byes += event.get('byes')
        return byes

    elo_leaderboard = []
    undefeated_leaderboard = []
    draw_leaderboard = []
    most_played_events_leaderboard = []
    modern_ligan_leaderboard = []
    bye_leaderboard = []
    for player, values in player_data_dict.items():

        elo_leaderboard.append({player:values.get('elo_rating')})
        undefeated_leaderboard.append({player:values.get('undefeated_records')})
        draw_leaderboard.append({player:values.get('draw_counter') })
        most_played_events_leaderboard.append({player:len(values.get('dates_played'))})
        bye_leaderboard.append({player:count_byes(list(values.get('dates_played').values()))})

    elo_leaderboard = sort_dict_list(elo_leaderboard, reverse=True)[:8]
    undefeated_leaderboard = sort_dict_list(undefeated_leaderboard, reverse=True)[:5]
    draw_leaderboard = sort_dict_list(draw_leaderboard, reverse=True)[:5]
    most_played_events_leaderboard = sort_dict_list(most_played_events_leaderboard, reverse=True)[:5]
    modern_ligan_leaderboard = sort_dict_list(modern_ligan_leaderboard, reverse=True)[:20]
    bye_leaderboard = sort_dict_list(bye_leaderboard, reverse=True)[:5]
    return elo_leaderboard, undefeated_leaderboard, draw_leaderboard, most_played_events_leaderboard, modern_ligan_leaderboard, bye_leaderboard

def sort_dict_list(dict_list, reverse=False):
    """
    Sorts a list of dictionaries based on the values of the first key-value pair.

    Args:
        dict_list (List[Dict]): A list of dictionaries to be sorted.

    Returns:
        List[Dict]: The sorted list of dictionaries.
    """
    # Sorts the list of dictionaries based on the values of the first key-value pair
    # using the lambda function as the sorting key.
    sorted_list = sorted(dict_list, key=lambda x: list(x.values())[0], reverse=reverse)
    
    return sorted_list


player_data_dict, date_list, all_dates = read_data()
events_data_dict = import_events(date_list)
calculate_elo_in_data(events_data_dict)
elo_leader_board, undefeated_leaderboard, draw_leaderboard, most_played_events_leaderboard, modern_ligan_leaderboard, bye_leaderboard = calculate_leaderboards(player_data_dict)
leaderboards_dict = {}
leaderboards_dict['Elo Leaderboard'] = elo_leader_board
leaderboards_dict['Undefeated Leaderboard'] = undefeated_leaderboard
leaderboards_dict['Draw Leaderboard'] = draw_leaderboard
leaderboards_dict['Most Played Events Leaderboard'] = most_played_events_leaderboard
leaderboards_dict['Modern Ligan Leaderboard'] = modern_ligan_leaderboard
leaderboards_dict['Bye Leaderboard'] = bye_leaderboard
write_data(player_data_dict, leaderboards_dict, date_list, all_dates)
