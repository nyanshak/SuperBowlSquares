from config import conf
from squares_website import app, configure_app, register_blueprints

configure_app(conf)
register_blueprints()
app.debug = True
app.run()
