from flask import Flask
from sum.views import SUM

application = Flask(__name__)


@application.route('/', methods=['GET', 'POST'])
def index():
    return 'Sum Server'


application.register_blueprint(SUM, url_prefix='/sum')
