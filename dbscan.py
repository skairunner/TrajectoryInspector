import json
from sklearn.cluster import DBSCAN
import numpy as np
import sys

root = "data_simple-segments/"

with open("edwpmanifest.json") as f:
    filenames = json.load(f)

with open("distmatrix.json") as f:
    matrix = json.load(f)

# load all segments
segments = [] # list of list of segments
fileindex = {} # mapping from index to mother filename
c = 0
for filename in filenames:
    with open(root + filename) as f:
        data = json.load(f)
    for traj in data:
        segments.append(traj)
        fileindex[c] = filename
        c += 1

for row in matrix:
    for i, val in enumerate(row):
        if val == "NaN":
            row[i] = sys.float_info.max

db = DBSCAN(eps=0.005, min_samples=2, metric="precomputed")
db.fit(matrix)
labels = db.labels_
# repackage data
# for each label, find the representative.
maxlabel = max(labels)
labeldict = {}
for i, seg in enumerate(segments):
    L = labeldict.setdefault(labels[i], [])
    L.append(i)

# print histogram, basically
for label in labeldict:
    print("{:<2}\t{:>3}".format(int(label), len(labeldict[label])))

def metric_nodelength(seg):
    return len(seg)

def metric_pathlength(seg):
    s = 0
    for i in range(0, len(seg)-1):
        s += (seg[i][0] - seg[i+1][0])**2 + (seg[i][1] - seg[i+1][1])**2
    return s

repdict = {-1: -1} # dictionary of representatives per cluster
for label in labeldict:
    if label == -1:
        continue
    maxlen = 0;
    maxindex = -1;
    for i in labeldict[label]:
        seg = segments[i];
        score = metric_pathlength(seg)
        if score > maxlen:
            maxlen = score
            maxindex = i
    repdict[label] = maxindex

out = []
for i, segment in enumerate(segments):
    label = labels[i]
    obj = {
        "path": segment,
        "icao": fileindex[i],
        "label": int(label),
        "rep": True if repdict[label] == i else False 
    }
    out.append(obj)

with open("dbscanned.json", "w") as outfile:
    json.dump(out, outfile)