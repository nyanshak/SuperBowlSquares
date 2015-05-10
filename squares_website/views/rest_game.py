import os
import os.path
import json
from flask import Blueprint, jsonify, request
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import random
import base64
import shortuuid

rest_game = Blueprint('rest_game', __name__)
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

@rest_game.route('/create', methods=['POST'])
def make_game():
    try:
        data = json.loads(request.data)
        name = data.get('name', None)
        token = data.get('token', None)
        if token is None or type(token) is not unicode:
            raise ValueError()
        g = create_game(name, token)
        if 'token' in g:
            del g['token']
        return jsonify({"success": True, "error": None, "game": g}), 200
    except ValueError as e:
        return jsonify({"success": False, "error": "Must pass game name and password token in post data, ex: {\"name\": \"my_awesome_game\", \"token\": \"super_secret_password\"}", "game": None}), 400

@rest_game.route('/<game_id>', methods=['GET'])
def show_game(game_id):
    g = load_game(game_id)

    if g is None:
        return jsonify({"success": False, "error": "That game does not exist", "game": None}), 404
    else:
        if 'token' in g:
            del g['token']
        return jsonify({"success": True, "error": None, "game": g}), 200

@rest_game.route('/<game_id>/numbers', methods=['POST'])
def set_numbers(game_id):
    g = load_game(game_id)
    if g is None:
        return jsonify({"success": False, "error": "No game for that game_id", "game": None}), 404
    if len(g['afc_values']) and len(g['nfc_values']):
        return jsonify({"success": False, "error": "Numbers already set", "game": g}), 400
    try:
        data = json.loads(request.data)
        token = data.get('token', None)

        if check_password_hash(g['token'], token):
            g = set_square_values(g)
            return jsonify({"success": True, "error": None, "game": g}), 200
        else:
            return jsonify({"success": False, "error": "Not authorized to perform that action", "game": None}), 401
    except ValueError as e:
        return jsonify({"success": False, "error": "Must post password token, ex: {\"token\": \"super_secret_password\"}"}), 400

@rest_game.route('/<game_id>/teams', methods=['POST'])
def set_teams(game_id):
    g = load_game(game_id)
    if g is None:
        return jsonify({"success": False, "error": "No game for that game_id"}), 404
    try:
        data = json.loads(request.data)

        afc_team = data.get('afc_team', None)
        nfc_team = data.get('nfc_team', None)
        token = data.get('token', None)

        if check_password_hash(g['token'], token):
            g['afc_team'] = afc_team
            g['nfc_team'] = nfc_team
            save_game(g)
            return jsonify({"success": True, "error": None}), 200
        else:
            return jsonify({"success": False, "error": "Not authorized to perform that action"}), 401
    except ValueError as e:
        return jsonify({"success": False, "error": "Must post AFC and NFC team names, ex: {\"afc_team\": \"Steelers\", \"nfc_team\": \"Cowboys\", \"token\": \"super_secret_password\"}"}), 400
    
    
@rest_game.route('/<game_id>/square/<int:position>', methods=['POST'])
def square(game_id, position):

    if position > 99 or position < 0:
        return jsonify({"success": False, "error": "Position must be a value between 0 and 99"}), 400
    g = load_game(game_id)
    if g is None:
        return jsonify({"success": False, "error": "No game for that game_id"}), 404
    try:
        data = json.loads(request.data)

        name = data.get('name', None)
        email = data.get('email', None)
        verified = bool(data.get('verified', False))
        token = data.get('token', None)

        if check_password_hash(g['token'], token):
            update_square(g, position, gen_square(name, email, verified))
            return jsonify({"success": True, "error": None}), 200
        elif g["squares"][position] == gen_square() and verified == False and name is not None and email is not None:
            if type(name) is not unicode or len(name) == 0 or type(email) is not unicode or len(email) == 0:
                return jsonify({"success": False, "error": "Name and email must be non-empty strings"}), 400
            else:
                update_square(g, position, gen_square(name, email))
                return jsonify({"success": True, "error": None}), 200
        else:
            return jsonify({"success": False, "error": "Not authorized to perform that action"}), 401
    except ValueError as e:
        return jsonify({"success": False, "error": "Must post square as {\"name\": \"john doe\", \"email\": \"j.doe@email.com\"}", "square": None}), 400


def set_square_values(g):
    g['afc_values'], g['nfc_values'] = get_random_values()
    save_game(g)
    return g

def save_game(g):
    game_file = os.path.join(data_path, "%s.json" % g['game_id'])
    with open(game_file, 'w') as outfile:
        json.dump(g, outfile)

def gen_square(name=None, email=None, verified=False):
    if verified is None:
        verified = False
    return {'name': name, 'email': email, 'verified': verified}

def load_game(game_id):
    game_file = os.path.join(data_path, "%s.json" % game_id)

    if os.path.isfile(game_file):
        with open(game_file) as json_data:
            g = json.load(json_data)
            return g
    else:
        return None

def create_game(name, password):
    g = {}
    g['game_name'] = name
    g['token'] = generate_password_hash(password)
    g['game_id'] = shortuuid.ShortUUID().random(length=6)
    g['afc_team'] = None
    g['nfc_team'] = None
    g['nfc_values'] = []
    g['afc_values'] = []
    g['squares'] = [gen_square() for x in range(100)]
    g['remaining_squares'] = 100
    save_game(g)
    return g

def get_random_values():
    lst = range(10)
    return random.sample(lst, 10), random.sample(lst, 10)

def get_square_number(afc_position, nfc_position):
    return afc_position * 10 + nfc_position

def get_afc_position(square_number):
    return square_number % 10

def get_nfc_position(square_number):
    return (square_number - get_afc_position(square_number)) // 10

def update_square(game, position, square=gen_square()):
    current_square = game['squares'][position]
    if current_square['name'] is not None and square['name'] is not None:
        game['squares'][position] = square
        save_game(game)
    elif current_square['name'] is not None and square['name'] is None:
        game['squares'][position] = gen_square()
        game['remaining_squares'] += 1
        save_game(game)
    elif current_square['name'] is None and square['name'] is not None:
        game['squares'][position] = square
        game['remaining_squares'] -= 1
        save_game(game)
    return game

