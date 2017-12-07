import json
import os
import psycopg2
import psycopg2.extras
import re
from collections import defaultdict

# retrieves paths from db and stores as json files.
conn = psycopg2.connect("dbname=flightpaths user=postgres password=dangerouscourtnounscience2",
    cursor_factory=psycopg2.extras.DictCursor)
cur = conn.cursor()

def simplepath(icao, path):
    cur.execute("SELECT lat, long, fseen, postime FROM paths WHERE ICAO=%s ORDER BY fseen", (icao,))
    out = []
    for row in cur.fetchall():
        lat = float(row["lat"])
        lon = float(row["long"])
        fseen = int(row["fseen"])
        postime = int(row["postime"])
        out.append([lon, lat, fseen, postime])
    # out = sorted(out, key=lambda x:x[2])

    with open(path + icao + ".json", "w") as f:
        json.dump(out, f)

def getplaneinfo(icao, path):
    cur.execute("SELECT * FROM aircraft WHERE ICAO=%s", (icao,))
    with open(path + icao + ".json", "w") as f:
        json.dump(dict(cur.fetchone()), f)

N = 100
cur.execute("SELECT ICAO FROM aircraft LIMIT %d" % (N))
icaos = [row[0] for row in cur.fetchall()]
for i, icao in enumerate(icaos):
    print("icao: %s (%s/%s)" % (icao, i + 1, N))
    getplaneinfo(icao, "data_icao-db/")
    simplepath(icao, "data_perplane/")