"""Patterns 18-29: Graph Traversal.

Core idea: model first, algorithm second — what are nodes/edges, is it
directed, what does "visited" mean? Then: components -> DFS/Union-Find;
shortest unweighted -> BFS; shortest weighted -> Dijkstra; ordering with
prerequisites -> topological sort.
Run: python 04_graphs.py
"""
import heapq
from collections import defaultdict, deque


# --------------------------------------------------------------- Pattern 18
# DFS components: each fresh DFS consumes exactly one component.
def num_islands(grid: list[list[str]]) -> int:  # LC 200
    """Count connected groups of '1' cells in a grid.
    Each fresh DFS start consumes exactly one whole component, so the number
    of starts IS the answer. Sinking cells to '0' as you go makes the grid its
    own visited set — no second structure, and no cell is entered twice.

    Naive: flood from every land cell and compare the resulting cell sets to
    all earlier ones — O((rc)^2) of set work the sinking already encodes.

    Real life: dripping bleach on a map and watching one landmass fade at a
    time — the answer is how often you had to reach for the bottle."""
    rows, cols = len(grid), len(grid[0])

    def sink(r: int, c: int) -> None:
        if not (0 <= r < rows and 0 <= c < cols) or grid[r][c] != "1":
            return
        grid[r][c] = "0"                   # mutate grid = visited set
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sink(r + dr, c + dc)

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                count += 1                 # count = fresh DFS starts
                sink(r, c)
    return count


def pacific_atlantic(heights: list[list[int]]) -> list[list[int]]:  # LC 417
    """Cells from which rain can reach BOTH oceans.
    Forward, the question "where does this cell drain?" gets asked once per
    cell and the descents overlap. Reversed it becomes "how far inland can
    each ocean climb?" — two floods total, and the answer is their intersection.

    Naive: DFS downhill from every cell and check whether it reaches both
    oceans — O((rc)^2), re-walking the same slopes from every start.

    Real life: instead of asking each raindrop where it ends up, walk inland
    from each shoreline while the ground keeps rising — wherever both walks
    arrive, water can leave in either direction."""
    rows, cols = len(heights), len(heights[0])

    def flood(starts: list[tuple[int, int]]) -> set[tuple[int, int]]:
        seen = set(starts)
        stack = list(starts)
        while stack:
            r, c = stack.pop()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if (0 <= nr < rows and 0 <= nc < cols
                        and (nr, nc) not in seen
                        and heights[nr][nc] >= heights[r][c]):  # water climbs
                    seen.add((nr, nc))
                    stack.append((nr, nc))
        return seen

    pac = flood([(0, c) for c in range(cols)] + [(r, 0) for r in range(rows)])
    atl = flood([(rows - 1, c) for c in range(cols)]
                + [(r, cols - 1) for r in range(rows)])
    return [[r, c] for r, c in pac & atl]


# --------------------------------------------------------------- Pattern 19
# Multi-source BFS: seed ALL sources; first arrival = shortest distance.
def oranges_rotting(grid: list[list[int]]) -> int:  # LC 994
    """Minutes until nothing fresh is left, or -1 if some orange is unreachable.
    Seed the queue with EVERY rotten orange at once — multi-source BFS is
    still BFS, so first arrival is still the earliest possible time. One ring
    of the queue is one minute, which is why the level snapshot is the clock.

    Naive: BFS separately from each rotten orange and take the per-cell
    minimum — O(sources * rc), recomputing the same overlap every time.

    Real life: several fires lit at once in a dry field — a patch burns when
    whichever flame gets there first arrives, not once per fire."""
    rows, cols = len(grid), len(grid[0])
    q: deque[tuple[int, int]] = deque()    # invariant: holds exactly the cells rotting this minute
    fresh = 0                              # invariant: fresh oranges not yet reached
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                q.append((r, c))           # every rotten orange starts at t=0
            elif grid[r][c] == 1:
                fresh += 1
    minutes = 0
    while q and fresh:
        minutes += 1                       # one BFS ring = one minute
        for _ in range(len(q)):
            r, c = q.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    q.append((nr, nc))
    return -1 if fresh else minutes


def zero_one_matrix(mat: list[list[int]]) -> list[list[int]]:  # LC 542
    """Distance from every cell to the nearest 0.
    Read it backwards: "the nearest 0 to me" is the same relation as "how far
    the 0s spread to reach me", so seed all zeros and let one multi-source BFS
    fill outward. dist doubles as the visited set — -1 means unreached.

    Naive: BFS outward from every 1 until it meets a 0 — O((rc)^2). The
    reversal turns rc separate searches into a single sweep.

    Real life: rather than every house timing its own walk to a postbox, the
    postboxes send walkers out and each house notes who knocked first."""
    rows, cols = len(mat), len(mat[0])
    dist = [[-1] * cols for _ in range(rows)]   # invariant: -1 = unreached, else final distance
    q: deque[tuple[int, int]] = deque()
    for r in range(rows):
        for c in range(cols):
            if mat[r][c] == 0:
                dist[r][c] = 0
                q.append((r, c))
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return dist


# --------------------------------------------------------------- Pattern 20
# Directed cycle detection needs THREE colors: white/gray/black.
def can_finish(num_courses: int, prerequisites: list[list[int]]) -> bool:  # LC 207
    """Can every course be taken — i.e. is the prerequisite graph acyclic?
    Directed cycle detection needs THREE colors, not two: white unvisited,
    gray on the CURRENT path, black fully explored and safe. Two colors
    conflate "seen before" with "seen on this path" and cry cycle on a diamond.

    Naive: from each node, search whether it can reach itself — O(V * (V+E)),
    re-exploring the same subgraphs from every starting point.

    Real life: tracing who-approves-whom in a company — meeting someone
    already on your current chain is a deadlock, but meeting someone you
    cleared earlier on a different chain is fine."""
    graph = defaultdict(list)              # invariant: prereq -> courses it unlocks
    for course, pre in prerequisites:
        graph[pre].append(course)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * num_courses          # invariant: GRAY = on the current DFS path

    def dfs(u: int) -> bool:               # True = cycle found
        color[u] = GRAY                    # gray = on the CURRENT path
        for v in graph[u]:
            if color[v] == GRAY:           # back-edge into current path
                return True
            if color[v] == WHITE and dfs(v):
                return True
        color[u] = BLACK                   # black = fully explored, safe
        return False

    for u in range(num_courses):      # every component needs its own start
        if color[u] == WHITE and dfs(u):
            return False               # a cycle anywhere kills the whole order
    return True


# --------------------------------------------------------------- Pattern 21
# Kahn's: indegree 0 = no unmet dependencies -> emit, free neighbors.
def find_order(num_courses: int, prerequisites: list[list[int]]) -> list[int]:  # LC 210
    """A workable course order, or [] if the prerequisites cycle.
    Kahn's: indegree 0 means no unmet dependency, so that node is safe to emit
    now — and emitting it frees each neighbor by exactly one. A short output
    is itself the cycle test, since trapped nodes never reach indegree 0.

    Naive: rescan every node for one whose prerequisites are all done —
    O(V^2). The indegree counters turn that rescan into a decrement.

    Real life: assembling furniture by doing whichever step has nothing left
    blocking it, ticking off what each finished step unlocks."""
    graph = defaultdict(list)              # invariant: prereq -> courses it unlocks
    indeg = [0] * num_courses              # invariant: unmet prerequisites still owed by each course
    for course, pre in prerequisites:
        graph[pre].append(course)
        indeg[course] += 1
    q = deque(u for u in range(num_courses) if indeg[u] == 0)
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in graph[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == num_courses else []  # short = cycle ate the rest


def alien_order(words: list[str]) -> str:  # LC 269
    """Recover an alien alphabet's letter order from a sorted word list.
    Modeling is 90% of it: two adjacent words disagree usefully at exactly one
    place — their FIRST differing char, worth one edge; everything past it
    says nothing. Then it is plain Kahn's, plus the "abc" before "ab" trap.

    Naive: test all 26! candidate orderings against the list — hopeless. One
    edge per adjacent pair reduces the whole thing to a topological sort.

    Real life: deducing a clerk's alphabet from an already-sorted drawer —
    each neighbouring pair of folders reveals one precedence, and no more."""
    graph: dict[str, set[str]] = {c: set() for w in words for c in w}   # invariant: letter -> letters that must follow it
    indeg = {c: 0 for c in graph}          # invariant: letters that must still come before this one
    for w1, w2 in zip(words, words[1:]):
        for a, b in zip(w1, w2):
            if a != b:
                if b not in graph[a]:
                    graph[a].add(b)
                    indeg[b] += 1
                break
        else:
            if len(w1) > len(w2):          # "abc" before "ab" is invalid
                return ""
    q = deque(c for c in indeg if indeg[c] == 0)
    out = []
    while q:
        c = q.popleft()
        out.append(c)
        for d in graph[c]:
            indeg[d] -= 1
            if indeg[d] == 0:
                q.append(d)
    return "".join(out) if len(out) == len(graph) else ""


# --------------------------------------------------------------- Pattern 22
# Clone: map original -> clone breaks the cycle chicken-and-egg.
class GraphNode:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors or []


def clone_graph(node: GraphNode | None) -> GraphNode | None:  # LC 133
    """Deep-copy a graph that may contain cycles.
    Chicken and egg: filling a clone's neighbor list needs clones that don't
    exist yet. Registering the clone in the map BEFORE recursing breaks it —
    a cycle arriving back at u finds the half-built clone and links to that.

    Naive: copy all nodes in one pass, then wire neighbors in a second — fine,
    but it needs the full node list up front, which a traversal doesn't give.

    Real life: redrawing a subway map whose lines loop — you write a station's
    name the moment you first meet it, so the loop coming back links to that
    entry instead of starting a second copy of the station."""
    if not node:
        return None
    clones: dict[GraphNode, GraphNode] = {}   # invariant: original -> its clone, possibly still being wired

    def dfs(u: GraphNode) -> GraphNode:
        if u in clones:
            return clones[u]               # already created: just look up
        clones[u] = GraphNode(u.val)       # create BEFORE recursing (cycles!)
        clones[u].neighbors = [dfs(v) for v in u.neighbors]
        return clones[u]
    return dfs(node)


# --------------------------------------------------------------- Pattern 23
# Dijkstra: smallest tentative distance is FINAL (needs non-negative edges).
def network_delay_time(times: list[list[int]], n: int, k: int) -> int:  # LC 743
    """Time for a signal starting at k to reach all n nodes, or -1.
    Dijkstra's guarantee: with non-negative edges, the smallest tentative
    distance on the heap is already final — no later path can undercut it.
    That is exactly why `if u in dist: continue` drops stale entries safely.

    Naive: BFS ignores weights and answers the wrong question; enumerating
    all paths is exponential. The heap finalizes each node exactly once.

    Real life: gossip spreading through a town where each retelling takes a
    different amount of time — whoever hears it first heard it by the fastest
    route that exists, so their timestamp never needs revising."""
    graph = defaultdict(list)              # invariant: node -> (neighbor, weight) pairs
    for u, v, w in times:
        graph[u].append((v, w))
    dist: dict[int, int] = {}              # invariant: node -> FINAL shortest distance; membership = finalized
    heap = [(0, k)]                        # invariant: (tentative distance, node), smallest first
    while heap:
        d, u = heapq.heappop(heap)
        if u in dist:                      # stale entry: already finalized
            continue
        dist[u] = d
        for v, w in graph[u]:
            if v not in dist:
                heapq.heappush(heap, (d + w, v))
    return max(dist.values()) if len(dist) == n else -1


def minimum_effort_path(heights: list[list[int]]) -> int:  # LC 1631
    """Corner-to-corner path minimizing its single largest height step.
    Same Dijkstra skeleton as LC 743, different combine: a path costs its MAX
    edge, not their sum. Both work for the same reason — extending a path can
    never lower its cost, which is the monotonicity Dijkstra actually needs.

    Naive: binary search the answer and BFS-test each threshold — O(rc log H),
    workable, but it re-floods the whole grid once per candidate.

    Real life: picking a hike rated by its steepest single climb rather than
    total ascent — a long gentle detour beats one short cliff."""
    rows, cols = len(heights), len(heights[0])
    best = [[float("inf")] * cols for _ in range(rows)]   # invariant: smallest max-step known to reach each cell
    best[0][0] = 0
    heap = [(0, 0, 0)]
    while heap:
        d, r, c = heapq.heappop(heap)
        if (r, c) == (rows - 1, cols - 1):
            return d
        if d > best[r][c]:
            continue
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                nd = max(d, abs(heights[nr][nc] - heights[r][c]))
                if nd < best[nr][nc]:
                    best[nr][nc] = nd
                    heapq.heappush(heap, (nd, nr, nc))
    return 0


# --------------------------------------------------------------- Pattern 24
# Constraint changes the state: k rounds of relaxation = paths of <= k edges.
def find_cheapest_price(n, flights, src, dst, k) -> int:  # LC 787 Bellman-Ford
    """Cheapest src -> dst fare using at most k stops.
    The stop limit changes what state means: cost alone no longer identifies a
    node, so relax in ROUNDS — after round i, dist holds the best price using
    at most i edges. `nxt = dist[:]` is what stops one round chaining edges.

    Naive: Dijkstra ignores the limit and returns a cheaper, too-long route;
    enumerating every path of <= k+1 edges is exponential.

    Real life: the cheapest ticket you can actually buy with one layover — a
    cheaper three-leg itinerary exists, but it is not on offer."""
    dist = [float("inf")] * n              # invariant: after round i, best cost using <= i edges
    dist[src] = 0
    for _ in range(k + 1):                 # k stops = k+1 edges
        nxt = dist[:]                      # copy: this round may only extend
        for u, v, w in flights:            # last round's paths by ONE edge
            if dist[u] + w < nxt[v]:
                nxt[v] = dist[u] + w
        dist = nxt
    return -1 if dist[dst] == float("inf") else dist[dst]


# --------------------------------------------------------------- Pattern 25
# DSU: near-O(1) "same group?" under streaming merges.
class DSU:
    """Disjoint set union: near-O(1) "are these two in the same group?"
    Two questions, one structure — find answers "which group is x in?" and
    union answers "merge these two". Path halving flattens the tree on every
    find and union by size keeps the bigger tree as root, which together hold
    the height low enough that both operations stay effectively O(1).

    Naive: keep an explicit set per component and merge by copying — O(n)
    per union, and "same group?" costs a scan.

    Real life: a club where each member points at whoever recruited them —
    to name your club you follow the chain to the founder, and merging two
    clubs just repoints the smaller founder at the larger."""

    def __init__(self, n: int):
        self.parent = list(range(n))       # invariant: parent[x] == x iff x is its group's root
        self.size = [1] * n                # invariant: valid only at roots — members below are stale
        self.components = n                # invariant: number of distinct roots

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path halving
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> bool:  # False if already connected
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.size[ra] < self.size[rb]:     # union by size
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        self.components -= 1
        return True


def count_components(n: int, edges: list[list[int]]) -> int:  # LC 323
    # Number of connected components in an undirected graph.
    # DSU already tracks this: start at n singletons, and every union that
    # actually merges something drops the count by exactly one.
    # Naive: DFS from each unvisited node — same O(V+E), but it needs the
    # whole edge list built into an adjacency map first.
    # Real life: counting how many clubs remain after a night of introductions.
    dsu = DSU(n)
    for a, b in edges:
        dsu.union(a, b)
    return dsu.components


def find_redundant_connection(edges: list[list[int]]) -> list[int]:  # LC 684
    """The one extra edge that turns a tree into a graph with a cycle.
    Reverse the question: the redundant edge is the first one joining two
    nodes ALREADY connected, and union returning False is exactly that
    signal. No cycle hunt is needed — the cycle announces itself as it forms.

    Naive: remove each edge in turn and test whether the rest is still a
    connected tree — O(E * (V+E)).

    Real life: cabling rooms one run at a time and stopping at the first
    cable that links two rooms you could already walk between."""
    dsu = DSU(len(edges) + 1)              # invariant: nodes are 1-indexed, so slot 0 goes unused
    for a, b in edges:
        if not dsu.union(a, b):            # first edge inside one component
            return [a, b]
    return []


# --------------------------------------------------------------- Pattern 26
# Kosaraju: order by finish time, then DFS the REVERSED graph in that order —
# each pass carves out exactly one SCC.
def count_sccs(n: int, edges: list[tuple[int, int]]) -> int:
    """Count strongly connected components — groups where everyone reaches
    everyone. Kosaraju: DFS once recording finish times, then DFS the REVERSED
    graph in decreasing finish order. Reversal leaves each SCC intact but
    flips the edges between them, so each second-pass DFS cannot escape its own.

    Naive: test mutual reachability for every pair of nodes — O(V^2 * (V+E)).
    Two linear passes replace all of it.

    Real life: a city of one-way streets — a neighbourhood where everyone can
    still reach everyone survives every street being flipped, while the roads
    linking separate neighbourhoods stop letting you out."""
    graph, rev = defaultdict(list), defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        rev[v].append(u)
    seen = [False] * n
    order: list[int] = []                  # invariant: postorder = increasing finish time

    def dfs1(u: int) -> None:
        seen[u] = True
        for v in graph[u]:
            if not seen[v]:
                dfs1(v)
        order.append(u)                    # postorder = finish time

    for u in range(n):
        if not seen[u]:
            dfs1(u)
    seen = [False] * n
    sccs = 0
    for u in reversed(order):
        if not seen[u]:
            sccs += 1
            stack = [u]
            seen[u] = True
            while stack:
                x = stack.pop()
                for v in rev[x]:
                    if not seen[v]:
                        seen[v] = True
                        stack.append(v)
    return sccs


# --------------------------------------------------------------- Pattern 27
# Tarjan bridges: low[v] = earliest discovery reachable from v's subtree;
# edge (u,v) is a bridge iff low[v] > disc[u] (no back-door above u).
def critical_connections(n: int, connections: list[list[int]]) -> list[list[int]]:  # LC 1192
    """Bridges: edges whose removal would disconnect the graph.
    disc[u] is when u was discovered; low[v] is the earliest discovery time
    anything in v's subtree can still reach. low[v] > disc[u] says that
    subtree has no back-door above u, so (u,v) is its only way in — a bridge.

    Naive: delete each edge and re-test connectivity — O(E * (V+E)). One DFS
    answers it for every edge, because low propagates up as the calls return.

    Real life: a road network where each region learns how far back it can
    still reach by another route — a road is critical exactly when the region
    beyond it has no other way around to anywhere older."""
    graph = defaultdict(list)
    for u, v in connections:
        graph[u].append(v)
        graph[v].append(u)
    disc = [-1] * n                        # invariant: -1 = undiscovered, else its discovery time
    low = [0] * n                          # invariant: earliest disc reachable from u's subtree
    bridges: list[list[int]] = []
    timer = 0

    def dfs(u: int, parent: int) -> None:
        nonlocal timer
        disc[u] = low[u] = timer
        timer += 1
        for v in graph[u]:
            if v == parent:
                continue
            if disc[v] == -1:
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:       # subtree of v can't climb above u
                    bridges.append([u, v])
            else:
                low[u] = min(low[u], disc[v])   # back-edge

    for u in range(n):
        if disc[u] == -1:
            dfs(u, -1)
    return bridges


# --------------------------------------------------------------- Pattern 28
# Kruskal: cheapest edge crossing any cut is safe (cut property).
def min_cost_connect_points(points: list[list[int]]) -> int:  # LC 1584
    """Cheapest set of edges joining all points — an MST under Manhattan distance.
    Kruskal rests on the cut property: the cheapest edge crossing any cut is
    always safe to take. So sort by weight and take everything that doesn't
    close a cycle; DSU is what makes "would this close a cycle?" O(1).

    Naive: enumerate spanning trees — n^(n-2) of them. Even greedily, without
    DSU each cycle test costs a traversal.

    Real life: laying cable between towns cheapest run first, skipping any run
    between two towns the network already connects."""
    n = len(points)
    edges = sorted(
        (abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1]), i, j)
        for i in range(n) for j in range(i + 1, n))
    dsu = DSU(n)
    total = 0
    for w, i, j in edges:
        if dsu.union(i, j):                # skip = would close a cycle
            total += w
            if dsu.components == 1:
                break
    return total


# --------------------------------------------------------------- Pattern 29
# Bidirectional BFS: 2·b^(d/2) beats b^d. Always expand the smaller frontier.
def ladder_length(begin: str, end: str, word_list: list[str]) -> int:  # LC 127
    """Shortest chain from begin to end changing one letter at a time.
    Searching from both ends turns b^d into 2*b^(d/2), because the frontiers
    meet in the middle. Always expanding the SMALLER frontier is what holds
    that bound — otherwise the bushier side dominates the work anyway.

    Naive: one-directional BFS — correct, but it explores the whole ball of
    radius d around begin instead of two balls of radius d/2.

    Real life: two search parties starting at opposite ends of a trail network
    and meeting in the middle, with whichever party faces fewer paths moving next."""
    words = set(word_list)                 # invariant: words not yet visited by either frontier
    if end not in words:
        return 0
    front, back = {begin}, {end}           # invariant: front is the frontier being expanded next
    steps = 1
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    while front and back:
        if len(front) > len(back):
            front, back = back, front      # expand the cheaper side
        steps += 1
        nxt = set()
        for word in front:
            for i in range(len(word)):
                for c in alphabet:
                    cand = word[:i] + c + word[i + 1:]
                    if cand in back:       # frontiers met
                        return steps
                    if cand in words:
                        words.remove(cand)  # visited = removed
                        nxt.add(cand)
        front = nxt
    return 0


if __name__ == "__main__":
    assert num_islands([list("11000"), list("11000"),
                        list("00100"), list("00011")]) == 3
    assert sorted(pacific_atlantic([[1, 2, 2, 3, 5], [3, 2, 3, 4, 4],
                                    [2, 4, 5, 3, 1], [6, 7, 1, 4, 5],
                                    [5, 1, 1, 2, 4]])) == \
        [[0, 4], [1, 3], [1, 4], [2, 2], [3, 0], [3, 1], [4, 0]]
    assert oranges_rotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]]) == 4
    assert zero_one_matrix([[0, 0, 0], [0, 1, 0], [1, 1, 1]]) == \
        [[0, 0, 0], [0, 1, 0], [1, 2, 1]]
    assert can_finish(2, [[1, 0]]) and not can_finish(2, [[1, 0], [0, 1]])
    assert find_order(4, [[1, 0], [2, 0], [3, 1], [3, 2]])[0] == 0
    assert alien_order(["wrt", "wrf", "er", "ett", "rftt"]) == "wertf"
    assert network_delay_time([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2) == 2
    assert minimum_effort_path([[1, 2, 2], [3, 8, 2], [5, 3, 5]]) == 2
    assert find_cheapest_price(
        4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]],
        0, 3, 1) == 700   # the 500 route needs 2 stops: the limit, not cost, decides
    assert count_components(5, [[0, 1], [1, 2], [3, 4]]) == 2
    assert find_redundant_connection([[1, 2], [1, 3], [2, 3]]) == [2, 3]
    assert count_sccs(5, [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4)]) == 3
    assert critical_connections(4, [[0, 1], [1, 2], [2, 0], [1, 3]]) == [[1, 3]]
    assert min_cost_connect_points([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]]) == 20
    assert ladder_length("hit", "cog",
                         ["hot", "dot", "dog", "lot", "log", "cog"]) == 5
    print("04_graphs: all checks passed")
