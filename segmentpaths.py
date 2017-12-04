import json
import os

pathlensum = 0
pathsum = 0

def getTime(ping):
    return ping[2]

# only segments of len 10 and up are accepted.
def tryAppend(output, segment, limit=10):
    global pathlensum, pathsum
    if len(segment) > limit:
        output.append(segment)
        pathlensum += len(segment)
        pathsum += 1

# slice plane paths when there is a sufficiently long interrupt.
root = "data_perplane/"
outdir = "data_segmented-paths/"
for file in os.listdir(root):
    with open(root + file) as f:
        path = json.load(f)
    output = []
    current_segment = []
    # sort paths by time
    path = sorted(path, key=getTime)
    for i, obj in enumerate(path[:-1]):
        current_segment.append(obj)
        t1 = getTime(obj)
        t2 = getTime(path[i+1])
        if t2 - t1 > 1 * 60: # over N minutes
            tryAppend(output, current_segment)
            current_segment = []
    current_segment.append(path[-1])
    tryAppend(output, current_segment)
    print("Path length: {0}. Segments: {1}".format(len(path), len(output)))
    with open(outdir + file, "w") as f:
        json.dump(output, f)

print("Average segment length: %.1f" % (pathlensum / pathsum))
print("Number of segments: %d" % (pathsum))
