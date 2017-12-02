import psycopg2

quit()

conn = psycopg2.connect("dbname=flightpaths user=postgres password=dangerouscourtnounscience2")

cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS aircraft")
cur.execute("CREATE TABLE aircraft (ICAO char(6) PRIMARY KEY,\
        type text, model text, manufacturer text, cnum text, \
        operator text, opICAO varchar(6), WTC int, species int, engtype int,\
        engmount int, engines char(1), mil boolean, country text, Call text,\
        interested boolean);")

cur.execute("DROP TABLE IF EXISTS paths")
cur.execute("CREATE TABLE paths (key serial PRIMARY KEY, ICAO char(6), Fseen bigint, PosTime bigint, \
        alt int, Galt int, InHG real, lat real, long real, speed real, trak real,\
        Sqk text, Vsi int, Gnd boolean, help boolean);")

cur.execute("DROP TABLE IF EXISTS test")
cur.execute("CREATE TABLE test (Key int PRIMARY KEY, data int);")

conn.commit()