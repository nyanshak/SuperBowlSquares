from __future__ import unicode_literals, print_function
import copy
import os
import os.path
import json
from flask import Blueprint, jsonify, request
import random
import shortuuid
import smtplib
import sys

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

api = Blueprint('api', __name__)
config = {}
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

if sys.version_info < (3,):
    text_type = unicode
    binary_type = str
else:
    text_type = str
    binary_type = bytes


@api.record
def record_params(setup_state):
    app = setup_state.app
    global config
    for k, v in app.config.iteritems():
        config[k] = v


@api.route('/create', methods=['POST'])
def make_game():
    resp = {
        "success": False,
        "error": ("Must pass game_name, email in post data"
                  ", ex: {\"game_name\": \"my_awesome_game\", "
                  "\"email\": \"user@example.com\"}"),
        "game": None
    }
    try:
        data = json.loads(request.data)
    except ValueError:
        return jsonify(resp), 400

    game_name = data.get('game_name', None)
    email = data.get('email', None)

    is_invalid_str = lambda x: type(x) is not text_type or len(x) == 0
    if is_invalid_str(game_name) or is_invalid_str(email):
        return jsonify(resp), 400

    g = create_game(game_name, email)
    try:
        from_addr = config.get('email_user', None)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Your board has been created!'
        msg['From'] = from_addr
        msg['To'] = email

        base_url = request.url.rstrip('api/game/create')
        user_link = os.path.join(base_url, "game/{}".format(g["game_id"]))
        print(user_link)
        raise Exception()
        admin_link = "{}/admin/{}".format(user_link, g['token'])

        text = ("You've created a squares board.\n"
                "Send users this link to sign up: {}\n"
                "This is the admin link (keep it secret!): {}"
                ).format(user_link, admin_link)
        html = "<html><head></head><body>{}</body></html>".format(text)
        text_part = MIMEText(text, 'plain')
        html_part = MIMEText(html, 'html')
        # Per RFC 2046, the last part of a multipart message is preferred
        # so we should attach html last
        msg.attach(text_part)
        msg.attach(html_part)

        pwd = config.get('email_pass', None)
        server_addr = config.get('email_server', None)
        send_email(from_addr, pwd, email, server_addr, msg.as_string())
    except Exception as e:
        print("REACHED:", e)

    resp['success'] = True
    resp['error'] = None
    resp['game'] = g
    return jsonify(resp), 200


@api.route('/<game_id>', methods=['GET'])
def show_game(game_id):
    g = load_game(game_id)

    if g is None:
        resp = {
            "success": False,
            "error": "That game does not exist",
            "game": None
        }
        return jsonify(resp), 404
    else:
        resp = {
            "success": True,
            "error": None,
            "game": g
        }
        return jsonify(resp), 200


@api.route('/<game_id>/numbers', methods=['POST'])
def set_numbers(game_id):
    g = load_game(game_id, filtered=False)

    resp = {"success": False, "error": None}
    if g is None:
        resp['error'] = "No game for that game_id"
        resp['game'] = None
        return jsonify(resp), 404
    if len(g['afc_values']) and len(g['nfc_values']):
        resp['error'] = 'Numbers already set'
        resp['game'] = filter_game(g)
        return jsonify(resp), 400

    try:
        data = json.loads(request.data)
    except ValueError:
        resp['error'] = ("Must post token, ex: {"
                         "\"token\": \"token\"}")
        resp['game'] = filter_game(g)
        return jsonify(resp), 400

    if check_auth(data, g):
        g = set_square_values(g)
        resp['success'] = True
        resp['game'] = g
        return jsonify(resp), 200
    else:
        resp['error'] = "Not authorized to perform that action"
        resp['game'] = filter_game(g)
        return jsonify(resp), 401


@api.route('/<game_id>/teams', methods=['POST'])
def set_teams(game_id):
    g = load_game(game_id, filtered=False)

    resp = {
        'success': False,
        'error': None
    }
    if g is None:
        resp['error'] = "No game for that game_id"
        return jsonify(resp), 404
    try:
        data = json.loads(request.data)
    except ValueError:
        resp['error'] = ("Must post AFC and NFC team names, ex: "
                         "{\"afc_team\": \"Steelers\", \"nfc_team\": "
                         "\"Cowboys\", \"token\": \"token\"}")
        return jsonify(resp), 400

    afc_team = data.get('afc_team', None)
    nfc_team = data.get('nfc_team', None)

    if check_auth(data, g):
        g['afc_team'] = afc_team
        g['nfc_team'] = nfc_team
        save_game(g)
        resp['success'] = True
        return jsonify(resp), 200
    else:
        resp['error'] = "Not authorized to perform that action"
        return jsonify(resp), 401


@api.route('/<game_id>/square/<int:position>', methods=['POST'])
def square(game_id, position):

    resp = {
        "success": False,
        "error": None,
        "square": None
    }
    if position > 99 or position < 0:
        resp['error'] = "Position must be a value between 0 and 99"
        return jsonify(resp), 400
    g = load_game(game_id, filtered=False)
    if g is None:
        resp['error'] = "No game for that game_id"
        return jsonify(resp), 404
    try:
        data = json.loads(request.data)
    except ValueError:
        resp['error'] = ("Must post square as {\"name\": "
                         "\"john doe\", \"email\": \"j.doe@email.com\"}")
        return jsonify(resp), 400

    name = data.get('name', None)
    email = data.get('email', None)
    verified = bool(data.get('verified', False))

    if check_auth(data, g):
        update_square(g, position, gen_square(name, email, verified))
        resp['success'] = True
        return jsonify(resp), 200
    elif g["squares"][position] == gen_square():
        valid_str = lambda x: type(x) is text_type and len(x) == 0
        if not valid_str(name) or not valid_str(email):
            resp['error'] = "Name and email must be non-empty strings"
            return jsonify(resp), 400
        else:
            update_square(g, position, gen_square(name, email))
            resp['success'] = True
            return jsonify(resp), 200
    else:
        resp['error'] = "Not authorized to perform that action"
        return jsonify(resp), 401


def set_square_values(g):
    g['afc_values'], g['nfc_values'] = get_random_values()
    save_game(g)
    return g


def gen_square(name=None, email=None, verified=False):
    if verified is None:
        verified = False
    return {'name': name, 'email': email, 'verified': verified}


def load_game(game_id, filtered=True):
    game_file = os.path.join(data_path, "%s.json" % game_id)

    if os.path.isfile(game_file):
        with open(game_file) as json_data:
            g = json.load(json_data)
            if filtered:
                return filter_game(g)
            else:
                return g
    else:
        return None


def create_game(game_name, email):
    g = {}
    g['game_name'] = game_name
    g['admin_email'] = email
    g['token'] = generate_uuid(length=6)
    g['game_id'] = generate_uuid(length=6)
    g['afc_team'] = None
    g['nfc_team'] = None
    g['nfc_values'] = []
    g['afc_values'] = []
    g['squares'] = [gen_square() for x in range(100)]
    g['remaining_squares'] = 100
    save_game(g)
    return g


def save_game(g):
    game_file = os.path.join(data_path, "%s.json" % g['game_id'])
    with open(game_file, 'w') as outfile:
        json.dump(g, outfile, indent=4)


def filter_game(g):
    g1 = copy.deepcopy(g)
    if 'token' in g1:
        del g1['token']
    if 'admin_email' in g1:
        del g1['admin_email']
    return g1


def get_random_values():
    nums = range(10)
    return random.sample(nums, 10), random.sample(nums, 10)


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


def generate_uuid(length=6):
    return shortuuid.ShortUUID().random(length)


def check_auth(data, game):
    user_token = data.get('token', None)
    return user_token == game['token']


def send_email(
        from_addr=None,
        pwd=None,
        to_addr=None,
        server_addr=None,
        msg=None):
    server = smtplib.SMTP(server_addr)
    server.ehlo()
    server.starttls()
    server.login(from_addr, pwd)
    server.sendmail(from_addr, to_addr, msg)
    server.close()
