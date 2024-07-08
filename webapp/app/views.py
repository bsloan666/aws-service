# Author: bsloan
"""
    Standard Flask Application endpoints
"""
import base64
import os
import re
import shutil
import uuid

from .compose import generate_notes
from flask import Flask, Blueprint, render_template, request, jsonify

from . import upaint

APP = Blueprint('app', __name__,
                template_folder='templates',
                static_folder='static')

RENDER_DIRECTORY = os.path.join('static', 'images')

app = app = Flask(__name__)

app.config['IMAGE_FOLDER'] = RENDER_DIRECTORY


def file_prefix_from_render_string(input_str):
    """
    make a unique-ish file name from the prompt
    """
    unfriendly = re.compile(r'[^a-zA-Z0-9]')
    outname = re.sub(unfriendly, '_', input_str)

    return "_".join(["render", outname[0:24], str(uuid.uuid4())[0:8]])


@APP.route('/render', methods=['GET', 'POST'])
def render():
    """
    The request will have a string and possibly some render parameters.
    convert the string to a rendered scene
    """
    render_string = request.form.get('prompt')
    resolution = request.form.get('resolution')
    width, height = [int(x)for x in re.split("x", resolution)]
    prefix = file_prefix_from_render_string(render_string)
    source_file_path = upaint.render(render_string, prefix, width, height)
    image_string = ""
    file_path = os.path.join(app.config['IMAGE_FOLDER'], "{0}.png".format(prefix))
    shutil.move(source_file_path, file_path)

    with open(file_path, "rb") as image_data:
        image_string = base64.b64encode(image_data.read()).decode("utf-8")

    if os.path.exists(file_path) and "render" in file_path:
        os.remove(file_path)

    return jsonify({"image_data": image_string})


@APP.route('/nsl', methods=['GET', 'POST'])
def index():
    """
    The request will have a string and possibly some render parameters.
    convert the string to a rendered scene
    """
    file_path = "static/images/logo.png"
    width, height = 720, 404
    resolution = "{0}x{1}".format(width, height)
    image_string = ""
    render_string = ""

    with open(file_path, "rb") as image_data:
        image_string = base64.b64encode(image_data.read()).decode("utf-8")

    return render_template(
        'nsl_gui.html',
        prompt=render_string,
        image_data=image_string,
        width=width,
        resolution=resolution)


@APP.route('/add2', methods=['GET', 'POST'])
def add2():
    """
    The request will have Left Hand Side and Right Hand Side arguments.
    Sum them and return
    """

    if request.method == 'POST':

        if 'submit' in request.form:
            lhs = float(request.form.get('lhs'))
            rhs = float(request.form.get('rhs'))
            result = lhs + rhs

            return render_template('add_gui.html',
                                   lhs=lhs,
                                   rhs=rhs,
                                   result=result)

    print("Entry Point!")
    return render_template('add_gui.html',
                           lhs="",
                           rhs="",
                           result="")


@APP.route('/thanks', methods=['GET', 'POST'])
def thanks():
    """
    The request will have Left Hand Side and Right Hand Side arguments.
    Sum them and return
    """

    if request.method == 'POST':

        if 'submit' in request.form:
            cfile = request.files['csvfile']

            address_line_1 = request.form.get('address_line_1')
            address_line_2 = request.form.get('address_line_2')
            disclaimer_line_1 = request.form.get('disclaimer_line_1')
            disclaimer_line_2 = request.form.get('disclaimer_line_2')
            content = generate_notes(
                cfile,
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                disclaimer_line_1=disclaimer_line_1,
                disclaimer_line_2=disclaimer_line_2)

            return render_template('blank.html', content=content)

    print("Entry Point!")
    return render_template('upload.html')
