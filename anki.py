import genanki.genanki as genanki
import re
import pathlib

class Anki():
    def __init__(self):
        self.model = genanki.Model(
            1305533440,
            'Basic (type in the answer) (genanki)',
            fields=[{
                'name': 'Front',
                'font': 'Arial',
            },
            {
                'name': 'Back',
                'font': 'Arial',
            },
            ],
            templates=[{
                'name': 'Card 1',
                'qfmt': '{{Front}}\n\n{{type:Back}}',
                'afmt': '{{Front}}\n\n<hr id=answer>\n\n{{type:Back}}',
                },
            ],
            css='.card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n',
        )

    def writeDeck(self, bible):
        deck = genanki.Deck(
            1305533440,
            'Bible'
        )

        for bookName, chapters in bible.items():
            for chapterName, verses in chapters.items():
                for verseName, verse in verses.items():

                    v = verseName.split('-')
                    verseName = v[0] + ' ' + v[1] + ':' + v[2]
                    bookName = re.sub('\\s+', '', bookName)
                    chapterName = re.sub('\\s+', '', chapterName)

                    deck.add_note(
                        genanki.Note(
                            model = self.model,
                            fields=[verseName,verse],
                            tags=[bookName, chapterName]
                        )
                    )

        pathlib.Path('./decks').mkdir(exist_ok=True)
        genanki.Package(deck).write_to_file('decks/bible.apkg')