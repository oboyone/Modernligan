from flask import Flask, render_template
import yaml

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
#app.run(host= '192.168.1.214', port=9000, debug=False)

@app.route('/leaderboards')
def leaderboards():
    with open('leaderboards.yaml', 'r') as file:
        leaderboard_data = yaml.safe_load(file)
    return render_template('leaderboards.html', leaderboard_data=leaderboard_data)

maintainer_email = 'alexanderjn@live.se'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html', maintainer_email=maintainer_email)

@app.route('/modernligan_standings.html')
def modernligan_standings():
    with open('leaderboards.yaml', 'r') as file:
        leaderboard_data = yaml.safe_load(file)
    return render_template('modernligan_standings.html', leaderboard_data=leaderboard_data)

with open("data.yaml", "r") as player_file:
    player_data = yaml.safe_load(player_file)

@app.route('/player_stats')
def player_stats():
    with open('opt_out_list.yaml', 'r') as opt_out_file:
        opt_out_list = yaml.safe_load(opt_out_file)
    return render_template('player_stats.html', players=player_data, opt_out_list=opt_out_list.get('opt_out'))

@app.route('/player_stats/<player_name>')
def player(player_name):
    player_info = player_data.get(player_name)
    if player_info:
        return render_template('player_info.html', player_info=player_info, player_name=player_name)
    else:
        return "Player not found."

@app.route('/player_stats/opt_out')   
def opt_out():
    return render_template('opt_out.html')
 

def create_app():
    return app

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="127.0.0.1", port=9000)
