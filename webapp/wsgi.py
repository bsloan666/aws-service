from flask import Flask
from app.views import APP

application = Flask(__name__)


@application.route('/', methods=['GET', 'POST'])
def index():
    return 'App Server'


application.register_blueprint(APP, url_prefix='/app')
