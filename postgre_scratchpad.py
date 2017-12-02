import psycopg2

conn = psycopg2.connect("dbname=flightpaths user=postgres password=dangerouscourtnounscience2")

cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS test")
cur.execute("CREATE TABLE test (Key int PRIMARY KEY, data int);")

conn.commit()

d = {"Thing1": 3, "thing": 4}
cur.execute("INSERT INTO test (Key, data) VALUES (%(Thing1)s, %(thing)s);", d)
conn.commit()

cur.execute("SELECT * FROM test")
print(cur.fetchall())