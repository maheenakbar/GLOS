from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, \
                  abort, jsonify
from app.core.repositor import *
from flask import Flask, request, render_template, redirect, url_for, flash, make_response
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Required

import requests
import json
import pandas as pd

df = pd.read_csv('clean_metadata.csv') 
df = df.transpose()
metadata_dict = df.to_dict()
id_coords_list_of_tuples = []
for record in metadata_dict.keys():
    if type(metadata_dict[record]['geoBox']) == str:
        id_coords_list_of_tuples.append([metadata_dict[record]['id'],float(metadata_dict[record]['geoBox'].split()[0]),float(metadata_dict[record]['geoBox'].split()[2]),1])

mod = Blueprint('core', __name__)

class NameForm(FlaskForm):
    search = StringField('What is your search term?', validators=[Required()])
    submit = SubmitField('Submit')
    
@mod.route('/')
def index():
    nameForm = NameForm()
    return render_template('nameform.html', form=nameForm, api_key=API_KEY, id_coords_list_of_tuples=json.dumps(id_coords_list_of_tuples))

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