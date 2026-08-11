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
    # Reverse the flow: DFS from each ocean UPHILL; answer = both reachable.
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
    rows, cols = len(grid), len(grid[0])
    q: deque[tuple[int, int]] = deque()
    fresh = 0
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
    # "Distance to nearest 0" = BFS FROM all zeros at once.
    rows, cols = len(mat), len(mat[0])
    dist = [[-1] * cols for _ in range(rows)]
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
    graph = defaultdict(list)
    for course, pre in prerequisites:
        graph[pre].append(course)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * num_courses

    def dfs(u: int) -> bool:               # True = cycle found
        color[u] = GRAY                    # gray = on the CURRENT path
        for v in graph[u]:
            if color[v] == GRAY:           # back-edge into current path
                return True
            if color[v] == WHITE and dfs(v):
                return True
        color[u] = BLACK                   # black = fully explored, safe
        return False

    return not any(color[u] == WHITE and dfs(u) for u in range(num_courses))


# --------------------------------------------------------------- Pattern 21
# Kahn's: indegree 0 = no unmet dependencies -> emit, free neighbors.
def find_order(num_courses: int, prerequisites: list[list[int]]) -> list[int]:  # LC 210
    graph = defaultdict(list)
    indeg = [0] * num_courses
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
    # Modeling is 90%: an edge per FIRST differing char of adjacent words.
    graph: dict[str, set[str]] = {c: set() for w in words for c in w}
    indeg = {c: 0 for c in graph}
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
    if not node:
        return None
    clones: dict[GraphNode, GraphNode] = {}

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
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))
    dist: dict[int, int] = {}
    heap = [(0, k)]
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
    # Same Dijkstra, different metric: path cost = MAX edge, not sum.
    rows, cols = len(heights), len(heights[0])
    best = [[float("inf")] * cols for _ in range(rows)]
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
    dist = [float("inf")] * n
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
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.size = [1] * n
        self.components = n

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
    dsu = DSU(n)
    for a, b in edges:
        dsu.union(a, b)
    return dsu.components


def find_redundant_connection(edges: list[list[int]]) -> list[int]:  # LC 684
    dsu = DSU(len(edges) + 1)
    for a, b in edges:
        if not dsu.union(a, b):            # first edge inside one component
            return [a, b]
    return []


# --------------------------------------------------------------- Pattern 26
# Kosaraju: order by finish time, then DFS the REVERSED graph in that order —
# each pass carves out exactly one SCC.
def count_sccs(n: int, edges: list[tuple[int, int]]) -> int:
    graph, rev = defaultdict(list), defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        rev[v].append(u)
    seen = [False] * n
    order: list[int] = []

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
    graph = defaultdict(list)
    for u, v in connections:
        graph[u].append(v)
        graph[v].append(u)
    disc = [-1] * n
    low = [0] * n
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
    words = set(word_list)
    if end not in words:
        return 0
    front, back = {begin}, {end}
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
        0, 3, 1) == 700
    assert count_components(5, [[0, 1], [1, 2], [3, 4]]) == 2
    assert find_redundant_connection([[1, 2], [1, 3], [2, 3]]) == [2, 3]
    assert count_sccs(5, [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4)]) == 3
    assert critical_connections(4, [[0, 1], [1, 2], [2, 0], [1, 3]]) == [[1, 3]]
    assert min_cost_connect_points([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]]) == 20
    assert ladder_length("hit", "cog",
                         ["hot", "dot", "dog", "lot", "log", "cog"]) == 5
    print("04_graphs: all checks passed")
