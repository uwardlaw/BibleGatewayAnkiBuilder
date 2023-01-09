import requests
from bs4 import BeautifulSoup
import re

class Gateway():
    def __init__(self, db):
        self.url = 'https://www.biblegateway.com'
        self.db = db

    def updateAvailable(self):
        print('Updating Available')
        
        versionsUrl = self.url + '/versions/'
        r = requests.get(versionsUrl)
        soup = BeautifulSoup(r.content, features='html.parser')

        # This pattern matches things likely to be the bible
        # code in a string such as "English Standard Version (ESV)"
        codePattern = re.compile(r'.*?(\(.*?\))$')

        for link in soup.find_all('a'):
            if len(link.contents) > 1:
                continue

            href = link.get('href')

            if '/versions/' in href:    
                bibleUrl = href.split('/versions/')[1].strip()

                if not bibleUrl.isspace() and not bibleUrl == "":

                    # The link contents contain the names of the bible versions
                    # Grab occurences that could be the bible code
                    match = re.search(codePattern, str(link.contents[0]))

                    # If more than one potential code, make a list out of it
                    code = (match.group(1).split(' '))

                    # Take the last match because the code is always listed last
                    code = code[-1]

                    # Get the string without the surrounding parenthese
                    code = code[1:-1]

                    self.db.addAvailableCode(code, versionsUrl + bibleUrl)

    def getBibleUrl(self, code):
        if code in self.db.root['available']:
            return self.db.root['available'][code]
        return None