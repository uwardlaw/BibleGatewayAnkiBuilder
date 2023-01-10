import re
import unicodedata
import requests
from bs4 import BeautifulSoup

import pprint

class Bible():

    def __init__(self, url, version):
        self.url = url
        self.version = version

        self.availableBooks = {}
        self.books = {}

        r = requests.get(url)
        soup = BeautifulSoup(r.content, features='html.parser')

        # This pattern matches the only reliable source to find the the
        #   name of the book being reviewed. The website links are basically
        #   search queries to a giant database, something like:
        #   "https://www.biblegateway.com/passage/?search=Genesis%201&version=ESV"
        bNamePattern = re.compile(r'.*?search=(.*?)\%')

        # The regex searches the html for the formal name of the tables per book
        #   of the bible containing references to each chapter. They look like:
        #   <tr class="gen-list ot-book">
        for book in soup.find_all(class_=re.compile(r'(nt|ot).*?book')):

            # Find the book name in the table for the book
            match = re.search(r'.*?search=(.*?)\%', (str(book)))

            # Though there many matches, the first one is fine
            bName = match.group(1)

            # Books with more than word actually us a + instead of space,
            #   so replace the + with a space
            bName = " ".join(bName.split('+'))

            self.availableBooks[bName] = {}

            for ch in book.find_all('a'):
                chName = ch.get('title')
                self.availableBooks[bName][chName] = ch.get('href')

    def addBook(self, bName):

        if bName not in self.availableBooks.keys():
            return None

        self.books[bName] = {}

        for chName, chUrl in self.availableBooks[bName].items():

            self.books[bName][chName] = {}
            r = requests.get('https://www.biblegateway.com' + chUrl)
            soup = BeautifulSoup(r.content, features='html.parser')

            for line in soup.find_all(class_='passage-text'):

                # The bible contains prose and poetry. A single verse of
                #   poetry is often broken into multiple lines 
                isPoetry = False
                if line.find(class_='poetry'):
                    isPoetry = True

                texts = line.find_all(class_='text')
                for i, text in enumerate(texts):

                    lineText = self._cleanLineText(text)
                    verseID = text.get('class')[1]               

                    if i < len(texts) - 1:

                        nextText = texts[i+1]
                        nextLineText = self._cleanLineText(nextText)

                        # Check if it's a "title" for a chapter
                        if (text.get('class')[1] == nextText.get('class')[1] and
                            not re.fullmatch(r'([0-9]*) .*', lineText) and
                            text.get('id')):
                            continue

                    if i > 0:

                        lastText = texts[i-1]

                        # If it's poetry then we might add multiple lines into one
                        #   verse
                        if (text.get('class')[1] == lastText.get('class')[1] and
                            not text.get('id')):
                            
                            # If there is a prose line mixed in with the poetry
                            #   or it's the first poetry line, it should just be entered
                            if verseID not in self.books[bName][chName]:
                                self.books[bName][chName][verseID] = lineText
                                continue

                            # If the current line is a continuiation of poetry,
                            #   add it to what ever is there
                            self.books[bName][chName][verseID] = \
                                self.books[bName][chName][verseID] + ' ' + lineText
                            continue

                    # If it's not poetry, if it's not a chapter title, and it's not
                    # prose in poetry, then it's just a regular verse that we can add
                    self.books[bName][chName][verseID] = lineText

    def _cleanLineText(self, text):
        dirtyText = text.get_text()
        lineText = unicodedata.normalize('NFKD', dirtyText)

        # Remove cross reference markings
        lineText = re.sub(r'\(.*?\)', '', lineText)

        # Remove footnote hyper link text
        lineText = re.sub(r'\[.*?\]', '', lineText)
        lineText.strip()

        # Make all white space a single space
        lineText = re.sub('\\s+', ' ', lineText)

        # Text sections marked as chapternum start with the chapter number
        #   instead of the verse number we place them with 1 because the
        #   chapternum sections always contain the first verse
        #   if text.find(class_='chapternum'):
        lineText = re.sub(r'^[0-9]*', '', lineText, 1)

        # Convert left and right quote to regular quote
        lineText = re.sub(r'[\u201C\u201D]', '\u0022', lineText, re.U)

        return lineText

    def printBible(self):
        for bName, chs in self.books.items():
            print(bName)
            print('---')
            for chapterName, verses in chs.items():
                print(chapterName)
                for verseName, verse in verses.items():
                    verseName = verseName.split('-')
                    v = verseName[0] + ' ' + verseName[1] + ':' + verseName[2]
                    print(v + '\t' + verse)
                print()
            print('\n\n')