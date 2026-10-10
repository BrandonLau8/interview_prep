# Depth-First Search

**In one line:** You solve a whole tree or graph by deciding, for one node only,
what it is told by its parent, what it reports back, and what it writes down for
everyone.

**Assumes you know:** recursion and the one-level induction argument from
[recursion.md](recursion.md). You have written `max_depth` and can follow it,
but writing a new DFS feels like tracking several places at once.

**Not covered:** BFS and shortest paths, iterative DFS with an explicit stack,
and the backtracking choose / explore / un-choose template (`07_backtracking.py`,
and Example 3 of [recursion.md](recursion.md)).

## ELI5

An org chart. Every employee gets a memo from their manager, sends one report
back up to that manager, and can write on a whiteboard in the hallway that
everyone shares. To answer a question about the whole company, you only have to
decide what one employee does with those three things. Everyone else does the
same.

**Where the analogy breaks:** in two places.

Real employees work at the same time. DFS runs one employee at a time and
finishes their entire department before their colleague starts. That ordering is
why a shared whiteboard can be written and then erased safely.

And an org chart has one manager per person and no loops. A graph can give a
node two "managers", or route a memo back to someone who already sent one. In a
graph, the whiteboard has to record who has already been asked, or the memos
never stop.

## Actually

Every call to `dfs(node)` has exactly three channels:

    down (params)      what this node is told by its caller, before it acts
    up (return)        what this node hands back, after its children finish
    sideways (shared)  state every call reads and writes: res, best, visited

Most DFS uses one or two of them. Writing a DFS means filling in these blanks, in
this order, as English sentences about a single node:

    up        what does this call hand its parent? one sentence, no "and"
    down      what must this node be told to do its job?
    sideways  what gets recorded that no parent can use?
    seen      graphs only: seen ever, or seen on my current path?
    base      what are the answers above for None, or for out of bounds?

Then you check one level. If the base case is right, and the combine line is
right assuming the recursive calls return correct answers, the whole function is
right. You never trace two levels deep.

Down versus up is the traversal order, chosen deliberately:

    preorder    node knows its answer before its subtree  ->  pass it DOWN
    postorder   node needs its subtree's answers first    ->  return it UP

**The "and" test:** if your up-wire sentence needs an "and", you have two values
pretending to be one. Return the one a parent can build on. Put the other
sideways. Example 3 is this rule in full.

## The picture

```
                  |   ^
   down (params)  |   |  up (return)
                  v   |
              +-------------+
              |  dfs(node)  |  =====>  sideways state
              +-------------+          (res, best, visited)
                  |   ^
   down (params)  |   |  up (return)
                  v   |
              +-------------+
              | dfs(child)  |  =====>  the same sideways state
              +-------------+
```

Every node is the same box. The only design work is what rides each wire.

## Setup

Every tree example runs after this block.

```python
class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

#        1
#       / \
#      2   3
#     / \
#    4   5
small = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3))

#          1
#         /
#        2
#       / \
#      3   4
#     /     \
#    5       6
bent = TreeNode(1, TreeNode(2, TreeNode(3, TreeNode(5)), TreeNode(4, None, TreeNode(6))))
```

# Trees

The three tree examples climb on how many wires are in use: one, then two, then
two where the return value is not the answer.

## Example 1 — up wire only: max_depth (LC 104)

    up        the height of the subtree rooted here, counted in nodes
    down      nothing
    sideways  nothing
    base      None has height 0

```python
def max_depth(node):  # LC 104
    if node is None:
        return 0                     # base: an empty tree has height 0
    left = max_depth(node.left)      # trust it
    right = max_depth(node.right)    # trust it
    return 1 + max(left, right)      # up wire

print(max_depth(small))   # 3
print(max_depth(bent))    # 4
```

The numbers on the edges are what each call hands its parent:

```
              (1) returns 3
             /   \
          2 /     \ 1
           /       \
        (2)         (3)  returns 1
        / \
     1 /   \ 1
      /     \
    (4)     (5)          leaves return 1
```

Node 2 sees 1 and 1 and hands up 2. Node 1 sees 2 and 1 and hands up 3. At no
point do you look further down than one node's two children.

Same logic at `pattern_code/03_trees.py:271`.

## Example 2 — down wire plus sideways: binary_tree_paths (LC 257)

    up        nothing
    down      the path string from the root to my parent
    sideways  res, the list of finished paths
    base      a leaf, not None: write the finished path and stop

```python
def binary_tree_paths(root):  # LC 257
    res = []                                   # sideways: finished paths

    def dfs(node, path):                       # down wire: path so far
        path = path + str(node.val)
        if node.left is None and node.right is None:
            res.append(path)                   # leaf: write sideways, send nothing up
            return
        if node.left is not None:
            dfs(node.left, path + "->")
        if node.right is not None:
            dfs(node.right, path + "->")

    dfs(root, "")
    return res

print(binary_tree_paths(small))   # ['1->2->4', '1->2->5', '1->3']
```

**Adds:** state flowing down instead of up. The answer at a leaf is complete the
moment you arrive, so nothing needs to come back. `pattern_code/03_trees.py:187`
is the same code.

    call     path received   after adding self   writes to res
    dfs(1)   ""              "1"
    dfs(2)   "1->"           "1->2"
    dfs(4)   "1->2->"        "1->2->4"           "1->2->4"
    dfs(5)   "1->2->"        "1->2->5"           "1->2->5"
    dfs(3)   "1->"           "1->3"              "1->3"

`dfs(5)` receives exactly what `dfs(4)` received. Strings are immutable, so
node 4's addition never leaked into its sibling and there is nothing to undo.
Pass a mutable list down instead and you must `pop()` on the way out; that
version is Example 3 of [recursion.md](recursion.md).

## Example 3 — return value is not the answer: diameter (LC 543)

LC 543 asks for the number of edges on the longest path between any two nodes.
On `bent` the answer is 4, the path 5-3-2-4-6, and it does not touch the root.

**Step 1: try the obvious up wire.** "`dfs(node)` returns the diameter of my
subtree." Test whether a parent can use it:

```
            (1)      gets "diameter below me = 4" from node 2
            /        can it add its own edge and make 5?
          (2)
         /   \       no: the 4-path already uses BOTH of node 2's arms
       (3)   (4)     reaching node 1 would mean passing through 2 again
       /       \
     (5)       (6)
```

A parent cannot build on a bent path. What a parent can build on is the longest
straight-down path from its child: one arm, which it extends by one edge.

Say the real requirement: "I need the longest path anywhere below, AND the
longest straight path down from here." That is the "and" test failing. Two
values, two wires.

**Step 2: fill in the blanks.**

    up        height: nodes on the longest straight-down path from here
    down      nothing
    sideways  best: the longest bent path seen at any node so far
    base      None has height 0

This is everything one node does:

```
                    ^
                    |  return 1 + max(lh, rh)          ONE arm: a parent can extend it
                    |
                 (node)  ====>  best = max(best, lh + rh)    BOTH arms: bends here
                 /    \
             lh /      \ rh
               /        \
          left arm    right arm
```

Counting height in nodes makes `lh + rh` come out in edges directly: each arm of
`k` nodes contributes `k` edges once joined through this node.

**Step 3: code.**

```python
def diameter_of_binary_tree(root):  # LC 543
    best = 0                          # invariant: longest bent path seen so far

    def height(node):
        nonlocal best
        if node is None:
            return 0
        lh = height(node.left)
        rh = height(node.right)
        best = max(best, lh + rh)     # sideways: the path bending here
        return 1 + max(lh, rh)        # up: only one arm continues

    height(root)
    return best

print(diameter_of_binary_tree(bent))    # 4
print(diameter_of_binary_tree(small))   # 3
```

Same code at `pattern_code/03_trees.py:286`.

**Step 4: trace it.** Postorder, so children finish before parents. The up wire
is written on each edge.

```
            (1)          returns 4
            /
         3 /
          /
        (2)              lh=2  rh=2  best becomes 4
       /   \
    2 /     \ 2
     /       \
   (3)       (4)
   /           \
1 /             \ 1
 /               \
(5)              (6)
```

    order   node   lh   rh   lh+rh   best   returns
      1      5     0    0     0       0      1
      2      3     1    0     1       1      2
      3      6     0    0     0       1      1
      4      4     0    1     1       1      2
      5      2     2    2     4       4      3
      6      1     3    0     3       4      4

At node 1 the bend is only 3, and `max` keeps the 4 found at node 2. That is why
the answer must live sideways. Here is what happens if you only measure the bend
at the root:

```python
def diameter_wrong(root):
    def height(node):
        if node is None:
            return 0
        return 1 + max(height(node.left), height(node.right))
    return height(root.left) + height(root.right)   # only the bend AT the root

print(diameter_wrong(bent))   # 3, but the answer is 4
```

**Adds:** the return value and the answer come apart. You return the value that
composes upward and record the value that doesn't. `max_path_sum` (LC 124) at
`pattern_code/03_trees.py:312` is the same skeleton with sums in place of
counts.

# Graphs

Same box, same wires. What changes is that a tree hands every call a fresh node,
and a graph does not.

```
     tree                          graph
       (A)                           (A)
       / \                           / \
     (B) (C)                       (B) (C)
                                     \ /
     one parent per node             (D)     D reachable two ways
     each node reached once           |
                                     (A)     an edge back to A: a loop
```

So the sideways wire stops being optional. Every graph DFS needs state that
answers "have I been here?", and the three graph examples climb on what that
question means:

    Example 4   seen means skip it
    Example 5   seen means reuse its answer
    Example 6   seen splits in two: still on my path, or finished earlier

Each wire changes like this:

    up        still works, but the node you call may be finished or mid-call
    down      undirected graphs often pass `parent`, so the edge back isn't a loop
    sideways  mandatory: a visited set, a color array, or a memo map

## Example 4 — seen means skip: num_islands (LC 200)

    up        nothing
    down      nothing; (r, c) is only a position
    sideways  the grid itself: sinking "1" to "0" marks a cell visited
    seen      ever; a sunk cell is never entered again
    base      off the map, or not land

```python
def num_islands(grid):  # LC 200
    rows = len(grid)
    cols = len(grid[0])

    def sink(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols:
            return                      # base: off the map
        if grid[r][c] != "1":
            return                      # base: water, or already sunk
        grid[r][c] = "0"                # sideways: mark BEFORE recursing
        sink(r + 1, c)
        sink(r - 1, c)
        sink(r, c + 1)
        sink(r, c - 1)

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                count += 1              # one fresh start = one whole island
                sink(r, c)
    return count

grid = [
    ["1", "1", "0"],
    ["1", "0", "0"],
    ["0", "0", "1"],
]
print(num_islands(grid))   # 2
```

Pure flood fill carries nothing up or down. Everything is sideways. Same logic
at `pattern_code/04_graphs.py:15`.

Why mark before recursing:

```
   (0,0) <----> (1,0)      every grid edge goes both ways

   sink(0,0) -> sink(1,0) -> sink(0,0) -> ...
                               ^
                               already "0" if you marked first: returns at once
                               still "1" if you marked after: they call each other forever
```

## Example 5 — seen means reuse its answer: clone_graph (LC 133)

    up        the clone of this node
    down      nothing
    sideways  clones: original node -> its clone, acting as visited AND memo
    seen      ever; a seen node returns its existing clone
    base      the node is already in clones

```python
class GraphNode:
    def __init__(self, val):
        self.val = val
        self.neighbors = []

def clone_graph(node):  # LC 133
    if node is None:
        return None
    clones = {}                         # sideways: original -> clone

    def dfs(u):                         # up wire: the clone of u
        if u in clones:
            return clones[u]            # seen: reuse its answer
        copy = GraphNode(u.val)
        clones[u] = copy                # register BEFORE recursing
        for v in u.neighbors:
            copy.neighbors.append(dfs(v))
        return copy

    return dfs(node)

a = GraphNode(1)
b = GraphNode(2)
c = GraphNode(3)
a.neighbors = [b, c]
b.neighbors = [a, c]
c.neighbors = [a, b]                    # a triangle: every node is on a cycle

a2 = clone_graph(a)
print(a2 is a)                          # False: a new node
print(a2.neighbors[0].neighbors[0] is a2)   # True: the cycle is rebuilt inside the copy
```

**Adds:** seen nodes now carry an answer, so the up wire works across a cycle.
Same logic at `pattern_code/04_graphs.py:252`.

    call     clones before   action
    dfs(a)   {}              make a', register, recurse into b
    dfs(b)   {a}             make b', register, recurse into a
    dfs(a)   {a, b}          seen: return a' even though its neighbors are half-built
    dfs(c)   {a, b}          make c', register; neighbors a and b both seen
    dfs(c)   {a, b, c}       back in a: seen, return c'

The third row is the subtle part. `a'` is returned before it is finished. That
is fine here because a pointer to it is all `b'` needs, and the list fills in
when `dfs(a)` resumes.

## Example 6 — seen splits in two: can_finish (LC 207)

LC 207 gives `[course, prereq]` pairs and asks whether every course can be
taken, which means asking whether the directed graph has a cycle.

    up        True if a cycle is reachable from here
    down      nothing
    sideways  color per node: WHITE unseen, GRAY on the current path, BLACK finished
    seen      two different things: GRAY is a cycle, BLACK is safe
    base      a neighbor that is GRAY returns True

The trap is using one "visited" flag. Compare these two graphs:

```
   diamond, no cycle                 real cycle

         0                                0
        / \                               |
       v   v                              v
       1   2                              1
        \ /                               |
         v                                v
         3                                2 ---> 0
```

```python
def build_graph(num_courses, prerequisites):
    graph = []
    for i in range(num_courses):
        graph.append([])
    for pair in prerequisites:
        course = pair[0]
        prereq = pair[1]
        graph[prereq].append(course)     # edge: prereq -> course it unlocks
    return graph

diamond = [[1, 0], [2, 0], [3, 1], [3, 2]]
cycle = [[1, 0], [2, 1], [0, 2]]


def can_finish_wrong(num_courses, prerequisites):
    graph = build_graph(num_courses, prerequisites)
    seen = [False] * num_courses

    def dfs(u):
        seen[u] = True
        for v in graph[u]:
            if seen[v]:
                return True              # "seen" can't tell on-my-path from finished
            if dfs(v):
                return True
        return False

    for u in range(num_courses):
        if not seen[u] and dfs(u):
            return False
    return True

print(can_finish_wrong(4, diamond))   # False, but the diamond has no cycle


def can_finish(num_courses, prerequisites):  # LC 207
    graph = build_graph(num_courses, prerequisites)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * num_courses        # invariant: GRAY = on the current DFS path

    def dfs(u):                          # up wire: True = cycle found
        color[u] = GRAY                  # entering: now on the current path
        for v in graph[u]:
            if color[v] == GRAY:
                return True              # back to my own path: cycle
            if color[v] == WHITE and dfs(v):
                return True
        color[u] = BLACK                 # leaving: finished and safe
        return False

    for u in range(num_courses):         # a disconnected graph needs several starts
        if color[u] == WHITE and dfs(u):
            return False
    return True

print(can_finish(4, diamond))   # True
print(can_finish(3, cycle))     # False
```

**Adds:** "seen" now depends on where you are in the call stack. GRAY is the
down-then-up timing of the tree examples made visible: a node is GRAY between
entering and returning, which is exactly while it's an ancestor of the current
call. Same logic at `pattern_code/04_graphs.py:145`.

    diamond                               cycle
    enter 0      0 gray                   enter 0      0 gray
    enter 1      1 gray                   enter 1      1 gray
    enter 3      3 gray                   enter 2      2 gray
    leave 3      3 black                  2 sees 0     0 is gray: cycle
    leave 1      1 black
    enter 2      2 gray
    2 sees 3     3 is black: safe, skip
    leave 2      2 black
    leave 0      0 black

The wrong version marks 3 as seen at step 3 and then treats "2 sees 3" as a
cycle. Nothing about 3 being seen says it's on the current path.

## Gotchas

- **Returning the answer when it doesn't compose** — for diameter or max path
  sum, returning the answer gives the parent a bent path it can't extend. Return
  the straight arm and record the answer sideways (Example 3).

- **An "and" in the up-wire sentence** — it means two values. Either return a
  tuple, as `rob_tree` at `pattern_code/03_trees.py:339` does, or split one
  value off sideways.

- **Marking visited after recursing** — in any graph with a two-way edge, the
  neighbor walks straight back and the two calls recurse until
  `RecursionError`. Mark on entry (Examples 4 and 5).

- **One visited flag for directed cycle detection** — reports a cycle on every
  diamond. Use three colors (Example 6). Two colors are enough for flood fill and
  undirected connectivity, where "seen ever" is the right question.

- **Undirected cycle detection without `parent`** — the edge you just arrived on
  leads back to a visited node and looks like a cycle. Pass the parent down and
  skip it, as `critical_connections` does at `pattern_code/04_graphs.py:504`.

- **Base case in the wrong unit** — height in nodes wants None to be 0. Height
  in edges wants None to be -1. Mixing them makes diameter off by one or two.

- **Recursion depth on grids** — a 1000 by 1000 all-land grid can make Python
  recurse a million deep, far past its default limit of about 1000 frames.
  Convert to an explicit stack or BFS when a path can be that long.

- **Sinking the caller's grid** — Example 4 destroys its input. That is accepted
  on LeetCode. In an interview, say so, or copy the grid first.

## Related

- **Recursion** — [recursion.md](recursion.md) has the one-level induction
  argument every example here leans on.
- **Backtracking** — DFS over choices, where sideways state is undone on the
  way out. `pattern_code/07_backtracking.py` is ten of them.
- **BFS** — visits by distance instead of by depth. Use it when the question is
  "fewest steps", which DFS can't answer without trying every path.
- **Topological sort** — LC 207 by Kahn's indegree BFS instead of three colors,
  at `pattern_code/04_graphs.py:181`.
- **Memoized DP** — Example 5's memo generalized: DFS over a graph of
  subproblems, where a finished node returns its cached answer.
- **Stack** — [stack.md](stack.md); iterative DFS replaces the call stack with
  one you manage.

## Sources

- CLRS, 3rd edition, section 22.3 "Depth-first search" — the WHITE / GRAY /
  BLACK coloring and why a GRAY neighbor means a back edge.
- `pattern_code/03_trees.py` and `pattern_code/04_graphs.py` — the verified
  versions of every example, runnable with `uv run python`.
