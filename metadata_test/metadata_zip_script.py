# importing required modules 
from zipfile import ZipFile 
import xmltodict, json
import os

# specifying the zip file name 
file_name = "export-full-1556040614144.zip"

rootdir = os.path.dirname(os.path.realpath(__file__))
for subdir, dirs, files in os.walk(rootdir):
	for file in files:
		if file.endswith("zip"):
			file_name = file

  # opening the zip file in READ mode 
with ZipFile(file_name, 'r') as zip:   
    # extracting all the files 
    print('Extracting all the files now...') 
    zip.extractall() 
    print('Done!')

masterlist = []
exception = 1
success = 1
for subdir, dirs, files in os.walk(rootdir):
	for file in files:
		if file == "metadata.xml":
			document_file = open(os.path.join(subdir, file), "r") # Open a file in read-only mode
			original_doc = document_file.read() # read the file object
			document = xmltodict.parse(original_doc) # Parse the read document string
			strdict = json.dumps(document)
			d = json.loads(strdict)
			masterlist.append(d)


print(masterlist[50])
print(len(masterlist))
