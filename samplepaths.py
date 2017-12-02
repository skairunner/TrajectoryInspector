import json
import os
import psycopg2
import psycopg2.extras
import re
import visvalingamwyatt as vw
from collections import defaultdict

# retrieves paths from db

DIR = "ADBX_RAW/"
BASE = "2017-08-29-%sZ.json" # HHMM
fseenregex = re.compile(r"\d+")


conn = psycopg2.connect("dbname=flightpaths user=postgres password=dangerouscourtnounscience2",
    cursor_factory=psycopg2.extras.DictCursor)
cur = conn.cursor()

def fullpath(icao, path):
    cur.execute("SELECT * FROM paths WHERE ICAO=%s ORDER BY Fseen", (icao,))
    geojson = {}
    coords = []
    for row in cur.fetchall():
        lat = float(row["lat"])
        lon = float(row["long"])
        coords.append([lng, lat])
    geojson = {}
    geojson["type"] = "LineString"
    geojson["coordinates"] = coords
    with open(path + icao + ".geo.json", "w") as f:
        json.dump(geojson, f)

def simplepath(icao, jsonpath, tsvpath, ratio=0.3):
    cur.execute("SELECT * FROM paths WHERE ICAO=%s ORDER BY Fseen", (icao,))
    geojson = {}
    coords = []
    out = []
    for row in cur.fetchall():
        lat = float(row["lat"])
        lon = float(row["long"])
        coords.append([lon, lat])
        out.append(dict(row))
    out = sorted(out, key=lambda x: x["postime"] if "postime" in x else x["fseen"])

    geojson = {}
    geojson["type"] = "LineString"
    geojson["coordinates"] = coords
    geojson = vw.simplify_geometry(geojson, ratio=ratio)
    with open(jsonpath + icao + ".simpl.geo.json", "w") as f:
        json.dump(geojson, f)

    with open(tsvpath + icao + ".json", "w") as f:
        json.dump(out, f)

def getplaneinfo(icao, path):
    cur.execute("SELECT * FROM aircraft WHERE ICAO=%s", (icao,))
    with open(path + icao + ".json", "w") as f:
        json.dump(dict(cur.fetchone()), f)

cur.execute("SELECT ICAO FROM aircraft LIMIT 10")
icaos = [row[0] for row in cur.fetchall()]
for i, icao in enumerate(icaos):
    print("icao: %s (%s/%s)" % (icao, i, 10))
    getplaneinfo(icao, "icao-db/")
    simplepath(icao, "ADBX_perplane/", "perplane_fullpath/")