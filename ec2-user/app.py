from flask import Flask
app = Flask(__name__)

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, \
                  abort, jsonify, flash, make_response

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Required

import requests
import json

from repositor import *
from config import *
import pandas as pd
import elasticsearch
from elasticsearch import Elasticsearch

app.config['SECRET_KEY'] = SECRET_KEY
host_url = ['https://search-glos-metadata-jy4xxxs6o26fgmdj7guj32nvje.us-east-2.es.amazonaws.com']
es_conn = Elasticsearch(host_url)

df = pd.read_csv('clean_metadata.csv') 
df = df.transpose()
metadata_dict = df.to_dict()
# print(metadata_dict)
id_coords_list_of_tuples = []
for record in metadata_dict.keys():
    if type(metadata_dict[record]['geoBox']) == str:
        try:
            s1 = set(metadata_dict[record]['title'].upper().split())
            s2 = set(['BUOY'])
            if s1.intersection(s2):
                color = 'blue'
            else:
                color = 'red'
            id_coords_list_of_tuples.append([metadata_dict[record]['id'],float(metadata_dict[record]['geoBox'].split()[0]),float(metadata_dict[record]['geoBox'].split()[2]),1, metadata_dict[record]['title'], metadata_dict[record]['link'].split()[0], color])
            
        except:
            pass

# print(id_coords_list_of_tuples)

class SearchForm(FlaskForm):
    search = StringField('What is your search term?', validators=[Required()])
    advanced1 = StringField('Advanced1')
    advanced2 = StringField('Advanced2')
    advanced3 = StringField('Advanced3')
    advanced4 = StringField('Advanced4')
    submit = SubmitField('')
    
@app.route('/')
def index():
    searchForm = SearchForm()
    return render_template('searchform.html', form=searchForm, api_key=API_KEY, id_coords_list_of_tuples=json.dumps(id_coords_list_of_tuples))

@app.route('/result', methods = ['GET', 'POST'])
def resultSearchForm():
    form=SearchForm(request.form)
    if request.method == 'POST' and form.search.data != "":
        searchTerm = form.search.data

        results = es_conn.search(index="metadata", body={"query": {"match": {'keyword':searchTerm}}})
        resultPlotList = []
        for hit in results['hits']['hits']:
            try:
                hit['geoList'] = hit['_source']['geoBox'].split()
                hit['geoList'] = [float(i) for i in hit['geoList']]
                hit['geoList'].append(hit['_source']['title'])
                # print(hit['geoList'])
      
                resultPlotList.append(hit['geoList'])
            except:
                pass
            # print(hit['geoList'])
             
        # print(resultPlotList)

        return render_template('result.html', searchTerm=searchTerm, api_key=API_KEY, id_coords_list_of_tuples=json.dumps(id_coords_list_of_tuples), results=results, results_len=len(results), searchResults=json.dumps(resultPlotList))
    else:
        flash('All fields are required!')
        return redirect(url_for('index'))



##############################
# Use this for running locally
##############################
if __name__ == '__main__':
    app.run(debug=True)


##############################
# Use this for running on AWS
##############################
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=80)