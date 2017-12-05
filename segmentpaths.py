import json
import os

pathlensum = 0
pathsum = 0

POSTIME = True

def getTime(ping):
    if POSTIME:
        return ping[3]
    return ping[2]

# only segments of len 10 and up are accepted.
def tryAppend(output, segment, limit=50):
    global pathlensum, pathsum
    if len(segment) > limit:
        output.append(segment)
        pathlensum += len(segment)
        pathsum += 1
        return 1
    return 0

# slice plane paths when there is a sufficiently long interrupt.
root = "data_perplane/"
outdir = "data_segmented-paths/"
blacklist = ["A234C0.json"]
for file in os.listdir(root):
    if file in blacklist:
        continue
    with open(root + file) as f:
        path = json.load(f)
    output = []
    current_segment = []
    segmentsAccepted = 0
    pathsegments = []
    # sort paths by time
    path = sorted(path, key=getTime)
    for i, obj in enumerate(path[:-1]):
        if POSTIME:
            current_segment.append(obj[:2] + [obj[3]])
        else:
            current_segment.append(obj[:3])
        t1 = getTime(obj)
        t2 = getTime(path[i+1])
        if t2 - t1 > 2000 * 60: # over N minutes
            segmentsAccepted += tryAppend(output, current_segment)
            pathsegments.append(current_segment)
            current_segment = []
    current_segment.append(path[-1])
    segmentsAccepted += tryAppend(output, current_segment)
    pathsegments.append(current_segment)
    # if no segments, append longest
    if segmentsAccepted == 0:
        maxseg = None
        maxlen = 0
        for seg in pathsegments:
            if len(seg) > maxlen:
                maxlen = len(seg)
                maxseg = seg
        output.append(maxseg);

    print("Path length: {0}. Segments: {1}".format(len(path), len(output)))
    with open(outdir + file, "w") as f:
        json.dump(output, f)

print("Average segment length: %.1f" % (pathlensum / pathsum))
print("Number of segments: %d" % (pathsum))
