from gevent import monkey
monkey.patch_all()

import engine
import time
import json
from flask_socketio import SocketIO, join_room, leave_room
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from collections import OrderedDict
from exceptiondef import GameException, AuthException
from storage_mysql import StorageMySql
from user_store import UserStore

app = Flask(__name__)
socketio = SocketIO(app)

def require_auth():
    users.validate(request.authorization.username, request.authorization.password)
    return request.authorization.username

@app.route('/signup', methods=['POST'])
def signup():
    try:
        if 'username' not in request.json or 'password' not in request.json:
            raise GameException('missing username or password in signup request')
        users.create(request.json['username'], request.json['password'])
        return ('', 200)
    except GameException as ex:
        return (ex.msg, 400)
    except AuthException as ex:
        return (ex.msg, 401)

    return render_template('login.html')

@app.route('/game', methods=['POST'])
def create_game():
    try:
        require_auth()
        result = game_engine.create_new_game(request.json['game_name'], request.json['player1a'], request.json['player1b'], request.json['player2a'], request.json['player2b'])
    except GameException as ex:
        return (ex.msg, 400)
    except AuthException as ex:
        return (ex.msg, 401)
    return (jsonify(result), 200)

@app.route('/game/<game_id>', methods=['DELETE'])
def end_game(game_id):
    try:
        username = require_auth()
        game_engine.end_game(game_id, username)
    except GameException as ex:
        return (ex.msg, 400)
    except AuthException as ex:
        return (ex.msg, 401)
    return ('', 200)

@app.route('/game/<game_id>/guess', methods=['POST'])
def guess(game_id):
    try:
        username = require_auth()
        result = game_engine.make_guess(game_id, username, request.json['guess_word'])
        update_clients_for_game(game_id)
    except GameException as ex:
        return (ex.msg, 400)
    except AuthException as ex:
        return (ex.msg, 401)
    return (jsonify(result), 200)

@app.route('/game/<game_id>/clue', methods=['POST'])
def clue(game_id):
    try:
        username = require_auth()
        result = game_engine.give_clue(game_id, username, request.json['clue_word'].split(' ')[0], request.json['clue_number'])
        update_clients_for_game(game_id)
    except GameException as ex:
        return (ex.msg, 400)
    except AuthException as ex:
        return (ex.msg, 401)
    return (jsonify(result), 200)

@app.route('/player/<player_id>/games', methods=['GET'])
def get_current_game(player_id):
    try:
        require_auth()
        result = game_engine.get_player_game_names(player_id)
    except GameException as ex:
        return (ex.msg, 400)
    except AuthException as ex:
        return (ex.msg, 401)
    return (jsonify(result), 200)

@app.route('/')
def main():
    return list_games()

@app.route('/game_list.html')
def list_games():
    try:
        return render_template('game_list.html')
    except AuthException as ex:
        return (ex.msg, 401)

@app.route('/game_board.html')
def play_game():
    try:
        return render_template('game_board.html')
    except AuthException as ex:
        return render_template('game_list.html')

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

def update_clients_for_game(game_id):
    gamestate = game_engine.get_game_state(game_id)
    gamestate['game_id'] = game_id
    socketio.emit('gamestate', gamestate, room=str(game_id) + 'cluer')
    game_engine.obscure_answers(gamestate)
    socketio.emit('gamestate', gamestate, room=str(game_id) + 'guesser')

@socketio.on('join_game')
def on_join_game(data):
    try:
        username = data['username']
        password = data['password']
        game_id = data['game_id']
        users.validate(username, password)
        if game_id in game_engine.get_player_games(username):
            role = game_engine.get_player_role(game_id, username)
            join_room(str(game_id) + role)
            update_clients_for_game(game_id)
    except AuthException as ex:
        return (ex.msg, 401)

@socketio.on('leave_game')
def on_leave_game(data):
    try:
        username = data['username']
        password = data['password']
        game_id = data['game_id']
        users.validate(username, password)
        if game_id in game_engine.get_player_games(username):
            role = game_engine.get_player_role(game_id, username)
            leave_room(str(game_id) + role)
    except AuthException as ex:
        return (ex.msg, 401)

if __name__ == '__main__':
    global game_engine
    with file('properties.json') as property_file:
        properties = json.load(property_file)
    storage = StorageMySql(properties['database'])
    users = UserStore(properties['database'])
    game_engine = engine.GameEngine(storage)
    socketio.run(app, properties['bind_ip_address'], port=properties['bind_port'])
