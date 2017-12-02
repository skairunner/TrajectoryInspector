from Trajectory import *
import math

# st-box
class stbox:
    def __init__(self, s1, s2, minL):
        self.s1 = s1 # stpoint
        self.s2 = s2 # stpoint
        # make sure the order is correct
        if self.s1.x > self.s2.x:
            raise ValueError("s1 must be to the left of s2")
        if self.s1.y > self.s2.y:
            raise ValueError("s1 must be above s2")
        self.minL = minL

    @property
    def volume(self):
        w = self.s2.x - self.s1.x
        h = self.s2.y - self.s1.y
        return w * h

    def dist(self, pt):
        dx = max(self.s1.x - pt.x, 0, pt.x - self.s2.x)
        dy = max(self.s1.y - pt.y, 0, pt.y - self.s2.y)
        return math.sqrt(dx*dx + dy*dy)

    def dist2(self, pt):
        dx = max(self.s1.x - pt.x, 0, pt.x - self.s2.x)
        dy = max(self.s1.y - pt.y, 0, pt.y - self.s2.y)
        return dx*dx + dy*dy

    # the closest point on stbox to pt
    def proj_pt(self, pt):
        x = pt.x
        y = pt.y
        # Simply clamp the x, y to the AABB.
        if x < self.s1.x:
            x = self.s1.x
        if y < self.s1.y:
            y = self.s1.y
        if self.s2.x < x:
            x = self.s2.x
        if self.s2.y < y:
            y = self.s2.y
        return stpoint(x, y, pt.t)

    # checks whether a segment or a point is inside this box
    def isBounded(self, obj):
        if isinstance(obj, stpoint):
            c1 = self.s1.x <= obj.x <= self.s2.x
            c2 = self.s1.y <= obj.y <= self.s2.y
            return c1 and c2
        if isinstance(obj, stsegment):
            return self.isBounded(obj.s1) and self.isBounded(obj.s2)
        raise ValueError("obj cannot be of type " + type(obj))

    # 'reverse projection' of e of b.
    # for all points s on e, find the projection with
    # minimum distance to aabb
    def proj_seg(self, seg):
        # case 1: one or two points within the box
        if self.isBounded(seg.s1):
            return seg.s1
        if self.isBounded(seg.s2):
            return seg.s2
        # case 2: seg is axis-aligned.
        if seg.s1.x == seg.s2.x or seg.s1.y == seg.s2.y:
            # clamp an arbitrary point to the AABB.
            return self.proj_pt(seg.s1)
        # case 3 and 4: one endpoint is closest, or point on line is closest
        # distances from endpoints to **box**
        dist = self.dist2(seg.s1)
        pt = seg.s1
        dist2 = self.dist2(seg.s2)
        if dist2 < dist:
            dist = dist2
            pt = seg.s2
        # distance from endpoint to **corner**
        cornerdist2, corner = self.closestCornerDist2(seg)
        if cornerdist2 < dist:
            dist = cornerdist2
            pt = corner
        return self.proj_pt(pt)

    def getCorner(self, corner):
        if corner == 0:
            return self.s1
        elif corner == 1:
            return stpoint(self.s2.x, self.s1.y)
        elif corner == 2:
            return self.s2
        else:
            return stpoint(self.s1.x, self.s2.y) #corner 3

    def dist2FromSegmentToCorner(self, seg, corner):
        pt = self.getCorner(corner)
        pt2 = seg.project(pt) # closest point on line
        return pt.dist2(pt2)

    def closestCornerDist2(self, seg):
        min_i = 0
        min_dist2 = self.dist2FromSegmentToCorner(seg, 0)
        for i in range(1, 4):
            d2 = self.dist2FromSegmentToCorner(seg, i)
            if d2 < min_dist2:
                min_dist2 = d2
                min_i = i
        return min_dist2, self.getCorner(min_i)

# tBoxSeq
class TrajBoxSeq:
    def __init__(self, boxes = []):
        self.boxes = []

    @property
    def volume(self):
        s = 0
        for box in self.boxes:
            s += box.volume
        return s

    def __getitem__(self, key):
        return self.boxes[key]

    def __setitem__(self, key, val):
        self.boxes[key] = val

    def __delitem__(self, key):
        self.boxes.pop(key)

    def coverage(tBoxSeq, traj):
        d1 = traj[0].length
        d2 = tBoxSeq[0].minL
        return d1 + d2

    # aka rep(,)
    def replace(tBoxSeq, traj):
        d1 = tBoxSeq[0].dist(traj[0].s1)
        d2 = tBoxSeq[0].dist(traj[0].s2)
        return d1 + d2

    # returns a new copy of this tboxseq
    # If order is false, treat as insert(tBoxSeq, traj)
    # otherwise treat as insert(traj, tBoxSeq)
    def insert(tBoxSeq, traj, order=False):
        box = tBoxSeq[0]
        seg = traj[0]

        if order:
            
        else:


        # find the proper p to split the first segment
        pt = stbox1.project(stbox2.s2)

        # if pt is s2, same code.
        newbox1 = stbox(stbox1.s1, pt, 0)
        newbox2 = stbox(pt, stbox1.s2, 0)
        return tbox1.cloneAndReplace(newseg1, newseg2)

    def cloneAndReplace(tbox1, tbox2):


if __name__ == "__main__":
    box = stbox(stpoint(0, 0, 0), stpoint(1, 1, 1), 0)
    seg1 = makestseg(.5, .5, 0, 2, -4, 1)
    seg2 = makestseg(-3, 0, 0, -3, 3, 0)
    seg3 = makestseg(0.5, 1.5, 0, -1, 4, 1)
    seg4 = makestseg(1, 2, 0, 2, 1, 1)
    print("Segment in box: ", box.proj_seg(seg1))
    print("Axis-aligned  : ", box.proj_seg(seg2))
    print("closest=endpnt: ", box.proj_seg(seg3))
    import rpdb2; rpdb2.start_embedded_debugger("1234")
    print("closest=middle: ", box.proj_seg(seg4))