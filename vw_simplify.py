import heapq
import functools

# simplification algorithm adapted from
# Mike Bostok,  https://bost.ocks.org/mike/simplify/simplify.js

@functools.total_ordering
class Triangle:
    def __init__(self, v1, v2, v3):
        self.prev = None
        self.next = None
        # each v is (x,y,t)
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.v2[3] = self.getarea()

    def __lt__(self, other):
        return self.area < other.area

    def __eq__(self, other):
        return self.area == other.area

    @property
    def area(self):
        return self.v2[3]

    @area.setter
    def area(self, value):
        self.v2[3] = value

    # given triangle with 1 vertex at origin
    # and 2 points, (a,b) (c,d)
    # area = | ad - bc | / 2
    def getarea(self):
        #                a                           d
        ad = (self.v2[0] - self.v1[0]) * (self.v3[1] - self.v1[1])
        #                b                           c
        bc = (self.v2[1] - self.v1[1]) * (self.v3[0] - self.v1[0])
        return abs(ad - bc) / 2


def identity(x):
    return x

def update(triangle, heap):
    triangle.area = triangle.getarea()
    heapq.heapify(heap)

def rate_area(data, key=identity):
    data = [[*x, 0] for x in data] # make a 4th element for area
    maxArea = 0
    triangles = []
    for i in range(1, len(data) - 1):
        triangles.append(Triangle(data[i-1], data[i], data[i+1]))
    for i, triangle in enumerate(triangles):
        if i != 0:
            triangle.prev = triangles[i-1]
        if i < len(triangles) - 1:
            triangle.next = triangles[i+1]
    # list of references
    heap = [x for x in triangles]
    heapq.heapify(heap)
    while len(heap) > 0:
        triangle = heapq.heappop(heap)
        if (triangle.area < maxArea):
            triangle.area = maxArea
        else:
            maxarea = triangle.area
        if triangle.prev:
            triangle.prev.next = triangle.next
            triangle.prev.v3 = triangle.v3
            update(triangle, heap)
        else:
            # if first triangle, memo area
            triangle.v1[3] = triangle.area

        if triangle.next:
            triangle.next.prev = triangle.prev
            triangle.next.v1 = triangle.v1
            update(triangle, heap)
        else:
            # if last triangle, memo area
            triangle.v3[3] = triangle.area
    return data

def by_threshold(data, threshold):
    out = []
    for point in data:
        if point[3] >= threshold:
            out.append(point)
    return out

def by_number(data, number):
    areas = [p[3] for p in data]
    areas.sort(reverse=True)
    return by_threshold(data, areas[number - 1])

def by_ratio(data, ratio):
    n = len(data)
    return by_number(data, int(ratio * n))

def simplify(data, ratio=0.5, threshold=None, number=None):
    data = rate_area(data)
    if threshold:
        return by_threshold(data, threshold)
    if number:
        return by_number(data, number)
    return by_ratio(data, ratio)

if __name__=="__main__":
    import os
    import json

    root = "data_segmented-paths/"
    outdir = "data_simple-segments/"
    for file in os.listdir(root):
        with open(root + file) as f:
            data = json.load(f)
        output = []
        for arr in data:
            if len(arr) > 10:
                arr = simplify(arr, ratio=0.2)
                arr = [x[:3] for x in arr] # strip out area factor
            output.append(arr)
        with open(outdir + file, "w") as f:
            json.dump(output, f)