from bs4 import BeautifulSoup
import requests
import pprint
import re
import unicodedata

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

bibleUrls = {}

url = 'https://www.biblegateway.com'
r = requests.get(url + '/versions/')
soup = BeautifulSoup(r.content, features='html.parser')

# This pattern matches things likely to be the bible
# code in a string such as "English Standard Version (ESV)"

# Search for:
# .*? any number of leading characters
# (\ matches a open parenthesis
# .*? matches any number of characters (i.e. the bible code)
# /) a closing parenthesis
# $ only matches the end of the string
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

            bibleUrls[code] = {}
            bibleUrls[code]['url'] = url + '/versions/' + bibleUrl


# For testing, only work with ESV for now
selectedBibleCode = 'ESV'
# selectedBooks = ['Jonah', 'Lamentations']
# selectedBooks = ['Jonah']
selectedBooks = ['Jonah', 'Lamentations']
# selectedBooks = ['Jonah', 'Lamentations']

bible = {}
#bible['url'] = bibleUrls[selectedBibleCode]['url']

r = requests.get(bibleUrls[selectedBibleCode]['url'])
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
            #bible[bookName][chapterName]['url'] = url + chapterUrl

            i = 0 
            r = requests.get(url + chapterUrl)
            soup = BeautifulSoup(r.content, features='html.parser')

            lastLineText = None
            for line in soup.find_all(class_='passage-text'):
                verse = ''
                isPoetry = False
                if line.find(class_='poetry'):
                    isPoetry = True

                # verse = ''
                texts = line.find_all(class_='text')
                for i, text in enumerate(texts):

                    lineText = cleanLineText(text)
                    classText = text.get('class')[1]

                    nextText = None
                    if not i + 1 == len(texts):
                        nextText = texts[i+1]
                        nextLineText = cleanLineText(nextText)

                    lastText = None
                    if i > 0:
                        lastText = texts[i-1]

                    diag = False
                    if diag:
                        print("Len: " + str(len(texts)))
                        print('i: ' + str(i))
                        if not re.fullmatch(r'([0-9]*) .*', lineText):
                            print('does not start with a num!')
                        #if text.get('id'):
                        #    print('\t\tID: ' + str(text.get('id')))
                        print('ID: ' + str(text.get('id')))
                        if nextText:
                            print('Next ID: ' + str(nextText.get('id')))
                        print('Class name: ' + classText)
                        pprint.pprint(text)
                        if nextText:
                            print('class: ' + text.get('class')[1] + ', nextClass: ' + nextText.get('class')[1])
                        print('Text: ' + lineText)
                        print()

                    # If the next line has the same class name (i.e. Jonah 2-1)
                    #   and the next line does not have a number in the start
                    if nextText:
                        if text.get('class')[1] == nextText.get('class')[1] and not re.fullmatch(r'([0-9]*) .*', lineText) and text.get('id'):
                            # print('Remove title: ' + classText)
                            # print()
                            continue
                        
                    if lastText:
                        if text.get('class')[1] == lastText.get('class')[1] and not text.get('id') and isPoetry:
                            # print('adding: ' + classText)
                            if classText not in bible[bookName][chapterName]:
                                bible[bookName][chapterName][classText] = lineText
                                continue
                            bible[bookName][chapterName][classText] = bible[bookName][chapterName][classText] + ' ' + lineText

                            # print(classText + ':\t' + bible[bookName][chapterName][classText])
                            continue

                    bible[bookName][chapterName][classText] = lineText

for i, (bookName, chapters) in enumerate(bible.items()):
    print(bookName)
    print('---')
    for i, (chapterName, verses) in enumerate(chapters.items()):
        for i, (verseName, verse) in enumerate(verses.items()):
            verseName = verseName.split('-')
            v = verseName[0] + ' ' + verseName[1] + ':' + verseName[2]
            print(v + '\t' + verse)
        print()
    print('\n\n')