import sqlite3
import json


class P110DBase:

    def __init__(self, dbasepath):
        self.dbasepath = dbasepath
        con = sqlite3.connect(self.dbasepath)
        cur = con.cursor()
        query = ('CREATE TABLE IF NOT EXISTS records ('
                      'timestamp   text,'
                      'info text,'
                      'usage text'
                 ')')
        cur.execute(query)
        con.close()

    def record(self, timestamp, info, usage):
        try:
            con = sqlite3.connect(self.dbasepath)
            cur = con.cursor()
            query = 'INSERT INTO records VALUES (?,?,?)'
            cur.execute(query, (timestamp, json.dumps(info), json.dumps(usage)))
            con.commit()
            con.close()
        except Exception as e:
            print(f"help: {e}")
