import math

# a space-time point, or s
class stpoint:
    def __init__(self, x = 0, y = 0, t = 0):
        self.x = x
        self.y = y
        self.t = t

    def dist(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def __str__(self):
        return "({:.2f}, {:.2f}, {:.2f})".format(self.x, self.y, self.t)

    def __repr__(self):
        return f"stpoint<{str(self)}>"

    def __eq__(self, other):
        if self.x != other.x:
            return False
        if self.y != other.y:
            return False
        if self.t != other.t:
            return False
        return True

    # epsilon equivalency
    def equivalent(self, other, e = 0.0001):
        if self.x - other.x > e:
            return False
        if self.y - other.y > e:
            return False
        if self.t - other.t > e:
            return False
        return True

class Vector2:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
        self.length = self.getlen()

    def __div__(self, val):
        return Vector2(self.x / other, self.y / other)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, val):
        return Vector2(self.x * val, self.y * val)

    def __repr__(self):
        return f"Vector2<{self.x}, {self.y}>";

    def normalize(self):
        self.x = self.x / self.length
        self.y = self.y / self.length
        self.length = 1
        return self;

    def normalized(self, other):
        o = Vector2(self.x, self.y)
        return o.normalize()

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def getlen(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

# a space-time segment, or e
class stsegment:
    def __init__(self, s1, s2):
        self.s1 = s1
        self.s2 = s2
        if self.s1.t > self.s2.t:
            raise ValueError("t not sorted: %d, %d" % (s1.t, s2.t))
        self.length = self.calclen()
        self.inserted = False

    def calclen(self):
        # euclidian for now
        return self.s1.dist(self.s2)

    def sets1(self, st):
        self.s1 = st
        self.sortself() # preserve time ordering
        self.length = self.calclen()

    def sets2(self, st):
        self.s2 = st
        self.sortself() # preserve time ordering
        self.length = self.calclen()

    def sortself(self):
        if self.s1.t > self.s2.t:
            temp = self.s1
            self.s1 = self.s2
            self.s2 = temp

    def __str__(self):
        return f"{str(self.s1)} -> {str(self.s2)}"

    def __repr__(self):
        return f"stsegment<{str(self)}>"

    @property
    def speed(self):
        return self.length / (self.s2.t - self.s1.t)


def stpointFromVector2(vec, time):
    return stpoint(vec.x, vec.y, time)

# a trajectory, or T
class Trajectory:
    def __init__(self, segments = []):
        self.segments = [x for x in segments]

    def __getitem__(self, key):
        return self.segments[key]

    def __setitem__(self, key, val):
        self.segments[key] = val

    def __delitem__(self, key):
        self.segments.pop(key)

    def __len__(self):
        return len(self.segments)

    def __str__(self):
        if len(self) == 0:
            return "Trajectory<>"
        if len(self) == 1:
            return f"Trajectory<{str(self.segments[0])}>"
        s = f"Trajectory<{str(self.segments[0])}\n"

        for seg in self.segments[1:-1]:
            s += f"           {str(seg)}\n"
        s += f"           {str(self.segments[-1])}>"
        return s

    def __repr__(self):
        if len(self) == 0:
            return "Trajectory<>"
        s = "Trajectory<"
        for seg in self.segments[:-1]:
            s += str(seg) + "; "
        s += str(self.segments[-1])
        return s + ">"

    @property
    def length(self):
        s = 0
        for seg in self.segments:
            s += seg.length
        return s

    # Clone this trajectory, replacing e1 with newsegs
    def cloneAndReplace(self, newseg1, newseg2):
        # probably also sort it
        t = Trajectory()
        t.segments = [newseg1, newseg2] + self.segments[1:]
        # t.segments = sorted(t.segments, key=)
        return t

    # aka rep(,)
    def replace(traj1, traj2):
        d1 = traj1[0].s1.dist(traj2[0].s1)
        d2 = traj1[0].s2.dist(traj2[0].s2)
        return d1 + d2

    # returns a new copy of this trajectory. aka ins(,)
    # in order to terminate, must check that the segment
    # hasn't already been projected.
    def insert(traj1, traj2):
        e1 = traj1[0]
        e2 = traj2[0]

        # if you're inserting onto a segment of length 0, just return none.
        if e1.s1 == e1.s2:
            return traj1.cloneAndReplace(e1, e1)

        # find the proper p to split the first segment
        # which is the closest p, using vector math
        a = Vector2(e1.s1.x, e1.s1.y)
        b = Vector2(e1.s2.x, e1.s2.y)
        q = Vector2(e2.s2.x, e2.s2.y)
        v = b - a # the line segment e1
        v.normalize()
        # these are essentially projecting a,b,q onto a new coord
        # system defined by the axis v.
        dista = v.dot(a)
        distb = v.dot(b)
        distq = v.dot(q)

        p = v * distq
        # if point not on segment, set to far point.
        if distq <= dista: # the new point is "behind" a
            pstatus = -1
            pt = e1.s1
        elif distb <= distq: # the new point is "in front of" b
            pstatus = 1
            pt = e1.s2
        else:
            pstatus = 0
            t = e1.s1.t + e1.s1.dist(p) / e1.speed
            pt = stpointFromVector2(p, t)

        # if point is already on this segment
        # if e1.s1.equivalent(pt) or e1.s2.equivalent(pt):
        # if e1.s1 == pt or e1.s2 == pt:
        #     return None

        # Next, if the point is ahead, check it's not already in Traj
        # if pstatus == 1 and len(traj1) > 1:
        #     if pt == traj1[1].s2:
        #         return None
        # might not be needed with the recursion prevention

        # If the point is behind, the next EDwP should catch duplicate.
        # Now, do the right things
        if pstatus == -1:
            newseg = stsegment(pt, e1.s1)
            return traj1.cloneAndReplace(newseg, e1)
        # if pt is s2, same code.
        newseg1 = stsegment(e1.s1, pt)
        newseg2 = stsegment(pt, e1.s2)
        return traj1.cloneAndReplace(newseg1, newseg2)
    
    # Return a shallow copy of T1, excluding first segment.
    def rest(self):
        return Trajectory(self.segments[1:])

    # Quantify how representative the first segments are
    def coverage(traj1, traj2):
        return traj1[0].length + traj2[0].length