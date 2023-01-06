from bs4 import BeautifulSoup
import requests
import pprint
import re
import unicodedata

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
selectedBooks = ['Jonah']
# selectedBooks = ['Jonah', 'Lamentations']
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
            # for line in soup.find_all(class_='text'):
            lastLineText = None
            for line in soup.find_all(class_='passage-text'):
                # print(line.prettify())
                # exit()
                verse = ''
                for text in line.find_all(class_='text'):
                    # if not text.find_all(class_=['chapternum','versenum']):
                    #     continue

                    lineText = unicodedata.normalize('NFKD', text.get_text())

                    # Remove cross reference markings
                    lineText = re.sub(r'\(.*?\)', '', lineText)

                    # Remove footnote hyper link text
                    lineText = re.sub(r'\[.*?\]', '', lineText)
                    lineText.strip()

                    # Make all white space a single space
                    lineText = re.sub('\\s+', ' ', lineText)

                #     verse = verse + ' ' + lineText
                # verseNumber = verse.split(' ', 2)[1]
                # verseFinal = verse.split(' ', 2)[2]
                # bible[bookName][chapterName][verseNumber] = verseFinal
                # print(verseFinal)
                    # print()
                    # print(text.prettify())
                    # print()
                    # Text sections marked as chapternum start with the chapter number instead of the verse number
                    #   we place them with 1 because the chapternum sections always contain the first verse
                    print(lineText)
                    if text.find(class_='chapternum'):
                        lineText = re.sub(r'([0-9]*) ', '1 ', lineText, 1)
                        print('\t\tsubbed a chapter num!')
                    if not re.fullmatch(r'([0-9]*) .*', lineText):
                        print('\t\tdoes not start with a num!')
                    lastLineText = lineText

                    i = i + 1
                    if (i>8):
                        break
            print('----')
            continue
                #print(line.prettify())
                #print()
            #print(soup.prettify())
# exit()
#pprint.pprint(bible)
exit()
for book in bible.values():
    #exit()
    for chapter in book.values():
        print(chapter)
exit()

# for book in soup.find_all(class_="chapters collapse"):
#     for chapter in book.contents:
#          print(chapter)
    # pprint.pprint(book.contents[0].get('title'))

# for table in soup.find_all('td'):
#     print()
#     pprint.pprint(vars(table))
    # if '/passage/' in href:
    #     print(href)