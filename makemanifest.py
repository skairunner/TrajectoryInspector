import json
import os

"""
Creates a manifest file for C#EDwP to consume, giving each segment an index
Format:
[
    ["filename.json", index]
    ...
]

The index is for the first segment of that file, with each segment incrementing by 1.
"""

root = "data_simple-segments/"
outfile = "edwpmanifest.json"
out = []
for file in os.listdir(root):
    out.append(file)

with open(outfile, "w") as f:
    json.dump(out, f)