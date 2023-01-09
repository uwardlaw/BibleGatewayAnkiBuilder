import pathlib
import persistent
import transaction
import ZODB, ZODB.FileStorage

class Database():
    def __init__(self):
        pathlib.Path('database').mkdir(exist_ok=True)

        dbExists = True
        if not pathlib.Path('database/db.fs').exists():
            # print('No database')
            dbExists = False

        storage = ZODB.FileStorage.FileStorage('database/db.fs')
        db = ZODB.DB(storage)

        # Get the database root
        conn = db.open()
        self.root = conn.root()

        # If the database did not exist, create the structure
        if not dbExists:

            # print('Creating event storage node in database')
            self.root['bibles'] = persistent.mapping.PersistentMapping()
            self.root['available'] = persistent.mapping.PersistentMapping()
            transaction.commit()

    def addAvailableCode(self, code, url):
        self.root['available'][code] = url
        transaction.commit()

    def addBible(self, version, bible):
        self.root['bibles'][version] = bible
        transaction.commit()

    def close(self):
        self.db.close()