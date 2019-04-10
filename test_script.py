with open('metadata.txt',errors='ignore') as f:
	colnames = f.readline().strip().split(",")
	# contents = f.read() # type bytes
	# df = pd.read_csv(StringIO(contents), sep='","',skiprows=[0],index_col=False,names=colnames, engine='python')
	
	# df['schema'] = df['schema'].str.replace('"', ' ', regex=True)
	# #df['abstract'] = df['abstract'].str.replace('<\s*[^>]*>', ' ', regex=True)
	# df['abstract'] = df['abstract'].str.replace('<p>', ' ', regex=True)
	# df['abstract'] = df['abstract'].str.replace('</p>', ' ', regex=True)
	# df['abstract'] = df['abstract'].str.replace('<h4>', ' ', regex=True)
	# df['abstract'] = df['abstract'].str.replace('</h4>', ' ', regex=True)
	# df['abstract'] = df['abstract'].str.replace('<span>', ' ', regex=True)
	# df['abstract'] = df['abstract'].str.replace('</span>', ' ', regex=True)
	# df['keyword'] = df['keyword'].str.replace('###', ',', regex=True)
	# df['link'] = df['link'].str.replace('###', ' ', regex=True)
	# df['responsibleParty'] = df['responsibleParty'].str.replace('###', ' ', regex=True)
	# df['geoBox'] = df['geoBox'].str.replace('###', ' ', regex=True)
	# df['SecurityConstraints'] = df['SecurityConstraints'].str.replace('".', "", regex=True)