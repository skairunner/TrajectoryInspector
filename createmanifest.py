# lumps all plane paths in directory

import json
import os
import sys

bigjson = []

rootdir = sys.argv[1]
output  = sys.argv[2]

for file in os.listdir(rootdir):
    with open(rootdir + "/" + file) as f:
        obj = {
            "icao": file.split(".")[0],
            "path": json.load(f)
        }
        bigjson.append(obj)

with open(output, "w") as f:
    json.dump(bigjson, f, indent=4)