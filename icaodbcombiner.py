import json
import os
import sys

bigjson = {}

rootdir = "data_icao-db/"
output  = "client/icaodb.json"

for file in os.listdir(rootdir):
    with open(rootdir + file) as f:
        bigjson[file.split(".")[0]] = json.load(f)

with open(output, "w") as f:
    json.dump(bigjson, f)