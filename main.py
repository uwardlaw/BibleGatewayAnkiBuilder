from bs4 import BeautifulSoup
import requests
import pprint
import re
import unicodedata
import pathlib

import gateway
import anki as ak
import database

def cleanLineText(text):
    dirtyText = text.get_text()
    lineText = unicodedata.normalize('NFKD', dirtyText)

    # Remove cross reference markings
    lineText = re.sub(r'\(.*?\)', '', lineText)

    # Remove footnote hyper link text
    lineText = re.sub(r'\[.*?\]', '', lineText)
    lineText.strip()

    # Make all white space a single space
    lineText = re.sub('\\s+', ' ', lineText)

    # Text sections marked as chapternum start with the chapter number instead of the verse number
    #   we place them with 1 because the chapternum sections always contain the first verse
    # if text.find(class_='chapternum'):
    lineText = re.sub(r'^[0-9]*', '', lineText, 1)

    return lineText

def printBible(bible):
    for bookName, chapters in bible.items():
        print(bookName)
        print('---')
        for chapterName, verses in chapters.items():
            print(chapterName)
            for verseName, verse in verses.items():
                verseName = verseName.split('-')
                v = verseName[0] + ' ' + verseName[1] + ':' + verseName[2]
                print(v + '\t' + verse)
            print()
        print('\n\n')

# For testing, only work with ESV for now
selectedBibleCode = 'NLT'
# selectedBooks = ['Jonah', 'Lamentations']
selectedBooks = ['Jonah']
# selectedBooks = ['Jonah', 'Lamentations']
# selectedBooks = ['Jonah', 'Lamentations']

url = 'https://www.biblegateway.com'
db = database.Database()
gate = gateway.Gateway(db)

if (bibleUrl := gate.getBibleUrl(selectedBibleCode)) is None:
    gate.updateAvailable()
    if (bibleUrl := gate.getBibleUrl(selectedBibleCode)) is None:
        print('Bible version not available')
        exit()

bible = {}
r = requests.get(bibleUrl)
soup = BeautifulSoup(r.content, features='html.parser')

# For testing, only work with two books for now


# This pattern matches the only reliable source to find the the
# name of the book being reviewed. The website links are basically
# search queries to a giant database, so the references all contain
# something like "https://www.biblegateway.com/passage/?search=Genesis%201&version=ESV"

# Search for:
# .*? any number of characters
# 'search=' this exact string
# .*? matches any number of character (i.e. the name of the book)
# \% matches the uri seperator for spaces, signaling the end of the name of the book
bookNamePattern = re.compile(r'.*?search=(.*?)\%')

# The regex searches the html for the formal name of the tables per book
# of the bible containing references to each chapter. They look like:
# <tr class="gen-list ot-book">

# Find all html blocks that have a class name that matches:
# (nt|ot) exactly 'nt' or 'ot'
# .*? any number of characters
# 'book' this exact string
for book in soup.find_all(class_=re.compile(r'(nt|ot).*?book')):

    # Find the book name in the table for the book
    match = re.search(bookNamePattern, (str(book)))

    # Though there many matches, the first one is fine
    bookName = match.group(1)

    # Books with more than word actually us a + instead of space,
    # so replace the + with a space
    bookName = " ".join(bookName.split('+'))

    if bookName in selectedBooks:
        bible[bookName] = {}
        for chapter in book.find_all('a'):
            chapterName = chapter.get('title')
            chapterUrl = chapter.get('href')
            bible[bookName][chapterName] = {}

            r = requests.get(url + chapterUrl)
            soup = BeautifulSoup(r.content, features='html.parser')

            for line in soup.find_all(class_='passage-text'):

                # The bible contains prose and poetry
                #   A single verse of poetry
                #   is often broken into multiple lines 
                isPoetry = False
                if line.find(class_='poetry'):
                    isPoetry = True

                texts = line.find_all(class_='text')
                for i, text in enumerate(texts):

                    lineText = cleanLineText(text)
                    classText = text.get('class')[1]               

                    if i < len(texts) - 1:

                        nextText = texts[i+1]
                        nextLineText = cleanLineText(nextText)

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
                            if classText not in bible[bookName][chapterName]:
                                bible[bookName][chapterName][classText] = lineText
                                continue

                            # If the current line is a continuiation of poetry,
                            #   add it to what ever is there
                            bible[bookName][chapterName][classText] = bible[bookName][chapterName][classText] + ' ' + lineText
                            continue

                    # If it's not poetry, if it's not a chapter title, and it's not
                    # prose in poetry, then it's just a regular verse that we can add
                    bible[bookName][chapterName][classText] = lineText

printBible(bible)
# createCards(bible)
# a = ak.Anki()
# a.writeDeck(bible)

