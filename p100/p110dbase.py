import sqlite3
import datetime

class P110DBase:

    def __init__(self, dbasepath):
        self.dbasepath = dbasepath
        con = sqlite3.connect(self.dbasepath)
        cur = con.cursor()
        query = ('CREATE TABLE IF NOT EXISTS records ('
                      'timestamp   text,'
                      'locdate   text,'
                      'delivtarief1   float,'
                      'delivtarief2   float'
                 ')')
        cur.execute(query)
        con.close()

    def record(self, timestamp, locdate, delivtarief1, delivtarief2):
        try:
            con = sqlite3.connect(self.dbasepath)
            cur = con.cursor()
            query = 'INSERT INTO records VALUES (?,?,?,?)'
            cur.execute(query, (timestamp, locdate, delivtarief1, delivtarief2))
            con.commit()
            con.close()
        except Exception as e:
            print(f"help: {e}")
