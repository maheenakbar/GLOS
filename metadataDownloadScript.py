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

host_url = ['https://search-glos-metadata-jy4xxxs6o26fgmdj7guj32nvje.us-east-2.es.amazonaws.com']

def sanitize(value):
    if isinstance(value, numbers.Number) and math.isnan(value):
        return None
    else:
        return value

def parse_metadata(metadata_df):
    for index, row in metadata_df.iterrows():
        yield {'_id' : index,
        'schema' : sanitize(row[0]),
        'uuid' : sanitize(row[1]), 
        'id' : sanitize(row[2]), 
        'title' : sanitize(row[3]), 
        'abstract' : sanitize(row[4]), 
        'keyword' : sanitize(row[5]),
        'link' : sanitize(row[6]),
        'responsibleParty' : sanitize(row[7]),
        'metadatacreationdate' : sanitize(row[8]),
        'geoBox' : sanitize(row[9]),
        'image' : sanitize(row[10]),
        'LegalConstraints' : sanitize(row[11]),
        'temporalExtent' : sanitize(row[12]),
        'parentId' : sanitize(row[13]),
        'datasetcreationdate' : sanitize(row[14]),
        'Constraints' : sanitize(row[15]),
        'SecurityConstraints' : sanitize(row[16])
              }

url = 'http://data.glos.us/metadata/srv/eng/csv.search?'
r = requests.get(url, allow_redirects=True)
open('metadata.txt', 'wb').write(r.content)

# colnames = ["schema","uuid","id","title","abstract","keyword","link","responsibleParty","metadatacreationdate","geoBox","image","LegalConstraints","temporalExtent","parentId","datasetcreationdate","Constraints","SecurityConstraints"]
with open('metadata.txt',errors='ignore') as f:
    colnames = f.readline().strip().replace('"','').split(",")

    contents = f.read() # type bytes
    df = pd.read_csv(StringIO(contents), sep='","',skiprows=[0],index_col=False,names=colnames, engine='python')
    df['schema'] = df['schema'].str.replace('"', ' ', regex=True)
    #df['abstract'] = df['abstract'].str.replace('<\s*[^>]*>', ' ', regex=True)
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

es_conn = Elasticsearch(host_url, ca_certs = certifi.where())

bulk(es_conn, parse_metadata(df), index = 'metadata', doc_type = 'record')

export_csv = df.to_csv(r'clean_metadata2.csv', index = None, header=True)

