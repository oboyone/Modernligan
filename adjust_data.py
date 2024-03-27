import yaml 
import csv

player_data_dict = {}

#with open('historic_data_all_seasons.yaml', 'r') as file:
#    temp_dict = yaml.safe_load(file)
#    for player, data in temp_dict.items():
#        player_data_dict[player.title()] = {'Played Events': data['Played Events']}

with open('current_standings_modernligan.csv', 'r') as file:
    reader = csv.reader(file, delimiter=',')
    for row in reader:
        player_data_dict[row[0].title()] = {}
        player_data_dict[row[0].title()]['Modernligan_Points'] = row[-1]

print(player_data_dict)



with open('data.yaml', 'r', encoding='utf-8') as data_file:
    data_dict = yaml.safe_load(data_file)
    with open('data.yaml', 'w', encoding='utf-8') as data_file:
        for player, data in data_dict.items():
            if player in player_data_dict:
                #data_dict[player]['events_played'] = 0
               # data_dict[player]['events_played'] = player_data_dict[player]['Played Events']
                data_dict[player]['modernligan_points'] = player_data_dict[player]['Modernligan_Points']
            else:
                pass

        yaml.dump(data_dict, data_file, encoding='utf-8', allow_unicode=True)
updated_leaderboards_list = []
with open ('data.yaml', 'r', encoding='utf-8') as data_file:
    data_dict = yaml.safe_load(data_file)
    with open ('leaderboards.yaml', 'r', encoding='utf-8') as leaderboards_file:
        leaderboards_dict = yaml.safe_load(leaderboards_file)
        for player in leaderboards_dict.get('Modern Ligan Leaderboard'):
            if list(player.keys())[0] in player_data_dict:
                updated_leaderboards_list.append({list(player.keys())[0]:int(player_data_dict[list(player.keys())[0]]['Modernligan_Points'])})
            
        updated_leaderboards_list = sorted(updated_leaderboards_list, key=lambda x: list(x.values())[0], reverse=True)
        leaderboards_dict['Modern Ligan Leaderboard'] = updated_leaderboards_list

        with open ('leaderboards.yaml', 'w', encoding='utf-8') as leaderboards_file:
            yaml.dump(leaderboards_dict, leaderboards_file, encoding='utf-8', allow_unicode=True)