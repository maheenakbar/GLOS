from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, \
                  abort, jsonify
from app.core.repository import *
from flask import Flask, request, render_template, redirect, url_for, flash, make_response
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Required
from app.core.ignore.apikey import *

import requests
import json
mod = Blueprint('core', __name__)

# @mod.route('/')
# def index():
#   repository = Repository()
#   return (render_template('core/index.html', resources=repository.getResources()))

class NameForm(FlaskForm):
    search = StringField('What is your search term?', validators=[Required()])
    submit = SubmitField('Submit')
    
############################
# Two error handler routes #
############################

# @app.errorhandler(404)
# def four_oh_four(error):
#     return render_template('thats_a_404.html'), 404

# @app.errorhandler(403)
# def four_oh_three(error):
#     return render_template('thats_a_503.html'), 403

@mod.route('/')
def index():
    nameForm = NameForm()
    return render_template('nameform.html', form=nameForm, api_key=API_KEY)

@mod.route('/result', methods = ['GET', 'POST'])
def showDadForm():
    form=NameForm(request.form)
    if request.method == 'POST' and form.search.data != "":
        searchTerm = form.search.data

    ####################
    # Setting a cookie #
    ####################

        response = make_response('<h1>This document carries a cookie!</h1>')
        response.set_cookie('Search', searchTerm)
    
        # dadForm = DadForm()
        return render_template('result.html', searchTerm=searchTerm)
    else:
        flash('All fields are required!')
        return redirect(url_for('index'))