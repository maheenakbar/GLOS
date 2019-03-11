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

import elasticsearch
from elasticsearch import Elasticsearch

host_url = ['https://search-glos-metadata-jy4xxxs6o26fgmdj7guj32nvje.us-east-2.es.amazonaws.com']
es_conn = Elasticsearch(host_url)

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
    advanced1 = StringField('Advanced1')
    advanced2 = StringField('Advanced2')
    advanced3 = StringField('Advanced3')
    advanced4 = StringField('Advanced4')
    submit = SubmitField('')
    
@mod.route('/')
def index():
    nameForm = NameForm()
    return render_template('nameform.html', form=nameForm, api_key=API_KEY, id_coords_list_of_tuples=json.dumps(id_coords_list_of_tuples))

@mod.route('/result', methods = ['GET', 'POST'])
def showDadForm():
    form=NameForm(request.form)
    if request.method == 'POST' and form.search.data != "":
        searchTerm = form.search.data

        results = es_conn.search(index="metadata", body={"query": {"match": {'keyword':searchTerm}}})
        for hit in results['hits']['hits']:
            print(hit['_source']['title'])
            print(hit['_source']['keyword'])
            print(hit['_source']['abstract'])
             

        #results = {'title':"sorry nothing here"}
        # results = [{'title':"sorry nothing here",'keyword':'nada','abstract':'also nada'}]
        # list_of_tups = id_coords_list_of_tuples

        # for record in metadata_dict:
        #     if type(metadata_dict[record]['keyword']) == type('str'):
        #         # print([w.upper() for w in metadata_dict[record]['keyword'].split()])
        #         if searchTerm.upper() in [w.upper() for w in metadata_dict[record]['keyword'].split()]:
        #             curr = metadata_dict[record]
        #             results.append(curr)
                # for tup in id_coords_list_of_tuples:
                #     if curr['id'] == str(tup[0]):
                #         list_of_tups = [tup]
                # try:
                #     list_of_tups = [[curr['id'], float(str(curr['geoBox']).split()[0]),float(str(curr['geoBox']).split()[2]),1]]
                # except: 
                #     pass

        ####################
        # Setting a cookie #
        ####################

        response = make_response('<h1>This document carries a cookie!</h1>')
        response.set_cookie('Search', searchTerm)
    
        # dadForm = DadForm()
        return render_template('result.html', searchTerm=searchTerm, api_key=API_KEY, id_coords_list_of_tuples=json.dumps(id_coords_list_of_tuples), results=results, results_len=len(results))
    else:
        flash('All fields are required!')
        return redirect(url_for('index'))