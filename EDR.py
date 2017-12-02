# mock implementation of
# Robust and Fast Similarity Search for Moving Object Trajectories

S1 = [(0,0), (1,3), (3,6)]
S2 = [(0,0), (2,3), (4,6)]
S3 = [(0,0), (1,2), (2,4), (3,6)]
S4 = [(0,0), (1,1), (1,2), (2,3), (2,4), (3,5), (3,6)]

# threshold of equivalence
DIFF = 2

# two tuples
def eq(c1, c2):
    return (abs(c1[0] - c2[0]) <= DIFF) and (abs(c1[1] - c2[1]) <= DIFF)

def EDR(S, R):
    if len(S) == 0:
        return len(R)
    if len(R) == 0:
        return len(S)
    subcost = 0 if eq(S[0], R[0]) else 1;
    a = EDR(R[1:], S[1:]) + subcost
    b = EDR(R[1:], S    ) + 1
    c = EDR(R    , S[1:]) + 1
    return min(a, b, c)

print("S1-S2: ", EDR(S1, S2))
print("S1-S3: ", EDR(S1, S3))
print("S2-S3: ", EDR(S2, S3))
print("S3-S4: ", EDR(S3, S4))