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

#secret key is necessary for flask-form operation. It works sort of like a checksum.
app.config['SECRET_KEY'] = SECRET_KEY
#this value will be replaced by the AWS elasticsearch instance URL.
host_url = ['https://search-glos-metadata-jy4xxxs6o26fgmdj7guj32nvje.us-east-2.es.amazonaws.com']
#establish a connection to the elasticsearch instance
es_conn = Elasticsearch(host_url)

#create a dataframe of the cleaned metadata export.
df = pd.read_csv('clean_metadata.csv')
#rotate the dataframe 90 degrees. 
df = df.transpose()
#create a python dictionary from the dataframe
metadata_dict = df.to_dict()
#create an empty list that will hold dictionaries representing metadata records.
id_coords_list_of_tuples = []
#iterate through the records in the main dictionary and append records with geobox values to the list.
for record in metadata_dict.keys():
	if type(metadata_dict[record]['geoBox']) == str:
		try:
			#check if the record has a metadata creation date greater than 2017
			if int(metadata_dict[record]['metadatacreationdate'][:4])>2017:
				active = '<i class="material-icons md-24 right">whatshot</i>'
			else:
				active = ''
		except:
			#call it inactive if not.
			active = 'inactive'
		try:
			#assign colors for the markers representing metadata records.
			s1 = set(metadata_dict[record]['title'].upper().split())
			s2 = set(['BUOY'])
			if s1.intersection(s2):
				color = 'blue'
			else:
				color = 'red'
			#add the record to the list of records.
			id_coords_list_of_tuples.append([metadata_dict[record]['id'],float(metadata_dict[record]['geoBox'].split()[0]),float(metadata_dict[record]['geoBox'].split()[2]),1, metadata_dict[record]['title'], metadata_dict[record]['link'].split()[0], color, active])
		except:
			#don't ad the record if it does not meet requirements
			pass

#The following class defines the search form.
class SearchForm(FlaskForm):
	#a main search term is required and will cause a redirect to the search page with a popup message if not set.
	search = StringField('What is your search term?', validators=[Required()])
	advanced1 = StringField('Title includes')
	advanced2 = StringField('Link includes')
	advanced3 = StringField('Abstract includes')
	advanced4 = StringField('Year range')
	submit = SubmitField('')
	
#The index route is defined by the index function that renders a template with a search form.
@app.route('/')
def index():
	searchForm = SearchForm()
	return render_template('searchform.html', form=searchForm, api_key=API_KEY, id_coords_list_of_tuples=json.dumps(id_coords_list_of_tuples))

#The result route is defined by the resultSearchForm function that renders a results page template and uses the search form again.
@app.route('/result', methods = ['GET', 'POST'])
def resultSearchForm():
	form=SearchForm(request.form)
	if request.method == 'POST':
		if form.search.data != "" and request.form['action'] == 'custom' :
			searchTerm = form.search.data

			# if there are no inputs in the advanced search fields
			if (form.advanced1.data == "" and form.advanced2.data == "" and form.advanced3.data == "" and form.advanced4.data == ""):
				results = es_conn.search(index="metadata", body={"query": {"match": {'keyword':searchTerm}}})
			
			else:
				#take values from the advances search fields and assign to variables.
				titleSearch = form.advanced1.data
				linkSearch = form.advanced2.data
				abstractSearch = form.advanced3.data
				yearSearch = form.advanced4.data

			
				#The following block determines logic for creating a search string and sending to AWS ElasticSearch.
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

		# the next three elif blocks are for when one of the canned queries is clicked on, it searches with specific terms related
		# to the canned query
		elif request.form['action'] == 'health':
			searchTerm = "health"
			bodyString = {"query": { "bool": { "must": [ { "match": { "keyword": searchTerm }}, { "match": { "abstract": "great lakes"}}]}}}
			results = es_conn.search(index="metadata", body=bodyString)


		elif request.form['action'] == 'cold':
			searchTerm = "temperature"
			bodyString = {"query": { "bool": { "must": [ { "match": { "keyword": searchTerm }}, { "match": { "abstract": "erie"}}]}}}
			results = es_conn.search(index="metadata", body=bodyString)


		elif request.form['action'] == 'fishing': 
			searchTerm = "fishing"
			bodyString = {"query": { "bool": { "must": [ { "match": { "keyword": searchTerm }}]}}}
			results = es_conn.search(index="metadata", body=bodyString)   
			


		#return render_template('result.html', searchTerm=searchTerm, api_key=API_KEY, id_coords_list_of_tuples=json.dumps(id_coords_list_of_tuples), results=results, results_len=len(results), searchResults=json.dumps(resultPlotList),form=form)
		else:
			flash('All fields are required!')
			return redirect(url_for('index'))

		#result plot list is sent to the results page so that markers can be plotted on the smaller map representing results.
		resultPlotList = []

		#Iterate through the results and append 'geolist' values to resultPlotList
		for hit in results['hits']['hits']:
			try:
				hit['geoList'] = hit['_source']['geoBox'].split()
				hit['geoList'] = [float(i) for i in hit['geoList']]
				hit['geoList'].append(hit['_source']['title'])
				
	  
				resultPlotList.append(hit['geoList'])
			except:
				pass

		return render_template('result.html', searchTerm=searchTerm, api_key=API_KEY, id_coords_list_of_tuples=json.dumps(id_coords_list_of_tuples), results=results, results_len=len(results), searchResults=json.dumps(resultPlotList),form=form)



##############################
# Use this for running locally
##############################
# if __name__ == '__main__':
# 	app.run(debug=True)


##############################
# Use this for running on AWS
##############################
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)