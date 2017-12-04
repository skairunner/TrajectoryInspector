import json
from sklearn.cluster import DBSCAN
import numpy as np
import sys

with open("A976C7.out.json") as f:
    matrix = json.load(f)

for row in matrix:
    for i, val in enumerate(row):
        if val == "NaN":
            row[i] = sys.float_info.max

db = DBSCAN(eps=0.001, min_samples=5, metric="precomputed")
db.fit(matrix)
labels = db.labels_
print(labels)
# repackage data
with open("data_segmented-paths/A976C7.json") as segfile:
    segments = json.load(segfile)

# for each label, find the representative.
maxlabel = max(labels)
labeldict = {}
for i, seg in enumerate(segments):
    L = labeldict.setdefault(labels[i], [])
    L.append(i)

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
        "label": int(label),
        "rep": True if repdict[label] == i else False 
    }
    out.append(obj)

with open("A976C7.annotated.json", "w") as outfile:
    json.dump(out, outfile)