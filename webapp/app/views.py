# Author: bsloan 
"""
    Shotgun Action Menu Item for Product Generation
    (using Product Generator)
    Standard Flask Application endpoints
"""
import os
import json
import sys

from flask import Blueprint, render_template, request


SUM = Blueprint('sum', __name__,
                template_folder='templates',
                static_folder='static')


@SUM.route('/add2', methods=['GET', 'POST'])
def add2():
    """
    The request will have Left Hand Side and Right Hand Side arguments.
    Sum them and return 
    """

    versions = []

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


        
