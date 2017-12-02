import json
import os
import psycopg2
import psycopg2.extras
import re
import visvalingamwyatt as vw

DIR = "ADBX_RAW/"
BASE = "2017-08-29-%sZ.json" # HHMM
fseenregex = re.compile(r"\d+")

conn = psycopg2.connect("dbname=flightpaths user=postgres password=dangerouscourtnounscience2",
    cursor_factory=psycopg2.extras.DictCursor)
cur = conn.cursor()


# cur.execute("SELECT reltuples AS approximate_row_count FROM pg_class WHERE relname = 'aircraft';")
# print(cur.fetchone())
# quit()

# for x in i:
#     print(x)

icao = "AAE597"
cur.execute("SELECT * FROM paths WHERE ICAO=%s ORDER BY Fseen", (icao,))
output = []
for row in cur.fetchall():
    lat = float(row["lat"])
    lon = float(row["long"])
    fseen = float(row["fseen"])
    output.append([lat, lon, fseen])

with open(icao + ".path", "w") as f:
    json.dump(output, f)

# output in geojson format
geojson = {}
geojson["type"] = "LineString"
geojson["coordinates"] = [[lng, lat] for lat, lng, fseen in output]
with open(icao + ".geo.json", "w") as f:
    json.dump(geojson, f)

# output simplified
simplified = vw.simplify_geometry(geojson, ratio=0.3)
with open(icao + ".simpl.geo.json", "w") as f:
    json.dump(simplified, f)

print(len(output))