import sqlite3
import json
import datetime


class P110DBase:

    def __init__(self, dbasepath):
        self.dbasepath = dbasepath
        con = sqlite3.connect(self.dbasepath)
        cur = con.cursor()
        query = ('CREATE TABLE IF NOT EXISTS sources ('
                 'name text PRIMARY KEY,'
                 'type text,'
                 'host text,'
                 'user text,'
                 'password text'
                 ')')
        cur.execute(query)
        query = ('CREATE TABLE IF NOT EXISTS records ('
                 'id  INTEGER PRIMARY KEY AUTOINCREMENT,'
                 't timestamp,'
                 'name text,'
                 'info text,'
                 'usage text'
                 ')')
        cur.execute(query)
        query = ('CREATE TABLE IF NOT EXISTS power ('
                 'id  INTEGER PRIMARY KEY AUTOINCREMENT,'
                 't timestamp,'
                 'name text,'
                 'power integer'
                 ')')
        cur.execute(query)
        query = ('CREATE TABLE IF NOT EXISTS usage ('
                 'id  INTEGER PRIMARY KEY AUTOINCREMENT,'
                 't timestamp,'
                 'name text,'
                 'kwh integer'
                 ')')
        cur.execute(query)
        con.close()

    def add_source(self, name, type, host, user, password):
        try:
            con = sqlite3.connect(self.dbasepath)
            cur = con.cursor()
            query = 'INSERT OR REPLACE INTO sources(name,type,host,user,password) VALUES (?,?,?,?,?)'
            cur.execute(query, (name, type, host, user, password))
            con.commit()
            con.close()
        except Exception as e:
            print(f"help: {e}")

    def record(self, timestamp, name, info, usage):
        try:
            con = sqlite3.connect(self.dbasepath)
            cur = con.cursor()
            # store the complete information for later analysis
            query = 'INSERT INTO records(t,name,info,usage) VALUES (?,?,?,?)'
            cur.execute(query, (timestamp, name, json.dumps(info), json.dumps(usage)))
            con.commit()
            # store the current power level
            self.calc_power(con, name, usage)
            con.commit()
            # store the kwh usage of the current hour
            self.calc_kwh(con, name, usage)
            con.commit()
            # end it
            con.close()
        except Exception as e:
            print(f"help: {e}")

    def calc_power(self, con, name, usage):
        timestr = usage["result"]["local_time"]
        t = datetime.datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
        t1 = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, 0, 0)
        pw = usage["result"]["current_power"]
        cur = con.cursor()
        query = 'INSERT OR REPLACE INTO power(t,name,power) VALUES (?,?,?)'
        cur.execute(query, (t1, name, pw))

    def calc_kwh(self, con, name, usage):
        timestr = usage["result"]["local_time"]
        t = datetime.datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
        # get the kwh for the current hour
        d = 6
        h = t.hour
        kwh1 = usage["result"]["past7d"][d][h]
        t1 = datetime.datetime(t.year, t.month, t.day, t.hour, 0, 0, 0)
        cur = con.cursor()
        query = 'INSERT OR REPLACE INTO usage(t,name,kwh) VALUES (?,?,?)'
        cur.execute(query, (t1, name, kwh1))
        # get the kwh for the previous hour
        if (h == 0):
            d = d - 1
            h = 23
        else:
            h = h - 1
        kwh2 = usage["result"]["past7d"][d][h]
        t2 = t1 - datetime.timedelta(hours=1)
        cur = con.cursor()
        query = 'INSERT OR REPLACE INTO usage(t,name,kwh) VALUES (?,?, ?)'
        cur.execute(query, (t2, name, kwh2))
