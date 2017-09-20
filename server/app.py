from gevent import monkey
monkey.patch_all()

import engine
import time
import json
from flask_login import LoginManager, login_user, login_required
from flask_socketio import SocketIO, join_room, leave_room
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from collections import OrderedDict
from exceptiondef import GameException
from storage_mysql import StorageMySql
from user_store import UserStore

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(player_id):
    return users.get(player_id)

def validate_user(player_id, password):
    return users.validate(player_id, password)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = validate_user(request.json['player_id'], request.json['password'])
        if user is not None:
            login_user(user)
            nexturl = request.args.get('next')
            return (nexturl or '/game_list.html', 200)
        else:
            return ('/login', 401)
    return render_template('login.html')

def update_clients_for_game(game_id):
    gamestate = game_engine.get_game_state(game_id)
    gamestate['game_id'] = game_id
    socketio.emit('gamestate', gamestate, room=str(game_id) + 'cluer')
    game_engine.obscure_answers(gamestate)
    socketio.emit('gamestate', gamestate, room=str(game_id) + 'guesser')

@app.route('/game', methods=['POST'])
@login_required
def create_game():
    try:
        result = game_engine.create_new_game(request.json['game_name'], request.json['player1a'], request.json['player1b'], request.json['player2a'], request.json['player2b'])
    except GameException as ex:
        return (ex.msg, 400)
    return (jsonify(result), 200)

@app.route('/game/<game_id>', methods=['DELETE'])
@login_required
def end_game(game_id):
    try:
        game_engine.end_game(game_id, request.json['player_id'])
    except GameException as ex:
        return (ex.msg, 400)
    return ('', 200)

@app.route('/game/<game_id>/guess', methods=['POST'])
@login_required
def guess(game_id):
    try:
        result = game_engine.make_guess(game_id, request.json['player_id'], request.json['guess_word'])
        update_clients_for_game(game_id)
    except GameException as ex:
        return (ex.msg, 400)
    return (jsonify(result), 200)

@app.route('/game/<game_id>/clue', methods=['POST'])
@login_required
def clue(game_id):
    try:
        result = game_engine.give_clue(game_id, request.json['player_id'], request.json['clue_word'].split(' ')[0], request.json['clue_number'])
        update_clients_for_game(game_id)
    except GameException as ex:
        return (ex.msg, 400)
    return (jsonify(result), 200)

@app.route('/player/<player_id>/games', methods=['GET'])
@login_required
def get_current_game(player_id):
    try:
        result = game_engine.get_player_game_names(player_id)
    except GameException as ex:
        return (ex.msg, 400)
    return (jsonify(result), 200)

@app.route('/')
@login_required
def main():
    return render_template('game_list.html')

@app.route('/game_list.html')
@login_required
def list_games():
    return render_template('game_list.html')

@app.route('/game_board.html')
@login_required
def play_game():
    return render_template('game_board.html')

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@socketio.on('join_game')
@login_required
def on_join_game(data):
    player_id = data['player_id']
    game_id = data['game_id']
    if game_id in game_engine.get_player_games(player_id):
        role = game_engine.get_player_role(game_id, player_id)
        join_room(str(game_id) + role)
        update_clients_for_game(game_id)

@socketio.on('leave_game')
@login_required
def on_leave_game(data):
    player_id = data['player_id']
    game_id = data['game_id']
    if game_id in game_engine.get_player_games(player_id):
        role = game_engine.get_player_role(game_id, player_id)
        leave_room(str(game_id) + role)

if __name__ == '__main__':
    global game_engine
    with file('properties.json') as property_file:
        properties = json.load(property_file)
    storage = StorageMySql(properties['database'])
    users = UserStore(properties['database'])
    game_engine = engine.GameEngine(storage)
    socketio.run(app, properties['bind_ip_address'], port=properties['bind_port'])
