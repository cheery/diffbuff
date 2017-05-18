"""
    diffbuff.treediff
    ~~~~~~~~~~~~~~~~~

    Diff implementation on diff buffers

    Not working.
"""
import wire
from wire import Node
from collections import namedtuple, defaultdict


# Yuan Wang, "X-Diff: An Effective Change Detection Algorithm for XML Documents"
def x_diff(a, b):
    M = []
    d, P, L, R = x_distance_them(a, b, (lambda node: (node.tag, node.kind)))
    for l, r, d in P:
        if x_match(M, l, r, d):
            M.append((0, l, r))
    for z in L:
        M.append((1, z))
    for z in R:
        M.append((2, z))
    return M

def x_match(M, node1, node2, data):
    if isinstance(node1, Node) and isinstance(node1.value, (set, dict, list)):
        assert isinstance(node2, Node)
        assert node1.tag == node2.tag
        assert node1.kind == node2.kind
        #node1.value
        #node2.value
        assert False, "TODO"
    else:
        assert False, "TODO"
        if node1 != node2:
            M.append((0, (node1, node2)))
    # TODO: use diff on these.
    #elif isinstance(node1, unicode):
    #elif isinstance(node1, str):

def x_distance(node1, node2):
    if isinstance(node1, Node):
        assert isinstance(node2, Node)
        assert node1.tag == node2.tag
        assert node1.kind == node2.kind
        assert False, "TODO"
    else:
        assert False, "TODO"

def x_distance_them(group1, group2, get_signature):
    P = []
    L = []
    R = []
    distance = 0
    lookup = dict(
        ((hash(node2), get_signature(node2)), node2)
        for node2 in group2)
    # filter out all subtrees with equal XHash values and equal signature.
    # they are immediately matched.
    pairs = defaultdict(lambda: ([],[]))
    for node1 in a:
        sig = get_signature(node1)
        key = (hash(node1), sig)
        if key in match_l:
            node2 = match_l.pop(key)
            P.append((node1, node2, None))
        else:
            pairs[sig][0].append(node1)
    for (h, sig), node2 in lookup.iteritems():
        pairs[sig][1].append(node2)

    for (xs, ys) in pairs.itervalues():
        if len(ys) == 0:
            for node1 in xs: # all remaining xs are deletions
                distance += node1.count
                L.append(node1)
        if len(xs) == 0:
            for node2 in ys: # all remaining ys are insertions
                distance += node2.count
                R.append(node2)

        C = []
        D = []
        for node1 in xs:
            Cx = []
            Dx = []
            for node2 in ys:
                c, d = x_distance(node1, node2)
                Cx.append(c)
                Dx.append(d)
            C.append(Cx)
            D.append(Dx)

        r_xs = set(range(len(xs)))
        r_ys = set(range(len(ys)))
        for x, y in hungarian(C, len(xs), len(ys)):
            distance += C[x][y]      # We finally get the costs at here.
            P.append((xs[x], ys[y], D[x][y])) 
            r_xs.discard(x)          # But actually building the table
            r_ys.discard(y)          # has been done already as well.
        for x in r_xs: # all remaining xs are deletions.
            node1 = xs[x]
            distance += node1.count
            L.append(node1)
        for y in r_ys: # all remaining ys are insertions.
            node2 = ys[y]
            distance += node2.count
            R.append(node2)
    return distance, P, L, R

def diff(a, b):
    edit_script = []
    matches = lcs(a, b)
    matches.append((len(a), len(b), 0))
    x = 0
    y = 0
    for i, j, c in matches:
        if i > x or j > y or c > 0:
            edit_script.append((a[x:i], b[y:j], c))
        x = i+c
        y = j+c
    return edit_script

# This link helped out at figuring out the small details:
#   https://gist.github.com/tonyg/2361e3bfe4e92a1fc6f7
# E. W. Myers, "An O(ND) difference algorithm and its variations,"
# E. Ukkonen, "Algorithms for approximate string matching," Inf.
def lcs(a, b):
    maximum = len(a) + len(b)
    vec = [0] * (2 * maximum + 1)
    candinates = [None] * (2 * maximum + 1)
    for d in range(maximum + 1):
        for k in range(-d, d+1, 2):
            if k == -d or (k != d and vec[maximum + k-1] < vec[maximum + k+1]):
                index = maximum + k + 1
                x = vec[index]
            else:
                index = maximum + k - 1
                x = vec[index] + 1
            y = x - k
            chain = candinates[index]
            c = 0
            while x < len(a) and y < len(b) and a[x] == b[y]:
                x += 1
                y += 1
                c += 1
            if c > 0:
                chain = ((x-c, y-c, c), chain)
            if x >= len(a) and y >= len(b):
                result = []
                while chain:
                    result.append(chain[0])
                    chain = chain[1]
                result.reverse()
                return result
            vec[maximum + k] = x
            candinates[maximum + k] = chain

# KF-Diff+ adaptation on sets
def udiff(a, b):
    lhs = []
    rhs = []
    a = sorted(a)
    b = sorted(b)
    while len(a) > 0 and len(b) > 0:
        x = a.pop()
        y = b.pop()
        while len(b) > 0 and x < y:
            rhs.append(y)
            y = b.pop()
        if x != y:
            lhs.append(x)
    lhs.extend(a)
    rhs.extend(b)
    return lhs, rhs

#def mdiff(a, b):
#

# hs[i] = null where i in (2, DEPTH) maximal depth
# for v in doc1
#   assign v an ID denoted by EID()
#   find out whether node belongs to MI
#     and compute KLab(v)
# for v in doc2
#   assign v an ID denoted by EID()
#   find out whether node belongs to MI
#     and compute KLab(v)
#
# algorithm(r1, r2):
#   empty tempset1, tempset2
#   deleted, inserted, updates, nodes sets.
#   first step: if lab(r1) != lab(r2) return null
#     else tempset1 = children(r1)
#          tempset2 = children(r2)
#   second step: call MatchFunc(tempset1, tempset2)
#   return changes

# matchfunc(tempset1, tempset2)
#   tempset = set()
#   sort elements in both sets
#   compare tempset1 with tempset2, according klab()
#   for each matching pair v, v'
#     remove from tempsets
#     add v, v' to M
#     if v is leaf node
#       if val(v) != val(v') add v, val(v') to updated
#     else
#       add v to tempset
#   add remaining nodes in tempset1 to deleted
#   add remaining nodes in tempset2 to inserted
#   for each element v in tempset
#     get v2 in M
#     call MatchFunc(v, v2)


def hungarian(cost, xs, ys):
    if xs <= ys:
        xy = hungarian_fn((lambda x, y: cost[x][y]), xs, ys)
        for x, y in enumerate(xy):
            yield x, y
    else:
        yx = hungarian_fn((lambda x, y: cost[y][x]), ys, xs)
        for y, x in enumerate(yx):
            yield x, y

# https://en.wikipedia.org/wiki/Hungarian_algorithm
def hungarian_fn(cost, xs, ys):
    h = Hungarian(cost, xs, ys,
        xy = [-1] * xs, # Initial answer
        yx = [-1] * ys,
        # These form a potential
        # The potential have to be set to a 'bottom' of the weights,
        # so that there forms a residual to lift from for code lifting the
        # potential upwards.
        px = [min(cost(x,y) for y in range(ys)) for x in range(xs)], 
        py = [0] * ys,
        S = [False] * xs, # Halves of Z
        T = [False] * ys,
        prev = [-1] * xs)
    for _ in range(xs):
        hungarian_match1(h)
    return h.xy

# The computational complexity of this algorithm is terrible
# but when I tested this, it will take sub-milliseconds to run
# through the larger matrices I could generate.
def hungarian_match(h):
    for x in range(h.xs):
        h.S[x] = False
        h.prev[x] = -1
    for y in range(h.ys):
        h.T[y] = False
    # One residual vertex is required to compute Z
    r = h.xy.index(-1)
    h.S[r] = True
    bfs = [r]
    while True:
        while len(bfs) > 0:
            x = bfs.pop(0)
            for y in range(h.ys):
                if h.T[y] or h.cost(x, y) != h.px[x] + h.py[y]:
                    continue
                if h.yx[y] == -1: # Means that another residual was found.
                    return hungarian_reverse(h, x, y)
                h.T[y] = True
                nx = h.yx[y]
                if h.S[nx]:
                    continue
                bfs.append(nx)
                h.prev[nx] = x
                h.S[nx] = True
        # An another residual was not found, so the
        # potential must be lifted.
        d = None
        for x in range(h.xs):
            if h.S[x]:
                for y in range(h.ys):
                    if not h.T[y]:
                        c = h.cost(x, y) - h.px[x] - h.py[y]
                        if d is None or c < d:
                            d = c
        assert d != None
        for x in range(h.xs):
            if h.S[x]:
                h.px[x] += d
        for y in range(h.ys):
            if h.T[y]:
                h.py[y] -= d

        for x in range(h.xs):
            if not h.S[x]:
                continue
            for y in range(h.ys):
                if h.T[y] or h.cost(x, y) != h.px[x] + h.py[y]:
                    continue
                if h.yx[y] == -1:
                    return hungarian_reverse(h, x, y)
                h.T[y] = True
                nx = h.yx[y]
                if h.S[nx]:
                    continue
                bfs.append(nx)
                h.prev[nx] = x
                h.S[nx] = True

def hungarian_reverse(h, x, y):
    while x != -1:
        ny = h.xy[x]
        h.yx[y] = x
        h.xy[x] = y
        x = h.prev[x]
        y = ny

Hungarian = namedtuple('Hungarian', [
    'cost', 'xs', 'ys',
    'xy', 'yx', 'px', 'py', 'S', 'T',
    'prev' ])
