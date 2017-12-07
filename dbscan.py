import json
from sklearn.cluster import DBSCAN
import numpy as np
import sys

DODBSCAN = False

""" load all the data first """

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

# to be used in Cluster.serialize()
def segobjFromSegids(ids):
    path = []
    for segid in ids:
        seg = segments[segid]
        for coord in seg:
            path.append(coord)
    segobj = {
        "path": path,
        "icao": fileindex[ids[0]].split(".json")[0]
    }
    return segobj


class Cluster:
    def __init__(self, label):
        self.label = int(label)
        self.segmentids = []
        self.rep = None

    def __len__(self):
        return len(self.segmentids)

    def findrep(self):
        if self.label == -1:
            return None
        # for each segment in cluster, find distance to all other segments
        distances = []
        for i, seg1 in enumerate(self.segmentids):
            total = 0
            for j, seg2 in enumerate(self.segmentids):
                if matrix[i][j] == sys.float_info.max:
                    total += 0
                else:
                    total += matrix[i][j] ** 2
            distances.append(total)
        # now find minimum
        m_score = None
        m_index = None
        for i, score in enumerate(distances):
            if i == 0:
                m_score = score
                m_index = i
            else:
                if score < m_score:
                    m_score = score
                    m_index = i
        self.rep = i
        return i

    def add(self, index):
        self.segmentids.append(index)

    # turn into base objects (arrays or dicts)
    def serialize(self):
        # inflate ids into paths, joining adjacent segments 
        # if same icao
        obj =  {
            "segments": [],
            "label": self.label
        }
        self.segmentids.sort()
        working = []
        for segid in self.segmentids:
            pinchoff = False
            if len(working) == 0:
                working.append(segid)
            else:
                previd = working[-1]
                if fileindex[segid] == fileindex[previd]:
                    t1 = segments[previd][-1][2]
                    t2 = segments[segid][0][2]
                    if t2 - t1 < 60 * 1000: # have to be within 1min to be one segment
                        working.append(segid)
                    else:
                        pinchoff = True
                else:
                    pinchoff = True
            # if either seg too far, or different path
            if pinchoff:
                obj["segments"].append(segobjFromSegids(working))
                working = [segid]
        if len(working) > 0:
            obj["segments"].append(segobjFromSegids(working))

        return obj

def mindistance(index, data, cluster):
    return min([data[index][c_in] for c_in in cluster])

# using Lu & Fu's nearest neighbor algorithm
def lufucluster(data, threshold=0.1):
    n = len(data)
    clusters = [[0]]
    # do the clustering
    for i in range(1, n):
        underthreshold = []
        for cluster in clusters:
            d = mindistance(i, data, cluster)
            if d < threshold:
                underthreshold.append([cluster, d])
        if len(underthreshold) == 0:
            clusters.append([i])
        else:
            smallest = min(underthreshold, key=lambda el: el[1])
            smallest[0].append(i)
    # get labels
    labels = [-1 for x in data]
    for i, cluster in enumerate(clusters):
        for el in cluster:
            labels[el] = i
    return labels


def metric_nodelength(seg):
    return len(seg)

def metric_pathlength(seg):
    s = 0
    for i in range(0, len(seg)-1):
        s += (seg[i][0] - seg[i+1][0])**2 + (seg[i][1] - seg[i+1][1])**2
    return s

if DODBSCAN:
    db = DBSCAN(eps=0.005, min_samples=2, metric="precomputed")
    db.fit(matrix)
    labels = db.labels_
else:
    labels = lufucluster(matrix, 0.3)

# repackage data
maxlabel = max(labels)
labeldict = {}
for i, seg in enumerate(segments):
    label = labels[i]
    if label not in labeldict:
        labeldict[label] = Cluster(label)
    labeldict[label].add(i)

# combine all the single element clusters as outlier group
outliers = Cluster(-1)
todelete = []
for cluster in labeldict.values():
    if len(cluster) == 1:
        outliers.add(cluster.segmentids[0])
        todelete.append(cluster.label)
for label in todelete:
    del labeldict[label]
labeldict[-1] = outliers


# also find the rep for purposes of distance
for label in labeldict:
    labeldict[label].findrep()

# print histogram, basically, for quick diagnostics
for label in labeldict:
    cluster = labeldict[label]
    print("{:<2}\t{:>3}".format(int(label), len(cluster)))

# finding cluster representatives
repdict = {} # dictionary of representatives per cluster
for label in labeldict:
    if label == -1:
        continue
    maxlen = 0;
    maxindex = -1;
    cluster = labeldict[label]
    for segid in cluster.segmentids:
        score = metric_pathlength(segments[segid])
        if score > maxlen:
            maxlen = score
            maxindex = i
    repdict[label] = maxindex

out = []
for cluster in labeldict.values():
    out.append(cluster.serialize())

with open("dbscanned.json", "w") as outfile:
    json.dump(out, outfile)