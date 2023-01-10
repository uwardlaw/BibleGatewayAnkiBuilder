
import pathlib

import gateway
import bible
import anki as ak
import database

# For testing, only work with ESV for now
selectedBibleCode = 'NLT'
# selectedBooks = ['Jonah', 'Lamentations']
# selectedBooks = ['Jonah']
selectedBooks = ['Jonah', 'Lamentations']
# selectedBooks = ['Jonah', 'Lamentations']

url = 'https://www.biblegateway.com'
db = database.Database()
gate = gateway.Gateway(db)

if (bibleUrl := gate.getBibleUrl(selectedBibleCode)) is None:
    gate.updateAvailable()
    if (bibleUrl := gate.getBibleUrl(selectedBibleCode)) is None:
        print('Bible version not available')
        exit()

b = bible.Bible(bibleUrl, selectedBibleCode)
for bookName in selectedBooks:
    b.addBook(bookName)

b.printBible()
# createCards(bible)
# a = ak.Anki()
# a.writeDeck(bible)