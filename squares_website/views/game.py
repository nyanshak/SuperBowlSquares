from flask import Blueprint, render_template

game = Blueprint('game', __name__)


@game.route('/<game_id>')
def show_game(game_id):
    return render_template("game.html", game_id=game_id)


@game.route('/create')
def create_game():
    return render_template("create.html")
