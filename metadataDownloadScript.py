#A version of this script can be run as a cron job to download the metadata text file daily
import pandas as pd
from io import StringIO
import numpy as np
import json
import requests

url = 'http://data.glos.us/metadata/srv/eng/csv.search?'
r = requests.get(url, allow_redirects=True)
open('metadata.txt', 'wb').write(r.content)

colnames = ["schema","uuid","id","title","abstract","keyword","link","responsibleParty","metadatacreationdate","geoBox","image","LegalConstraints","temporalExtent","parentId","datasetcreationdate","Constraints","SecurityConstraints"]
with open('metadata.txt',errors='ignore') as f:
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
	df['keyword'] = df['keyword'].str.replace('###', ' ', regex=True)
	df['link'] = df['link'].str.replace('###', ' ', regex=True)
	df['responsibleParty'] = df['responsibleParty'].str.replace('###', ' ', regex=True)
	df['geoBox'] = df['geoBox'].str.replace('###', ' ', regex=True)
	df['SecurityConstraints'] = df['SecurityConstraints'].str.replace('".', "", regex=True)

	export_csv = df.to_csv(r'clean_metadata2.csv', index = None, header=True)