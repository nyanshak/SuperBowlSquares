import os
import os.path
import json
from flask import Blueprint, jsonify, request, render_template
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import random

game = Blueprint('game', __name__)

@game.route('/<game_id>')
def show_game(game_id):
    return render_template("layout.html", game_id=game_id)

