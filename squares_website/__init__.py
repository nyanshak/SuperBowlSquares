from flask import Flask
from .views.game import game
from .views.rest_game import rest_game

app = Flask(__name__, static_url_path = "/web")
app.debug = True

app.register_blueprint(rest_game, url_prefix='/rest/game')
app.register_blueprint(game, url_prefix='/game')
