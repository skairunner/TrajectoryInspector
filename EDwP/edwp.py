import json
import math
from Trajectory import *
import sys
import random

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

def EDwP_it(traj1, traj2, average=False):
    stack = [[traj1, traj2, -1, [None, None, None], False]]
    retval = None
    while len(stack) > 0:
        t1 = stack[-1][0]
        t2 = stack[-1][1]
        counter = stack[-1][2]
        vals = stack[-1][3]
        skipbranch = stack[-1][4] # after a branch, skip another branch
        if counter == -1: # counter being -1 means initial
            if t1 == None or t2 == None:
                retval = float("+inf")
                stack.pop()
                continue
            if len(t1) == len(t2) == 0:
                retval = 0
                stack.pop()
                continue
            if (len(t1) == 0) or (len(t2) == 0):
                retval = float("+inf")
                stack.pop()
                continue
            counter += 1

        if counter >= 3: # all 3 cases done
            retval = min(*vals)
            if average:
                retval = averager(t1, t2, retval)
            stack.pop()
            continue
        # go through branches 0,1,2
        if retval is not None:
            if retval == 0:
                # shortcircuit
                retval = 0
                stack.pop()
                continue
            vals[counter] = retval
            if counter == 0: # First case needs to have more value
                vals[counter] += t1.replace(t2) * t1.coverage(t2)
            retval = None
            counter += 1
        else: # retval is none? do work
            if counter == 0:
                stack.append([t1.rest(), t2.rest(), -1, [None, None, None], False])
            else:
                if not skipbranch:
                    if counter == 1:
                        stack.append([t1.rest(), t2.rest(), -1, [None, None, None], True])
                    else: # counter == 2
                        stack.append([t1.rest(), t2.rest(), -1, [None, None, None], True])
    return retval

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


def testEDwP(filename, doprint=True):
    with open(filename) as f:
        data = json.load(f)
    Ts = [trajectoryFromArray(a) for a in data]
    # import rpdb2; rpdb2.start_embedded_debugger("1234")
    average = True
    v1 = EDwP(Ts[0], Ts[1], average)
    v2 = EDwP(Ts[2], Ts[1], average)
    v3 = EDwP(Ts[0], Ts[2], average)
    v4 = EDwP(Ts[3], Ts[4], False)
    if doprint:
        print(v1, "should be 5.65")
        print(v2, "should be 4.64")
        print(v3, "should be 7.77")
        print(v4, "should be 89.65")

def profilecall(t1, t2):
    EDwP(t1, t2)

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
    # testEDwP("trajectories.json")

    if False:
        paths = []
        for x in range(2):
            path = []
            for i in range(10):
                c = [random.uniform(-10, 10),
                     random.uniform(-10, 10),
                     i]
                path.append(c)
            paths.append(trajectoryFromArray(path))
        for i in range(1):
            profilecall(*paths)

        quit()

    testEDwP("trajectories.json", True)
    quit()
    import json
    import time
    with open("../data_segmented-paths/4BB467.json") as f:
        data = json.load(f)
    t0 = trajectoryFromArray(data[0])
    t1 = trajectoryFromArray(data[1])
    timestart = time.perf_counter()
    print("t0: %d t1: %d" % (len(t0), len(t1)))
    print(EDwP(t0, t1, average=True))
    timeend = time.perf_counter()
    print("Elapsed time: %d" % (timeend))