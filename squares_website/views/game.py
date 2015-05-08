import os
import os.path
import json
from flask import Blueprint, jsonify
from datetime import datetime
import random

game = Blueprint('game', __name__)
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static/data")

@game.route('/<int:year>')
def show_game(year):
    now = datetime.utcnow().year
    if year == now:
        g = load_game(year, create=True)
        return jsonify(g), 200
    else:
        return "Not implemented yet", 404

def set_square_values(g):
    g['afc_values'], g['nfc_values'] = get_random_values()
    save_game(g)
    return g

def save_game(g):
    game_file = os.path.join(data_path, "%s.json" % g['year'])
    with open(game_file, 'w') as outfile:
        json.dump(g, outfile)

def gen_player(name=None, email=None, verified=False):
    return {'name': name, 'email': email, 'verified': verified}

def load_game(year, create=False):
    game_file = os.path.join(data_path, "%s.json" % year)

    if os.path.isfile(game_file):
        with open(game_file) as json_data:
            g = json.load(json_data)
            return g
    else:
        if create:
            g = {}
            g['year'] = year
            g['nfc_values'] = []
            g['afc_values'] = []
            g['squares'] = [gen_player() for x in range(100)]
            g['remaining_squares'] = 100
            save_game(g)
            return g
        else:
            return None

def get_random_values():
    lst = range(10)
    return random.sample(lst, 10), random.sample(lst, 10)

def get_square_number(afc_position, nfc_position):
    return afc_position * 10 + nfc_position

def get_afc_position(square_number):
    return square_number % 10

def get_nfc_position(square_number):
    return (square_number - get_afc_position(square_number)) // 10

def update_square(game, position, square={}):
    current_square = game['squares'][position]
    if current_square['name'] is not None and square['name'] is not None:
        game['squares'][position] = square
    elif current_square['name'] is not None and square['name'] is None:
        game['squares'][position] = gen_player()
        game['remaining_squares'] += 1
    elif current_square['name'] is None and square['name'] is not None:
        game['squares'][position] = square
        game['remaining_squares'] -= 1
    return game
        


