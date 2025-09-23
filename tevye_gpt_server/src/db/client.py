import sqlite3


class DBClient:

    def __init__(self):
        n = sqlite3.connect('database.db')
        print(n)

    def get_db(self):
        db = sqlite3.connect('database.db')
        try:
            yield db
        finally:
            db.close()


db_client = DBClient()
