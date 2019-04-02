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
            if int(metadata_dict[record]['metadatacreationdate'][:4])>2017:
                active = '<i class="material-icons md-24 right">whatshot</i>'
            else:
                active = ''
        except:
            active = 'inactive'
        try:
            s1 = set(metadata_dict[record]['title'].upper().split())
            s2 = set(['BUOY'])
            if s1.intersection(s2):
                color = 'blue'
            else:
                color = 'red'
            # print(active)
            id_coords_list_of_tuples.append([metadata_dict[record]['id'],float(metadata_dict[record]['geoBox'].split()[0]),float(metadata_dict[record]['geoBox'].split()[2]),1, metadata_dict[record]['title'], metadata_dict[record]['link'].split()[0], color, active])
        except:
            pass
# metadata_dict['record']['metadatacreationdate'], metadata_dict['record']['datasetcreationdate']
# print(id_coords_list_of_tuples)


class SearchForm(FlaskForm):
    search = StringField('What is your search term?', validators=[Required()])
    advanced1 = StringField('Title includes')
    advanced2 = StringField('Link includes')
    advanced3 = StringField('Abstract includes')
    advanced4 = StringField('Year range')
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

        # if there are no inputs in the advanced search fields
        if (form.advanced1.data == "" and form.advanced2.data == "" and form.advanced3.data == "" and form.advanced4.data == ""):
            results = es_conn.search(index="metadata", body={"query": {"match": {'keyword':searchTerm}}})
            #results = es_conn.search(index="metadata", doc_type = 'record', body={"query": {"multi_match": {'query': searchTerm, 'fields': ['schema', 'title', 'abstract', 'keyword']}}})

        else:
            titleSearch = form.advanced1.data
            linkSearch = form.advanced2.data
            abstractSearch = form.advanced3.data
            yearSearch = form.advanced4.data

            #bodyString2 = {"query": { "bool": { "must": [ { "range": { float("metadatacreationdate"[0:4]): float(yearSearch[0:4])-float(yearSearch[5:9]) }}, { "match": { "keyword": searchTerm }}, { "match": { "title": titleSearch }}, { "match": { "link": linkSearch }}, { "match": { "abstract": abstractSearch}}]}}}

            #bodyString2 = {"query": { "bool": { "must": [ { "range": { float("metadatacreationdate"[0:4]): { "gte": int(yearSearch[0:4]), "lte": int(yearSearch[5:9]) }}}, { "match": { "keyword": searchTerm }}, { "match": { "title": titleSearch }}, { "match": { "link": linkSearch }}, { "match": { "abstract": abstractSearch}}]}}}

            if (titleSearch and linkSearch and abstractSearch):

                bodyString = {"query": { "bool": { "must": [ { "match": { "keyword": searchTerm }}, { "match": { "title": titleSearch }}, { "match": { "link": linkSearch }}, { "match": { "abstract": abstractSearch}}]}}}
                results = es_conn.search(index="metadata", body=bodyString)

            elif (titleSearch and linkSearch and not abstractSearch):
                bodyString = {"query": { "bool": { "must": [ { "match": { "keyword": searchTerm }}, { "match": { "title": titleSearch }}, { "match": { "link": linkSearch }}]}}}
                results = es_conn.search(index="metadata", body=bodyString)

            elif (titleSearch and not linkSearch and abstractSearch):
                bodyString = {"query": { "bool": { "must": [ { "match": { "keyword": searchTerm }}, { "match": { "title": titleSearch }}, { "match": { "abstract": abstractSearch}}]}}}
                results = es_conn.search(index="metadata", body=bodyString)

            elif (titleSearch and not linkSearch and not abstractSearch):
                bodyString = {"query": { "bool": { "must": [ { "match": { "keyword": searchTerm }}, { "match": { "title": titleSearch }}]}}}
                results = es_conn.search(index="metadata", body=bodyString)

            elif (not titleSearch and linkSearch and abstractSearch):
                bodyString = {"query": { "bool": { "must": [ { "match": { "keyword": searchTerm }}, { "match": { "link": linkSearch }}, { "match": { "abstract": abstractSearch}}]}}}
                results = es_conn.search(index="metadata", body=bodyString)

            elif (not titleSearch and linkSearch and not abstractSearch):
                bodyString = {"query": { "bool": { "must": [ { "match": { "keyword": searchTerm }}, { "match": { "link": linkSearch }}]}}}
                results = es_conn.search(index="metadata", body=bodyString)

            elif (not titleSearch and not linkSearch and abstractSearch):
                bodyString = {"query": { "bool": { "must": [ { "match": { "keyword": searchTerm }}, { "match": { "abstract": abstractSearch}}]}}}
                results = es_conn.search(index="metadata", body=bodyString)

            
            
            
        
        #for item in results.keys:
        #    print (item)
        resultPlotList = []

        for hit in results['hits']['hits']:
            try:
                hit['geoList'] = hit['_source']['geoBox'].split()
                hit['geoList'] = [float(i) for i in hit['geoList']]
                hit['geoList'].append(hit['_source']['title'])
                #print(hit['geoList'])
      
                resultPlotList.append(hit['geoList'])
            except:
                pass
            # print(hit['geoList'])
             
        # print(resultPlotList)


        return render_template('result.html', searchTerm=searchTerm, api_key=API_KEY, id_coords_list_of_tuples=json.dumps(id_coords_list_of_tuples), results=results, results_len=len(results), searchResults=json.dumps(resultPlotList),form=form)
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