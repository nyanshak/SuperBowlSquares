from flask import Flask
from .views.game import game

app = Flask(__name__)
app.debug = True

app.register_blueprint(game, url_prefix='/game')
