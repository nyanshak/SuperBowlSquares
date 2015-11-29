from flask import Flask
from .views.game import game
from .views.api import api

app = Flask(__name__, static_url_path="/web")


def configure_app(conf={}):
    for k, v in conf.iteritems():
        app.config[k] = v


def register_blueprints():
    app.register_blueprint(api, url_prefix='/api/game')
    app.register_blueprint(game, url_prefix='/game')
