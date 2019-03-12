#A version of this script can be run as a cron job to download the metadata text file daily

import requests

url = 'http://data.glos.us/metadata/srv/eng/csv.search?'
r = requests.get(url, allow_redirects=True)
open('metadata.txt', 'wb').write(r.content)