from flask import Flask, render_template
import yaml

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Route to display leaderboards
@app.route('/leaderboards')
def leaderboards():
    # Load leaderboard data from YAML file
    with open('leaderboards.yaml', 'r') as file:
        leaderboard_data = yaml.safe_load(file)
    # Render leaderboard template with the loaded data
    return render_template('leaderboards.html', leaderboard_data=leaderboard_data)

# Email address of the maintainer
maintainer_email = 'alexanderjn@live.se'

# Route to display the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to display the about page
@app.route('/about')
def about():
    # Pass maintainer email to the template
    return render_template('about.html', maintainer_email=maintainer_email)

# Route to display modernligan standings
@app.route('/modernligan_standings.html')
def modernligan_standings():
    # Load leaderboard data from YAML file
    with open('leaderboards.yaml', 'r') as file:
        leaderboard_data = yaml.safe_load(file)
    # Render modernligan standings template with the loaded data
    return render_template('modernligan_standings.html', leaderboard_data=leaderboard_data)

# Load player data from YAML file
with open("data.yaml", "r") as player_file:
    player_data = yaml.safe_load(player_file)

# Route to display player stats
@app.route('/player_stats')
def player_stats():
    # Load opt-out list from YAML file
    with open('opt_out_list.yaml', 'r') as opt_out_file:
        opt_out_list = yaml.safe_load(opt_out_file)
    # Render player stats template with player data and opt-out list
    return render_template('player_stats.html', players=player_data, opt_out_list=opt_out_list.get('opt_out'))

# Route to display player information
@app.route('/player_stats/<player_name>')
def player(player_name):
    # Get player information from player data
    player_info = player_data.get(player_name)
    if player_info:
        # Render player info template with player information
        return render_template('player_info.html', player_info=player_info, player_name=player_name)
    else:
        # Display message if player is not found
        return "Player not found."

# Route to display opt-out information
@app.route('/player_stats/opt_out')   
def opt_out():
    # Render opt-out template
    return render_template('opt_out.html')

# Function to create the Flask app
def create_app():
    return app

# Run the app if this file is executed directly
if __name__ == "__main__":
    from waitress import serve
    # Serve the app using Waitress server
    serve(app, host="127.0.0.1", port=9000)
