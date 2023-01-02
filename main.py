from bs4 import BeautifulSoup
import requests

bibles = []

url = 'https://www.biblegateway.com/versions/'
r = requests.get(url)
soup = BeautifulSoup(r.content, features='html.parser')

for link in soup.find_all('a'):
    href = link.get('href')
    if '/versions/' in href:
        version = href.split('/versions/')[1]
        if not version.isspace() and not version == "":
            bibles.append(url + version)


