import os
import re
import csv
import json
import urllib
import pandas as pd
import requests
from collections import Counter

# Use the search API to retrieve AJPS datasets
# Since there are < 1000 datasets, we do not need to page through results
url = 'https://dataverse.harvard.edu/api/search?q=*&subtree=ajps&type=dataset&start=0&per_page=1000'

resp = requests.get(url)
datasets = json.loads(resp.text)

# To save time on future runs, keep a cache of downloaded data
os.makedirs("cache", exist_ok=True)

exts = Counter()
for dataset in datasets['data']['items']:

    doi = dataset['global_id']

    # If we haven't retrieved this DOI, store it on disk. If we have, read the
    # cache file.
    cache_file = 'cache/' + urllib.parse.quote_plus(str(doi))
    if not os.path.isfile(cache_file):
        # print('Not using cache for %s' % doi)
        url = 'https://dataverse.harvard.edu/api/datasets/export?exporter=OAI_ORE&persistentId=' + doi
        resp = requests.get(url)
        try:
            r = json.loads(resp.text)
            with open(cache_file, 'w') as f:
                json.dump(r, f)
        except json.decoder.JSONDecodeError:
            print('There might be some problems with the link.', doi)
    else:
        # print('Using cache for %s' % doi)
        with open(cache_file, 'r') as f:
            r = json.load(f)

    # For each file, increment a counter for the extension

    files = r["ore:describes"]["ore:aggregates"]
    for f in files:
        ext = f['schema:name'].split('.')[-1].lower()
        exts[ext] += 1


# Output the extension
with open('file_extensions.txt', 'w') as f:
    print('extension,count,platform,type', file=f)
    for ext, cnt in exts.most_common():
        print('%s,%s' % (ext, cnt), file=f)


lang_dict = {'sh': 'bash', 'do': 'stata', 'jl': 'julia', 'py': 'python', 'R': 'R', 'r': 'R', 'c': 'C', 'cpp': 'C++',
                 'm': 'Matlab', 'f': 'fortran', 'f90': 'fortran', 'sas': 'SAS', 'java': 'Java', '2012': 'stata',
                 'sps': 'SPSS', 'Rhistory[1]': 'R', 'mx': 'Mathematica', 'replication': 'stata', 'php': 'PHP',
                 'nb': 'Mathematica', 'sci': 'Scilab', 'shp': "ArcGIS"}
final_data = []

for dataset in datasets['data']['items']:
    doi = dataset['global_id']
    cache_file = 'cache/' + urllib.parse.quote_plus(str(doi))
    try:
        with open(cache_file, 'r') as f:
            r = json.load(f)
    except FileNotFoundError:
        continue
    total_size = 0
    codebook = []
    verified_note = False
    pub_date = r["ore:describes"]["schema:datePublished"]
    title = r["ore:describes"]["citation:Title"][22:]
    files = r["ore:describes"]["ore:aggregates"]
    num_files = len(files)
    lang_num = {'bash': 0, 'stata': 0, 'julia': 0, 'python': 0, 'R': 0, 'C': 0, 'C++': 0, 'Matlab': 0, 'fortran': 0,
                'SAS': 0, 'Java': 0, 'SPSS': 0, 'Mathematica': 0, 'PHP': 0, 'Scilab': 0, 'ArcGIS': 0, 'code_sum': 0}
    for f in files:
        total_size += f['dvcore:filesize']
        file_extension = f['schema:name'].split('.')[-1]
        if re.match(r'.*codebook.*', f['schema:name'], re.I) is not None:
            codebook.append(re.match(r'.*codebook.*', f['schema:name'], re.I).group(0))
        try:
            if lang_dict[file_extension] in lang_num:
                lang_num[lang_dict[file_extension]] += 1
        except KeyError:
            continue
    lang_num['code_sum'] = sum(lang_num.values())
    total_size_kb = round(total_size / 1024, 2)
    try:
        note = r["ore:describes"]["citation:Notes"]
    except KeyError:
        note = "There is no note in this dataset."
    if 'independent verification' in note:
        verified_note = True
    out_dict = {'DOI': doi[4:], 'title': title, 'publication_date': pub_date, 'total_size_kb': total_size_kb,
                'num_files': num_files, 'codebook': codebook, 'verified_note': verified_note}
    out_dict.update(lang_num)
    final_data.append(out_dict)

out_data = pd.DataFrame(final_data, columns=['DOI', 'title', 'publication_date', 'total_size_kb', 'num_files',
                                             'codebook', 'verified_note', 'bash', 'stata', 'julia', 'python', 'R',
                                             'C', 'C++', 'Matlab', 'fortran', 'SAS', 'Java', 'SPSS', 'Mathematica',
                                             'PHP', 'Scilab', 'ArcGIS', 'code_sum'])
out_data.to_csv('try.csv', index=False)
