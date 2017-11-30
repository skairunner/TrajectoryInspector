import json
import math
from datastructures import *
import sys

# to be used for EDwP_avg
def averager(traj1, traj2, val):
    return val / (traj1.length + traj2.length)

# Find the EDwP distance for given trajectories
def EDwP(traj1, traj2, average=False):
    if traj1 == None or traj2 == None:
        return float("+inf")
    if len(traj1) == len(traj2) == 0:
        return 0
    if (len(traj1) == 0) or (len(traj2) == 0):
        return float("+inf")
    # print(traj1, traj2)
    val1 = EDwP(traj1.rest(), traj2.rest())
    # short-circuit if EDwP is inf.
    if not math.isinf(val1):
        val1 += traj1.replace(traj2) * traj1.coverage(traj2)
    if val1 == 0:
        return 0 # already the minimum
    val2 = EDwP_inserted(traj1.insert(traj2), traj2, average)
    if val2 == 0:
        return 0;
    val3 = EDwP_inserted(traj1, traj2.insert(traj1), average)
    if val3 == 0:
        return 0
    retval = min(val1, val2, val3)
    if average:
        return averager(traj1, traj2, retval)
    return retval

def EDwP_inserted(traj1, traj2, average=False):
    if traj1 == None or traj2 == None:
        return float("+inf")
    if len(traj1) == len(traj2) == 0:
        return 0
    if (len(traj1) == 0) or (len(traj2) == 0):
        return float("+inf")
    val  = EDwP(traj1.rest(), traj2.rest(), average)
    val += traj1.replace(traj2) * traj1.coverage(traj2)
    if average:
        return averager(traj1, traj2, val)
    return val

# convert [[x, y, t]...] into a traj
def trajectoryFromArray(obj):
    stpoints = []
    obj = sorted(obj, key=lambda coord: coord[2])
    for x, y, t in obj:
        point = stpoint(x, y, t)
        stpoints.append(point)
    segments = []
    # skip last point because can't make segment
    for i in range(0, len(stpoints) - 1):
        seg = stsegment(stpoints[i], stpoints[i+1])
        segments.append(seg)
    return Trajectory(segments)


def testEDwP(filename):
    with open(filename) as f:
        data = json.load(f)
    Ts = [trajectoryFromArray(a) for a in data]
    # import rpdb2; rpdb2.start_embedded_debugger("1234")
    average = True
    print(EDwP(Ts[0], Ts[1], average), "should be 5.65")
    print(EDwP(Ts[2], Ts[1], average), "should be 4.64")
    print(EDwP(Ts[0], Ts[2], average), "should be 7.77")
    print(EDwP(Ts[3], Ts[4], False), "should be 89.65")

def testPrint():
    s1 = stsegment(stpoint(0, 1, 2), stpoint(2, 3, 4))
    s2 = stsegment(stpoint(0, 3, 4), stpoint(3, 2, 1))
    s3 = stsegment(stpoint(1, 3, 6), stpoint(1, 3, 7))
    t0 = Trajectory([])
    t1 = Trajectory([s1])
    t2 = Trajectory([s1, s2])
    t3 = Trajectory([s1, s2, s3])
    print("__str__")
    print(str(t1))
    print(str(t2))
    print(str(t3))
    print("__repr__")
    print(repr(t1))
    print(repr(t2))
    print(repr(t3))

if __name__=="__main__":
    # import rpdb2; rpdb2.start_embedded_debugger("1234")
    testEDwP("trajectories.json")