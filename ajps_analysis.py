import requests
from bs4 import BeautifulSoup
import os
import json


def get_doi(page_number):

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


def get_content(doi):

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
    try:
        url = "https://dataverse.harvard.edu/api/datasets/export?exporter=OAI_ORE&persistentId=doi%3A" + str(doi)[16:]
        htmlcontent = requests.get(url, headers=headers, timeout=30)
        htmlcontent.raise_for_status()
        htmlcontent.encoding = 'utf-8'
        r = htmlcontent.json()
        # with open("Log.txt", "at") as f:
        #     print(str(r), file=f)

        # jsonDumpsIndentStr = json.dumps(r["ore:describes"]["ore:aggregates"], indent=2)
        # print("jsonDumpsIndentStr=", jsonDumpsIndentStr)
        print("Title:", r["ore:describes"]["schema:name"])
        print("DOI:", str(doi)[16:])
        print("Publication date:", r["ore:describes"]["schema:datePublished"])
        files = r["ore:describes"]["ore:aggregates"]
        total_size = 0
        for file in files:
            total_size += file['dvcore:filesize']
        print("Total file size(Kb): '%.2f'", total_size/1024)
        print('Number of files:', len(files))
        print('Note:', type(r["ore:describes"]['citation:Notes']))


    except:
        return "Request failed."
#
# get_content("https://doi.org/10.7910/DVN/O6VHZZ")



if __name__ == "__main__":
    doi_list = []
    for page in range(38):
        text = get_doi(page+1)
        doi_list += parseHTML(text)
    with open('doi.txt', 'a+') as f:
        print(doi_list, len(doi_list), file=f)
    for doi in doi_list:
        get_content(doi)
