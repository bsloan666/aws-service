# Author: bsloan
"""
    Standard Flask Application endpoints
"""
# import base64
from datetime import datetime
import os
import re
import shutil
import uuid

from .compose import generate_notes
from flask import Flask, Blueprint, render_template, request

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


@APP.route('/nsl', methods=['GET', 'POST'])
def parse_scene():
    """
    The request will have a string and possibly some render parameters.
    convert the string to a rendered scene
    """
    render_string = ""
    prefix = "dummy"
    file_path = "static/images/logo.png"
    width, height = 720, 404
    resolution = "{0}x{1}".format(width, height)
    # image_string = ""
    if request.method == 'POST':
        render_string = request.form.get('prompt')
        resolution = request.form.get('resolution')
        width, height = [int(x)for x in re.split("x", resolution)]
        if 'submit' in request.form:
            prefix = file_prefix_from_render_string(render_string)
            source_file_path = upaint.render(render_string, prefix, width, height)

            file_path = os.path.join(app.config['IMAGE_FOLDER'], "{0}.png".format(prefix))
            shutil.move(source_file_path, file_path)

    # with open(file_path, "rb") as image_data:
    #    image_string = base64.b64encode(image_data.read()).decode("utf-8")

    files = os.listdir(os.path.dirname(file_path))
    now = datetime.now()
    removed = []
    for basename in files:
        del_path = os.path.join(os.path.dirname(file_path), basename)
        modtime = int(os.path.getmtime(del_path))
        hour_ago = int(now.timestamp()) - 3600
        print("MODTIME:", modtime, "HOUR_AGO:", hour_ago)
        if os.path.exists(del_path) and "render" in del_path and  modtime < hour_ago:
            os.remove(del_path)
            removed.append(del_path)

    print("REMOVED:")
    for path in removed:
        print("   ", path)

    if not removed:
        print("Nothing to remove!")

    return render_template(
        'nsl_gui.html',
        prompt=render_string,
        # image_data=image_string,
        render=file_path,
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
