import os
import os.path
import json
from flask import Blueprint, jsonify, request, render_template
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import random

game = Blueprint('game', __name__)

@game.route('/<int:year>')
def show_game(year):
    return render_template("layout.html", year=year)


