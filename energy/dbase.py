import time
import sqlite3


class EnergyDbase:

    def __init__(self, uri, listener):
        self.uri = uri
        self.listener = listener
        self.running = True
        self.last_power_id = -1
        self.last_usage_id = -1

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            with sqlite3.connect(self.uri, uri=True, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES) as con:
                self.check_new_record(con)
            time.sleep(1)

    def check_new_record(self, con):
        cur = con.cursor()
        # cur.execute('SELECT t as "t [timestamp]" FROM power WHERE t > ? ORDER BY t', (self.last_power_t,))
        cur.execute('SELECT id,t,name,power FROM power WHERE id > ? ORDER BY id', (self.last_power_id,))
        powers = {}
        for row in cur.fetchall():
            self.last_power_id = row[0]
            if row[2] not in powers:
                powers[row[2]] = []
            powers[row[2]].append({
                'id': row[0],
                't': row[1],
                'power': row[3]
            })
        if len(powers)>0:
            self.handle_power_records(con, powers)
        cur = con.cursor()
        # cur.execute('SELECT t as "t [timestamp]" FROM usage WHERE t > ? ORDER BY t', (self.last_usage_t,))
        cur.execute('SELECT id,t,name,today_runtime,month_runtime,today_energy,month_energy  FROM usage WHERE id > ? ORDER BY id', (self.last_usage_id,))
        usages = {}
        for row in cur.fetchall():
            self.last_usage_id = row[0]
            if row[2] not in usages:
                usages[row[2]] = []
            usages[row[2]].append({
                'id': row[0],
                't': row[1],
                'today_runtime': row[3],
                'month_runtime': row[4],
                'today_energy': row[5],
                'month_energy': row[6],
            })
        if len(usages)>0:
            self.handle_usage_records(con, usages)

    def handle_power_records(self, con, powers):
        self.listener.event("Powers", powers)

    def handle_usage_records(self, con, usages):
        self.listener.event("Usages", usages)

    def list_tables(self, con):
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_schema WHERE type='table' ORDER BY name;")
        for tbl in cur:
            print(f"table: {tbl[0]}")

    def last_t(self):
        with sqlite3.connect(self.uri, uri=True, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES) as con:
            cur = con.cursor()
            cur.execute('SELECT  max(t) as "max_ts [timestamp]" FROM records;')
            row = cur.fetchone()
            print(f"current_timestamp[{row[0]}][{type(row[0])}]")
            return row[0]
