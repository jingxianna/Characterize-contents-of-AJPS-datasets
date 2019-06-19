import requests
from bs4 import BeautifulSoup
import os
import json
import pandas as pd


def get_doi(page_number):
    try:
        url = "https://dataverse.harvard.edu/dataverse/ajps?q=&types=dataverses%3Adatasets&sort=dateSort&order=desc&page=" + str(page_number)
        htmlcontent = requests.get(url, headers=headers, timeout=30)
        htmlcontent.raise_for_status()
        htmlcontent.encoding = 'utf-8'
        return htmlcontent.text
    except:
        return "Request failed."


def parseHTML(content):
    d_list = []
    soup = BeautifulSoup(content, 'html.parser')
    body = soup.body
    resultsTable = body.find('table', attrs={'id': 'resultsTable'})
    for result in resultsTable.find_all('div', attrs={'class': 'resultDatasetCitationBlock alert alert-info bg-citation'}):
        doi = result.a['href']
        d_list.append(doi)
    return d_list



def get_ext_list(doi):
    try:
        url = "https://dataverse.harvard.edu/api/datasets/export?exporter=OAI_ORE&persistentId=doi%3A" + str(doi)[16:]
        htmlcontent = requests.get(url, headers=headers, timeout=30)
        htmlcontent.raise_for_status()
        htmlcontent.encoding = 'utf-8'
    except:
        print("Request failed.")
    else:
        r = htmlcontent.json()
        files = r["ore:describes"]["ore:aggregates"]
        ext_list = []
        for file in files:
            file_extension = file['schema:name'].split('.')[-1]
            ext_list.append(file_extension)
        ext_list = list(set(ext_list))
        return(ext_list)



def get_content(doi):
    try:
        url = "https://dataverse.harvard.edu/api/datasets/export?exporter=OAI_ORE&persistentId=doi%3A" + str(doi)[16:]
        htmlcontent = requests.get(url, headers=headers, timeout=30)
        htmlcontent.raise_for_status()
        htmlcontent.encoding = 'utf-8'
    except:
        print("Request failed.")
    else:
        r = htmlcontent.json()
        # with open("Log.txt", "at") as f:
        #     print(str(r), file=f)

        jsonDumpsIndentStr = json.dumps(r["ore:describes"]["ore:aggregates"], indent=2)
        print("jsonDumpsIndentStr=", jsonDumpsIndentStr)
        print("Title:", r["ore:describes"]["schema:name"].split(': ', 1)[1])
        print("DOI:", str(doi)[16:])
        print("Publication date:", r["ore:describes"]["schema:datePublished"])
        files = r["ore:describes"]["ore:aggregates"]
        total_size = 0
        for file in files:
            total_size += file['dvcore:filesize']
            file_extension = file['schema:name'].split('.')[-1]
            try:
                if lang_dict[file_extension] in lang_num:
                    lang_num[lang_dict[file_extension]] += 1
            except KeyError:
                continue
        print("Total file size(Kb): %.2f" % (total_size / 1024))
        print('Number of files:', len(files))
        print("Language count:", lang_num)
        print('Note:', type(r["ore:describes"]['citation:Notes']))




headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        'ContentType':
        'text/html; charset=utf-8',
        'Accept-Encoding':
        'gzip, deflate, sdch',
        'Accept-Language':
        'en;q=0.8',
        'Connection':
        'keep-alive',
    }

lang_dict = {'sh': 'bash', 'do': 'stata', 'jl': 'julia', 'py': 'python', 'R': 'R', 'c': 'C', 'cpp': 'C++'\
            , 'm': 'Matlab', 'f': 'fortran', 'f90': 'fortran', 'sas': 'SAS', 'java': 'Java'}
lang_num = {}
for value in lang_dict.values():
    lang_num[value] = 0




# get_ext_list("https://doi.org/10.7910/DVN/24800")


if __name__ == "__main__":
    doi_list = []
    file_ext = []
    for page in range(38):
        text = get_doi(page+1)
        doi_list += parseHTML(text)
    with open('doi.txt', 'w') as f:
        print(doi_list, len(doi_list), file=f)
    with open('file_extention.txt', 'w') as g:
        for doi in doi_list:
            print(doi, get_ext_list(doi), file=g)
            file_ext += get_ext_list(doi)
        file_ext = list(set(file_ext))
        print(file_ext, file=g)