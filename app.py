from flask import Flask, render_template
import yaml

# Initialize Flask app
app = Flask(__name__)

# Automatically reload templates when they are modified
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Define route for displaying leaderboards
@app.route('/leaderboards')
def leaderboards():
    # Load leaderboard data from YAML file
    with open('leaderboards.yaml', 'r') as file:
        leaderboard_data = yaml.safe_load(file)
    # Render leaderboards template with the loaded data
    return render_template('leaderboards.html', leaderboard_data=leaderboard_data)

# Email of the maintainer
maintainer_email = 'alexanderjn@live.se'

# Define route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Define route for the about page
@app.route('/about')
def about():
    # Pass maintainer email to the about template
    return render_template('about.html', maintainer_email=maintainer_email)

# Define route for displaying modernligan standings
@app.route('/modernligan_standings.html')
def modernligan_standings():
    # Load leaderboard data from YAML file
    with open('leaderboards.yaml', 'r') as file:
        leaderboard_data = yaml.safe_load(file)
    # Render modernligan standings template with the loaded data
    return render_template('modernligan_standings.html', leaderboard_data=leaderboard_data)

# Load player data from YAML file
with open("players.yaml", "r") as player_file:
    player_data = yaml.safe_load(player_file)

# Define route for displaying player statistics
@app.route('/player_stats')
def player_stats():
    # Load opt-out list from YAML file
    with open('opt_out_list.yaml', 'r') as opt_out_file:
        opt_out_list = yaml.safe_load(opt_out_file)
    # Render player statistics template with the loaded player data and opt-out list
    return render_template('player_stats.html', players=player_data, opt_out_list=opt_out_list.get('opt_out'))

# Define route for displaying individual player information
@app.route('/player_stats/<player_name>')
def player(player_name):
    # Retrieve player info from player data dictionary
    player_info = player_data.get(player_name)
    if player_info:
        # Render player info template with the retrieved player info
        return render_template('player_info.html', player_info=player_info, player_name=player_name)
    else:
        # Return a message if player is not found
        return "Player not found."

# Define route for opting out of player statistics
@app.route('/player_stats/opt_out')   
def opt_out():
    return render_template('opt_out.html')

# Define route for displaying information about Glicko Elo ratings
@app.route('/glicko_elo_about')   
def glicko_elo_about():
    return render_template('glicko_elo_about.html')

# Function to create and return the Flask app
def create_app():
    return app

# Start the server if the script is executed directly
if __name__ == "__main__":
    from waitress import serve
    # Serve the app using Waitress server on localhost port 9000
    serve(app, host="127.0.0.1", port=9000)
