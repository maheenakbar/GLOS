#A version of this script can be run as a cron job to download the metadata text file regularly
import pandas as pd
from io import StringIO
import numpy as np
import json
import requests
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import numbers
import math
import certifi
from datetime import datetime

host_url = ['https://search-glos-metadata-jy4xxxs6o26fgmdj7guj32nvje.us-east-2.es.amazonaws.com']

def sanitize(value):
    if isinstance(value, numbers.Number) and math.isnan(value):
        return None
    else:
        return value

def parse_metadata(metadata_df):
    for index, row in metadata_df.iterrows():
        yield {'_id' : index,
        'schema' : sanitize(row['schema']),
        'uuid' : sanitize(row['uuid']), 
        'id' : sanitize(row['id']), 
        'title' : sanitize(row['title']), 
        'abstract' : sanitize(row['abstract']), 
        'keyword' : sanitize(row['keyword']),
        'link' : sanitize(row['link']),
        'responsibleParty' : sanitize(row['responsibleParty']),
        'metadatacreationdate' : sanitize(row['metadatacreationdate']),
        'geoBox' : sanitize(row['geoBox']),
        'image' : sanitize(row['image']),
        'LegalConstraints' : sanitize(row['LegalConstraints']),
        'temporalExtent' : sanitize(row['temporalExtent']),
        'parentId' : sanitize(row['parentId']),
        'datasetcreationdate' : sanitize(row['datasetcreationdate']),
        'Constraints' : sanitize(row['Constraints']),
        'SecurityConstraints' : sanitize(row['SecurityConstraints']),
        'Quality Score' : sanitize(row['Quality Score']),
        'Grade' : sanitize(row['Grade'])
              }
def quality_score(df):
    for row in df.iterrows():
        rows = row[1]
        qs = rows.count()
        try:
            kw = len(rows[5].split(','))

        except:
            kw = 0
        
        if kw < 2:
            pass
        elif kw >= 2 and kw < 4:
            qs+=1
        elif kw >= 4:
            qs+=2  
        try:
            abst = len(rows[4].split(' '))
    
        except:
            abst = 0
    
        if abst == 0:
            pass
        elif abst > 0 and abst < 100:
            qs+=1
        elif abst >= 100 and abst < 200:
            qs += 2
        elif abst > 200 and abst < 300:
            qs += 3
        elif abst >= 300:
            qs += 4
    
        try:
            link = len(rows[8].split())
        except:
            link = 0
        if link < 2:
            pass
        elif link >=2 and link < 4:
            qs += 1
        elif link >=4:
            qs += 2
            
        try:
            date = row[1]['metadatacreationdate']
            year = int(date[:4])
            year = datetime.today().year - year
            if year < 2:
                qs += 6
            elif year >=2 and year < 4:
                qs += 4
            elif year >= 4 and year < 6:
                qs += 2
            
        except:
            pass

        df.at[row[0], 'Quality Score'] = qs
    
    return (df)

def grade(df):
    for row in df.iterrows():
        rows = row[1]
        qs = rows[17]
    
        if qs < 13:
            grade = 'F'
        elif qs >= 13 and qs < 18:
            grade = 'D'
        elif qs >= 18 and qs < 23:
            grade = 'C'
        elif qs >= 23 and qs < 28:
            grade = 'B'
        elif qs >= 28:
            grade = 'A'
        df.at[row[0], 'Grade'] = grade
    return (df)

url = 'http://data.glos.us/metadata/srv/eng/csv.search?'
r = requests.get(url, allow_redirects=True)
open('metadata.txt', 'wb').write(r.content)

with open('metadata.txt',errors='ignore') as f:
    colnames = f.readline().strip().replace('"','').split(",")

    contents = f.read() # type bytes
    df = pd.read_csv(StringIO(contents), sep='","',skiprows=[0],index_col=False,names=colnames, engine='python')
    df['schema'] = df['schema'].str.replace('"', ' ', regex=True)
    df['abstract'] = df['abstract'].str.replace('<p>', ' ', regex=True)
    df['abstract'] = df['abstract'].str.replace('</p>', ' ', regex=True)
    df['abstract'] = df['abstract'].str.replace('<h4>', ' ', regex=True)
    df['abstract'] = df['abstract'].str.replace('</h4>', ' ', regex=True)
    df['abstract'] = df['abstract'].str.replace('<span>', ' ', regex=True)
    df['abstract'] = df['abstract'].str.replace('</span>', ' ', regex=True)
    df['keyword'] = df['keyword'].str.replace('###', ',', regex=True)
    df['link'] = df['link'].str.replace('###', ' ', regex=True)
    df['responsibleParty'] = df['responsibleParty'].str.replace('###', ' ', regex=True)
    df['geoBox'] = df['geoBox'].str.replace('###', ' ', regex=True)
    df['SecurityConstraints'] = df['SecurityConstraints'].str.replace('".', "", regex=True)

    df = quality_score(df)
    df = grade(df)

es_conn = Elasticsearch(host_url, ca_certs = certifi.where())

bulk(es_conn, parse_metadata(df), index = 'metadata', doc_type = 'record')

export_csv = df.to_csv(r'clean_metadata2.csv', index = None, header=True)

print ('Indexing Successful')

