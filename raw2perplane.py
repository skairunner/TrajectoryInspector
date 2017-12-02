import json
import os
import psycopg2
import re

DIR = "ADBX_RAW/"
BASE = "2017-08-29-%sZ.json" # HHMM
fseenregex = re.compile(r"\d+")

conn = psycopg2.connect("dbname=flightpaths user=postgres password=dangerouscourtnounscience2")
cur = conn.cursor()


# takes an aircraft ping and fills in empty fields with Null.
optfields = ["Type", "Mdl", "Man", "Cnum", "Op", "Call", "PosTime", "InHG", "Spd", "Vsi",
    "Trak", "OpIcao", "Species", "EngType", "EngMount", "Engines", "Galt", "Help", "Gnd", "Alt"] # optional fields
def fillkeys(d):
    for field in optfields:
        d.setdefault(field, None)
    d["FSeen"] = fseenregex.search(d["FSeen"]).group(0) # extract the epoch time
    d["FSeen"] = int(d["FSeen"])
    # cause someone named their plane ?\t??*
    if d["Call"] != None:
        d["Call"] = d["Call"].replace("\u0000", "")


startHH = 5
startMM = 40


total = 0
excluded = 0
for HH in range(24):
    print("HH: {:02d}".format(HH))
    if HH < startHH:
        continue
    for MM in range(60):
        if HH == startHH and MM < startMM:
            continue
        try:
            print("  MM: {:02d}".format(MM))
            if HH < 10:
                timestamp = "0" + str(HH)
            else:
                timestamp = str(HH)
            if MM < 10:
                timestamp += "0" + str(MM)
            else:
                timestamp += str(MM)

            with open(DIR + (BASE % timestamp), encoding="utf-8") as f:
                data = json.load(f)

            # aircraft is a single 'ping' on adbx exchange, including a lot of plane info
            # as well as positional data.

            for aircraft in data["acList"]:
                fillkeys(aircraft)
                total += 1
                if "Lat" not in aircraft:
                    excluded += 1
                    continue # skip non-latitude
                cur.execute("""INSERT INTO aircraft (ICAO, type, model, manufacturer,
                    cnum, operator, opICAO, WTC, species,
                    engtype, engmount, engines, mil, country, Call, interested) 
                    VALUES (%(Icao)s, %(Type)s, %(Mdl)s, %(Man)s,
                    %(Cnum)s, %(Op)s, %(OpIcao)s, %(WTC)s, %(Species)s,
                    %(EngType)s, %(EngMount)s, %(Engines)s, %(Mil)s, %(Cou)s, %(Call)s, %(Interested)s)
                    ON CONFLICT DO NOTHING""", aircraft)
                cur.execute("""INSERT INTO paths (ICAO, PosTime, alt, Galt, 
                    InHG, lat, long, speed, trak,
                    Sqk, Vsi, Gnd, help, Fseen)
                    VALUES (%(Icao)s, %(PosTime)s, %(Alt)s, %(Galt)s,
                    %(InHG)s, %(Lat)s, %(Long)s, %(Spd)s, %(Trak)s,
                    %(Sqk)s, %(Vsi)s, %(Gnd)s, %(Help)s, %(FSeen)s)""", aircraft)
        except Exception as e:
            conn.rollback()
            print("Total: %d\nExcluded: %d\nExcluded ratio: %.2f\n" % (total, excluded, 100 * excluded / total))
            raise e
        conn.commit()

print("Total: %d\nExcluded: %d\nExcluded ratio: %.2f\n" % (total, excluded, 100 * excluded / total))