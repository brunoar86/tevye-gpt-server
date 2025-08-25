import sqlite3


class DBClient:

    def __init__(self):
        n = sqlite3.connect('database.db')
        print(n)
