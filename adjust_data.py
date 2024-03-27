import yaml 
import csv

player_data_dict = {}

# Load data from CSV file into player_data_dict
with open('current_standings_modernligan.csv', 'r') as file:
    reader = csv.reader(file, delimiter=',')
    for row in reader:
        # Capitalize player name and store points
        player_data_dict[row[0].title()] = {'Modernligan_Points': row[-1]}

# Update data.yaml with modernligan points
with open('data.yaml', 'r', encoding='utf-8') as data_file:
    data_dict = yaml.safe_load(data_file)
    for player, data in data_dict.items():
        if player in player_data_dict:
            data_dict[player]['modernligan_points'] = player_data_dict[player]['Modernligan_Points']

# Write updated data to data.yaml
with open('data.yaml', 'w', encoding='utf-8') as data_file:
    yaml.dump(data_dict, data_file, encoding='utf-8', allow_unicode=True)

# Update leaderboard based on modernligan points
updated_leaderboards_list = []
with open('leaderboards.yaml', 'r', encoding='utf-8') as leaderboards_file:
    leaderboards_dict = yaml.safe_load(leaderboards_file)
    for player in leaderboards_dict.get('Modern Ligan Leaderboard'):
        player_name = list(player.keys())[0]
        if player_name in player_data_dict:
            updated_leaderboards_list.append({player_name: int(player_data_dict[player_name]['Modernligan_Points'])})

# Sort leaderboard based on points
updated_leaderboards_list = sorted(updated_leaderboards_list, key=lambda x: list(x.values())[0], reverse=True)
leaderboards_dict['Modern Ligan Leaderboard'] = updated_leaderboards_list

# Write updated leaderboard to leaderboards.yaml
with open('leaderboards.yaml', 'w', encoding='utf-8') as leaderboards_file:
    yaml.dump(leaderboards_dict, leaderboards_file, encoding='utf-8', allow_unicode=True)
