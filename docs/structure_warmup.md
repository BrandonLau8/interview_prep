# Structure warmup

This file has one short, runnable example for each idiom you need once the
input stops being a flat array: linked lists, trees, graphs, and the string
and number tricks that come up alongside them. Each block ends with an
`assert`, so you can paste it into `main.py` and run it.

Assumes you know: section 0 of `docs/array_warmup.md` (several idioms here
reuse its loop shapes), and recursion (`docs/concepts/recursion.md`).
Not covered: segment trees. Dijkstra, tries, and heaps are in
`docs/search_warmup.md`.

How to use it: read the task, cover the code, and write it from memory. Then
run the asserts and say the invariant out loud. If you can't explain why the
trap breaks it, you memorized the code without understanding it.

    1. Linked lists
    walk                    while cur is not None, not cur.next
    dummy head              return dummy.next; don't advance prev after a delete
    reverse in place        save next before you rewire cur.next
    fast / slow middle      fast is not None first in the and
    kth from end            open a k-node gap, then move both
    merge two sorted        one link attaches the leftover; no drain loop

    2. Trees
    base case first         if node is None: return the identity
    pass down               state rides in the arguments; check for a leaf explicitly
    return up               return one side to the parent, record both sides
    BFS by level            freeze size before the inner loop
    iterative inorder       push the left spine, pop, go right
    BST bounds              pass (lo, hi) down; children-only checks miss grandchildren

    3. Graphs
    adjacency list          one list per node; undirected adds both directions
    mark before recursing   visited[u] = True on entry, or a cycle recurses forever
    grid DFS                bounds, check, mark, spread: in that order
    BFS shortest path       mark on push; dist of -1 doubles as visited
    topological sort        emitted < n means a cycle
    union-find              link roots, not nodes; union returns False on a cycle
    three colours           directed cycles need an "in progress" state

    4. Strings and numbers
    char to index           ord(c) - ord('a'); 26 slots, not 128
    build, then join        append pieces, join once
    multi-digit parse       num = num * 10 + digit; flush the last run after the loop
    digit extraction        % 10 then // 10; negatives differ in Java
    ceil division           (a + b - 1) // b, never through a float
    2-D init                one list per row, never [[0] * cols] * rows
    DP table                n+1 slots per side; dp index i is string index i - 1

Every idiom uses the same names, so a name tells you the variable's role:

    head          the first node of a list
    cur           the node being looked at
    prev, nxt     the node before cur, and cur.next saved before rewiring
    dummy, tail   a fake node before head, and the last node of a list being built
    slow, fast    two walkers moving at different speeds
    node, root    a tree node, and the top of the tree
    left, right   the results returned by the two subtrees
    queue, stack  nodes waiting to be processed
    size, level   the frozen size of the current BFS level, and its values
    n             the number of nodes in a graph, or the length of a string
    u, v          a graph node, and one of its neighbours
    adj           adjacency list: adj[u] = neighbours of u
    visited       visited[u] = u has been reached
    dist          dist[u] = edges from the source, -1 if not reached yet
    indegree      indegree[v] = edges still pointing into v
    parent        union-find: parent[x], where x is a root if parent[x] == x
    state         three-colour DFS: 0 unvisited, 1 in progress, 2 done
    r, c          a grid cell; rows, cols are the grid size
    freq          a tally array indexed by letter
    best          the answer so far
    out           the output
    dp            the DP table

### Setup — run this first

The list and tree idioms use these classes and builders. The graph idioms
after the first one call `build_adj` from "Adjacency list."

```python
from collections import deque

class ListNode:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def build_list(vals):                  # [1, 2, 3] -> 1 -> 2 -> 3
    dummy = ListNode(0)
    tail = dummy
    for i in range(len(vals)):
        tail.next = ListNode(vals[i])
        tail = tail.next
    return dummy.next

def to_array(head):
    out = []
    cur = head
    while cur is not None:
        out.append(cur.val)
        cur = cur.next
    return out

def build_tree(vals):                  # level order, None = missing child: [1, None, 2]
    if len(vals) == 0 or vals[0] is None:
        return None
    root = TreeNode(vals[0])
    queue = deque([root])
    i = 1
    while i < len(vals):
        node = queue.popleft()
        if vals[i] is not None:
            node.left = TreeNode(vals[i])
            queue.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i])
            queue.append(node.right)
        i += 1
    return root
```


## 1. Linked lists

### Walk — while cur is not None

Task: return the number of nodes in a list.

```python
# shorthand: start at the head, count the node, step to the next one until you fall off the end
def length(head):
    count = 0
    cur = head                         # invariant: count = nodes before cur
    while cur is not None:
        count += 1
        cur = cur.next
    return count

assert length(build_list([1, 2, 3])) == 3
assert length(None) == 0                           # empty list: loop never runs
```

Trap: `while cur.next is not None` stops on the last node without counting
it, and it crashes on an empty list. Use that form only when you need to stop
at the last node, for example to append after it. Walk with `cur`, never with
`head`, or you lose the start of the list.

### Dummy head — return dummy.next

Task: remove every node whose value is `val`, including the head if it
matches.

```python
# shorthand: put a fake node before the head, unlink each matching node after prev, return the node after the fake one
def remove_value(head, val):  # LC 203
    dummy = ListNode(0)
    dummy.next = head
    prev = dummy                       # invariant: prev and everything before it is kept
    while prev.next is not None:
        if prev.next.val == val:
            prev.next = prev.next.next # unlink; prev stays, because the new prev.next is unchecked
        else:
            prev = prev.next
    return dummy.next

assert to_array(remove_value(build_list([1, 2, 1, 3]), 1)) == [2, 3]
assert to_array(remove_value(build_list([7, 7]), 7)) == []   # every node removed, head included
```

Trap: returning `head` returns a deleted node whenever the head matched. The
dummy exists so the head is never a special case. Advancing `prev` after a
delete skips the next node, which breaks on two matches in a row. It's the
same asymmetry as Dutch flag's `hi` swap: after a delete, the node in front of
you hasn't been checked.

### Reverse in place — save next first

Task: reverse a list and return its new head.

```python
# shorthand: save the next node, point the current node back, step prev and cur forward
def reverse_list(head):  # LC 206
    prev = None                        # invariant: prev = head of the already-reversed part
    cur = head
    while cur is not None:
        nxt = cur.next                 # save it: the next line destroys cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    return prev

assert to_array(reverse_list(build_list([1, 2, 3]))) == [3, 2, 1]
assert reverse_list(None) is None                  # empty list: prev is still None
```

Trap: without `nxt`, `cur.next = prev` cuts off the rest of the list. This is
swap with tmp for pointers. Return `prev`, not `cur`, because `cur` is `None`
when the loop ends. The four lines go in a fixed order: save, rewire, step
prev, step cur.

### Fast / slow — the middle

Task: return the middle node. For an even length, return the second of the
two middles.

```python
# shorthand: move slow one step and fast two steps until fast runs out; slow is at the middle
def middle(head):  # LC 876
    slow = head
    fast = head                        # invariant: fast has taken twice as many steps as slow
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
    return slow

assert middle(build_list([1, 2, 3])).val == 2
assert middle(build_list([1, 2, 3, 4])).val == 3   # even length: the second middle
assert middle(build_list([1])).val == 1            # single node: the loop never runs
```

Trap: `fast is not None` has to come first in the `and`, or an even-length
list reads `None.next`. To split a list in half (LC 148, LC 234), you want the
first middle, so start with `fast = head.next`. The same loop detects a cycle
(LC 141): if `slow == fast` after a step, there is one.

### Kth from end — open the gap first

Task: return the k-th node from the end, where `1 <= k <= length`.

```python
# shorthand: move fast k steps ahead, then move both until fast falls off; slow is k from the end
def kth_from_end(head, k):
    fast = head
    for i in range(k):
        fast = fast.next
    slow = head                        # invariant: fast is k nodes ahead of slow
    while fast is not None:
        slow = slow.next
        fast = fast.next
    return slow

assert kth_from_end(build_list([1, 2, 3, 4, 5]), 2).val == 4
assert kth_from_end(build_list([1, 2, 3]), 3).val == 1   # k == length: the head itself
```

Trap: when fast falls off the end, slow is exactly k nodes from it. To delete
the k-th from the end (LC 19), you need the node before it, so start both
walkers at a dummy. Then `k == length` deletes the head without a special
case.

### Merge two sorted — attach the leftover

Task: merge two sorted lists into one sorted list by relinking the nodes.

```python
# shorthand: hang the smaller front node off the tail until one list runs out, then hang the rest
def merge_lists(a, b):  # LC 21
    dummy = ListNode(0)
    tail = dummy                       # invariant: dummy.next .. tail = sorted merge so far
    while a is not None and b is not None:
        if a.val <= b.val:
            tail.next = a
            a = a.next
        else:
            tail.next = b
            b = b.next
        tail = tail.next
    if a is not None:                  # one link, not a drain loop: the rest is already chained
        tail.next = a
    else:
        tail.next = b
    return dummy.next

assert to_array(merge_lists(build_list([1, 4]), build_list([2, 3, 5]))) == [1, 2, 3, 4, 5]
assert to_array(merge_lists(None, build_list([1]))) == [1]   # one side empty
```

Trap: forget `tail = tail.next` and every node overwrites the same slot.
Compare this with merging arrays, where you have to copy the leftovers one at
a time. Here a single assignment attaches the whole remaining chain.


## 2. Trees

### Base case first — None returns the identity

Task: return the depth of the tree: the number of nodes on the longest path
from the root down to a leaf.

```python
# shorthand: an empty tree has depth 0; otherwise one plus the deeper child
def max_depth(node):  # LC 104
    if node is None:
        return 0                       # identity: an empty tree adds nothing
    left = max_depth(node.left)
    right = max_depth(node.right)
    return 1 + max(left, right)

assert max_depth(build_tree([3, 9, 20, None, None, 15, 7])) == 3
assert max_depth(None) == 0                        # empty tree
assert max_depth(build_tree([1, 2, None, 3])) == 3 # lopsided: a child is missing at each level
```

Trap: testing `node.left is None` and `node.right is None` before each call
turns one base case into four branches. Let the call on `None` return the
identity instead: 0 for a count or depth, `True` for "all nodes satisfy,"
`float('-inf')` for a max.

### Pass down — state rides in the arguments

Task: return whether any root-to-leaf path sums to `target`.

```python
# shorthand: subtract this node from what's left of the target; at a leaf, check whether nothing is left
def has_path_sum(node, remaining):  # LC 112
    if node is None:
        return False
    remaining -= node.val              # invariant: remaining = target - sum(root .. node)
    if node.left is None and node.right is None:
        return remaining == 0          # leaf: the path ends here
    return has_path_sum(node.left, remaining) or has_path_sum(node.right, remaining)

tree = build_tree([5, 4, 8, 11, None, 13, 4, 7, 2])
assert has_path_sum(tree, 22) is True              # 5 -> 4 -> 11 -> 2
assert has_path_sum(build_tree([1, 2]), 1) is False    # 1 isn't a leaf: its left child exists
```

Trap: test for the leaf explicitly. If you return `remaining == 0` at `None`
instead, then `[1, 2]` with target 1 returns `True` through the missing right
child, which is a path that ends at a node that isn't a leaf. Each call gets
its own `remaining`, so there's nothing to undo on the way back up.

### Return up — return one side, record both

Task: return the diameter: the number of edges on the longest path between
any two nodes. The path doesn't have to pass through the root.

```python
# shorthand: each node returns its height to its parent, and records left height + right height as a candidate
def diameter(root):  # LC 543
    best = [0]                         # a box so the helper can write to it; Java: a field
    def height(node):
        if node is None:
            return 0
        left = height(node.left)
        right = height(node.right)
        if left + right > best[0]:     # the path that bends here: uses both sides
            best[0] = left + right
        return 1 + max(left, right)    # the path the parent can extend: one side only
    height(root)
    return best[0]

assert diameter(build_tree([1, 2, 3, 4, 5])) == 3              # 4 -> 2 -> 1 -> 3
assert diameter(build_tree([1, 2, None, 3, 4, 5, None, 6])) == 4   # best path skips the root
```

Trap: what you return and what you record are different values. Returning
`left + right` to the parent is wrong, because a path that already bends at
this node can't be extended upward. The answer counts edges, and the height
counts nodes, which is why `left + right` needs no `- 1`. LC 124 is the same
shape with sums and a `max(0, ...)` that drops negative branches.

### BFS by level — freeze the size

Task: return the values level by level, as a list of lists.

```python
# shorthand: take the queue's size, pop exactly that many nodes as one level, push their children for the next level
def level_order(root):  # LC 102
    out = []
    if root is None:
        return out
    queue = deque([root])              # invariant: at the top of the loop, queue holds exactly one level
    while len(queue) > 0:
        size = len(queue)              # freeze it: the loop below appends the next level
        level = []
        for i in range(size):
            node = queue.popleft()
            level.append(node.val)
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
        out.append(level)
    return out

assert level_order(build_tree([3, 9, 20, None, None, 15, 7])) == [[3], [9, 20], [15, 7]]
assert level_order(None) == []                     # empty tree
```

Trap: in Java, `for (int i = 0; i < queue.size(); i++)` re-reads the size on
every iteration, so the children you push join the current level. Python's
`range(len(queue))` happens to evaluate once, which hides the bug. Use
`deque.popleft()`, not `list.pop(0)`, which is O(n). In Java, use
`ArrayDeque` with `offer` and `poll`.

### Iterative inorder — left spine, pop, go right

Task: return the inorder traversal (left, node, right) without recursion.

```python
# shorthand: push every left child, pop one and record it, then move to its right child
def inorder(root):  # LC 94
    out = []
    stack = []                         # invariant: stack = ancestors not yet recorded, deepest on top
    cur = root
    while cur is not None or len(stack) > 0:
        while cur is not None:         # push the left spine
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        out.append(cur.val)            # its whole left subtree is done
        cur = cur.right
    return out

assert inorder(build_tree([4, 2, 6, 1, 3, 5, 7])) == [1, 2, 3, 4, 5, 6, 7]
assert inorder(build_tree([1, None, 2, 3])) == [1, 3, 2]   # right child that has a left child
assert inorder(None) == []                         # empty tree: both conditions false
```

Trap: the outer loop needs both conditions. With `while stack` alone, the
loop never starts, because the stack begins empty. With `while cur` alone, it
stops at the first leaf's missing right child. On a BST, inorder visits values
in sorted order, which is why this shape solves k-th smallest (LC 230).

### BST bounds — pass the range down

Task: return whether a tree is a valid BST, where every node is strictly
greater than everything in its left subtree and strictly less than everything
in its right subtree.

```python
# shorthand: each node must sit inside the range its ancestors allow; going left lowers the top, going right raises the bottom
def is_valid_bst(node, lo, hi):  # LC 98, call with -inf and inf
    if node is None:
        return True
    if node.val <= lo or node.val >= hi:   # invariant: node satisfies every ancestor's bound
        return False
    return is_valid_bst(node.left, lo, node.val) and is_valid_bst(node.right, node.val, hi)

inf = float('inf')
assert is_valid_bst(build_tree([2, 1, 3]), -inf, inf) is True
assert is_valid_bst(build_tree([5, 1, 6, None, None, 3, 7]), -inf, inf) is False   # 3 < 5, but it's in 5's right subtree
assert is_valid_bst(build_tree([2, 2]), -inf, inf) is False    # duplicate: strict bounds reject it
```

Trap: comparing each node only with its own children accepts the second tree,
because 3 < 6 is fine locally. The bound from 5, two levels up, is what
rejects it. In Java, `Integer.MIN_VALUE` can be a real node value, so use
`long` bounds or nullable `Integer`s.


## 3. Graphs

### Adjacency list — one list per node

Task: given n nodes numbered 0..n-1 and undirected edges `[u, v]`, return
each node's neighbours.

```python
# shorthand: give every node an empty list, then for each edge add each end to the other's list
def build_adj(n, edges):
    adj = []
    for i in range(n):
        adj.append([])                 # not [[]] * n: that's one list shared n times
    for i in range(len(edges)):
        u = edges[i][0]
        v = edges[i][1]
        adj[u].append(v)
        adj[v].append(u)               # undirected: drop this line for a directed graph
    return adj

assert build_adj(3, [[0, 1], [1, 2]]) == [[1], [0, 2], [1]]
assert build_adj(2, []) == [[], []]                # nodes with no edges still get a list
```

Trap: `[[]] * n` creates n references to one list, so every node ends up with
every neighbour. Size the list from n, not from the edges, or a node with no
edges never gets a slot.

### Mark before you recurse — count components

Task: return the number of connected components in an undirected graph.

```python
# shorthand: for each unvisited node, start a DFS that marks everything it reaches; each start is one component
def count_components(n, edges):  # LC 323
    adj = build_adj(n, edges)
    visited = [False] * n              # invariant: visited[v] = v is in a component already counted
    def dfs(u):
        visited[u] = True              # mark on entry, before looking at neighbours
        for i in range(len(adj[u])):
            v = adj[u][i]
            if not visited[v]:
                dfs(v)
    count = 0
    for u in range(n):
        if not visited[u]:
            dfs(u)
            count += 1
    return count

assert count_components(5, [[0, 1], [1, 2], [3, 4]]) == 2
assert count_components(3, []) == 3                # no edges: every node is its own component
assert count_components(3, [[0, 1], [1, 2], [2, 0]]) == 1   # cycle: marking first stops it looping
```

Trap: if you mark `u` after the neighbour loop, a cycle sends the DFS around
it forever. Python's recursion limit is about 1000, so a long path graph
crashes. Switch to an explicit stack, or call `sys.setrecursionlimit`, when n
can be large.

### Grid DFS — bounds, check, mark, spread

Task: given a grid of 1 (land) and 0 (water), count the islands, where land
connects up, down, left, and right.

```python
# shorthand: stop if off the grid or not land, sink the cell, then spread to its four neighbours
def num_islands(grid):  # LC 200, modifies grid
    rows = len(grid)
    cols = len(grid[0])
    def sink(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols:
            return                     # 1. bounds
        if grid[r][c] != 1:
            return                     # 2. water, or land already sunk
        grid[r][c] = 0                 # 3. mark: sinking is the visited set
        sink(r + 1, c)                 # 4. spread
        sink(r - 1, c)
        sink(r, c + 1)
        sink(r, c - 1)
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                sink(r, c)
                count += 1
    return count

assert num_islands([[1, 1, 0],
                    [0, 1, 0],
                    [0, 0, 1]]) == 2
assert num_islands([[1, 0, 1, 0],
                    [1, 0, 0, 1]]) == 3            # non-square: catches swapped rows / cols
assert num_islands([[0]]) == 0                     # no land
```

Trap: the order is the idiom. A check before the bounds test reads
`grid[-1]`, which Python silently wraps to the last row (see "Grid
neighbours" in `docs/array_warmup.md`). Spreading before marking lets a
neighbour spread back into this cell forever. If you can't modify the input,
use a separate `visited` grid.

### BFS shortest path — mark on push

Task: in an unweighted, undirected graph, return the fewest edges from `src`
to `dst`, or -1 if `dst` can't be reached.

```python
# shorthand: start from the source at distance 0; when you push a new neighbour, give it the current distance + 1
def shortest_path(n, edges, src, dst):
    adj = build_adj(n, edges)
    dist = [-1] * n                    # invariant: dist[v] != -1 means v was pushed, with its final distance
    dist[src] = 0
    queue = deque([src])
    while len(queue) > 0:
        u = queue.popleft()
        for i in range(len(adj[u])):
            v = adj[u][i]
            if dist[v] == -1:          # mark on push, not on pop
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist[dst]

assert shortest_path(5, [[0, 1], [1, 2], [0, 3], [3, 2], [2, 4]], 0, 4) == 3
assert shortest_path(3, [[0, 1]], 0, 2) == -1      # unreachable
assert shortest_path(2, [[0, 1]], 0, 0) == 0       # src == dst
```

Trap: marking on pop lets several neighbours push the same node before it
comes out. In the first graph, both 1 and 3 would push 2. BFS gives shortest
paths only because every edge costs 1. Weighted edges need Dijkstra.

### Topological sort (Kahn) — count what you emit

Task: given directed edges `[u, v]` meaning u must come before v, return an
order of all n nodes that respects every edge, or `[]` if there's a cycle.

```python
# shorthand: queue every node with nothing before it; pop one, emit it, remove its out-edges, and queue any node that drops to zero
def topo_sort(n, edges):
    adj = []
    for i in range(n):
        adj.append([])
    indegree = [0] * n                 # invariant: indegree[v] = unemitted nodes that must come before v
    for i in range(len(edges)):
        u = edges[i][0]
        v = edges[i][1]
        adj[u].append(v)               # directed: one direction only
        indegree[v] += 1
    queue = deque()
    for v in range(n):
        if indegree[v] == 0:
            queue.append(v)
    out = []
    while len(queue) > 0:
        u = queue.popleft()
        out.append(u)
        for i in range(len(adj[u])):
            v = adj[u][i]
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)
    if len(out) < n:
        return []                      # cycle: its nodes never reach indegree 0
    return out

assert topo_sort(4, [[0, 1], [0, 2], [1, 3], [2, 3]]) == [0, 1, 2, 3]
assert topo_sort(2, [[0, 1], [1, 0]]) == []        # cycle
assert topo_sort(3, []) == [0, 1, 2]               # no edges: every node starts in the queue
```

Trap: LC 207 and LC 210 give prerequisites as `[a, b]`, meaning b comes
before a, which is the reverse of this task's edges. Read the edge direction
before you write `indegree[...] += 1`. The cycle check is free: nodes in a
cycle wait on each other, so they never get emitted.

### Union-find — link roots, not nodes

Task: nodes are 1..n. Edges arrive one at a time and make a tree plus one
extra edge. Return the first edge that connects two nodes that are already
connected.

```python
# shorthand: find walks up to the root, shortening the path; union links two roots, or reports they were already the same
def find(parent, x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]  # path halving: point x at its grandparent
        x = parent[x]
    return x

def union(parent, a, b):
    ra = find(parent, a)
    rb = find(parent, b)
    if ra == rb:
        return False                   # already connected: this edge closes a cycle
    parent[ra] = rb                    # link the roots, never a and b themselves
    return True

def redundant_edge(edges):  # LC 684
    n = len(edges)
    parent = [0] * (n + 1)             # invariant: parent[x] == x means x is a root
    for i in range(n + 1):
        parent[i] = i
    for i in range(len(edges)):
        if not union(parent, edges[i][0], edges[i][1]):
            return edges[i]
    return []

assert redundant_edge([[1, 2], [1, 3], [2, 3]]) == [2, 3]
assert redundant_edge([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]) == [1, 4]   # cycle closes mid-list
```

Trap: `parent[a] = b` relinks a single node and leaves the rest of a's set
behind. Always link the two roots. Every node has to start as its own parent,
so skipping the init loop makes everything look connected to node 0. This
handles undirected graphs only. For directed cycles, use three colours.

### Three colours — directed cycle check

Task: return whether a directed graph has a cycle.

```python
# shorthand: mark a node in progress on entry and done on exit; reaching an in-progress node means a cycle
def has_cycle(n, edges):
    adj = []
    for i in range(n):
        adj.append([])
    for i in range(len(edges)):
        adj[edges[i][0]].append(edges[i][1])
    state = [0] * n                    # invariant: state[v] == 1 exactly for nodes on the current DFS path
    def dfs(u):
        state[u] = 1
        for i in range(len(adj[u])):
            v = adj[u][i]
            if state[v] == 1:
                return True            # back edge: v is an ancestor on this path
            if state[v] == 0 and dfs(v):
                return True
        state[u] = 2                   # every path out of u is finished and cycle-free
        return False
    for u in range(n):
        if state[u] == 0 and dfs(u):
            return True
    return False

assert has_cycle(3, [[0, 1], [1, 2], [2, 0]]) is True
assert has_cycle(3, [[0, 1], [0, 2], [1, 2]]) is False   # diamond: 2 is reached twice, no cycle
```

Trap: a plain `visited` boolean reports the diamond as a cycle, because
reaching 2 a second time looks the same as looping back. Only a node that is
still on the current path proves a cycle. In undirected graphs every edge
leads back to its parent, so use union-find there, or skip the parent.


## 4. Strings and numbers

### Char to index — 26 slots

Task: return whether two lowercase strings are anagrams, meaning they use the
same letters the same number of times.

```python
# shorthand: add one per letter of s, subtract one per letter of t; anagrams leave every slot at zero
def is_anagram(s, t):  # LC 242
    if len(s) != len(t):
        return False
    freq = [0] * 26                    # invariant: freq[k] = (count of letter k in s[0:i]) - (in t[0:i])
    for i in range(len(s)):
        freq[ord(s[i]) - ord('a')] += 1
        freq[ord(t[i]) - ord('a')] -= 1
    for k in range(26):
        if freq[k] != 0:
            return False
    return True

assert is_anagram("anagram", "nagaram") is True
assert is_anagram("ab", "a") is False              # different lengths
assert is_anagram("", "") is True                  # empty strings
```

Trap: `ord(c)` without `- ord('a')` indexes 97..122 and overruns 26 slots. In
Java, it's `c - 'a'` directly. The array only works for a fixed alphabet; for
arbitrary characters, use a map.

### Build, then join

Task: run-length encode a string: `"aaabcc"` becomes `"a3b1c2"`.

```python
# shorthand: append each piece to a list, then join the list once at the end
def compress(s):
    n = len(s)
    parts = []
    i = 0
    while i < n:
        j = i                          # invariant: s[i:j] all equal s[i]
        while j < n and s[j] == s[i]:
            j += 1
        parts.append(s[i])
        parts.append(str(j - i))
        i = j
    return "".join(parts)

assert compress("aaabcc") == "a3b1c2"
assert compress("") == ""                          # empty string: join of nothing
```

Trap: `out += piece` in a loop copies the whole string every time, which is
O(n^2). CPython sometimes optimizes it in place, but Java never does. Use a
`StringBuilder` there. The inner loop is run grouping from
`docs/array_warmup.md`.

### Multi-digit parse — num * 10 + digit

Task: decode a run-length string where each letter is followed by its count,
which can be more than one digit: `"a3b12"` becomes three `a`s, then twelve
`b`s.

```python
# shorthand: build the count one digit at a time; when a new letter arrives, emit the previous letter count times, and emit the last one after the loop
def decode_rle(s):
    n = len(s)
    parts = []
    letter = ''
    num = 0                            # invariant: num = the digits read since letter, as one number
    for i in range(n):
        c = s[i]
        if c >= '0' and c <= '9':
            num = num * 10 + (ord(c) - ord('0'))   # shift left one decimal place, add the new digit
        else:
            for k in range(num):       # flush the previous run
                parts.append(letter)
            letter = c
            num = 0                    # reset: the next count starts fresh
    for k in range(num):               # flush the last run: no letter follows it
        parts.append(letter)
    return "".join(parts)

assert decode_rle("a3b2") == "aaabb"
assert decode_rle("a3b12") == "aaa" + "bbbbbbbbbbbb"   # multi-digit count: 12, not 1 then 2
assert decode_rle("x10") == "xxxxxxxxxx"               # zero digit inside a count
assert decode_rle("") == ""                            # empty string: num stays 0, nothing flushed
```

Trap: the last run has no letter after it to trigger its flush, so without
the loop after the main loop, `"a3b2"` decodes to `"aaa"`. Reset `num` at every
letter, or the counts run together. The first letter flushes `num = 0`
copies, so it needs no special case. In Java, `num * 10 + (c - '0')`
overflows `int` past 10 digits. LC 8 clamps it, and LC 394 and LC 224 parse
numbers with this same line.

### Digit extraction — % 10, then // 10

Task: return the sum of a non-negative integer's digits.

```python
# shorthand: peel off the last digit with % 10, drop it with // 10, until nothing is left
def digit_sum(x):                      # x >= 0
    total = 0
    while x > 0:                       # invariant: total = sum of the digits already dropped from x
        total += x % 10
        x //= 10
    return total

assert digit_sum(1234) == 10
assert digit_sum(0) == 0                           # zero: no digits peeled
```

Trap: negatives behave differently. Python gives `-7 // 10 == -1` and
`-7 % 10 == 3`, while Java gives `0` and `-7`. Take `abs` first and handle
the sign separately (see `docs/modulo.md`). "Count the digits" with this loop
returns 0 for `x = 0`, but 0 has one digit.

### Ceil division — add b - 1

Task: return a / b rounded up, for `a >= 0` and `b > 0`.

```python
# shorthand: add b - 1 before dividing, so any remainder pushes the result up by one
def ceil_div(a, b):
    return (a + b - 1) // b

assert ceil_div(7, 3) == 3
assert ceil_div(6, 3) == 2                         # exact: b - 1 isn't enough to push it over
assert ceil_div(0, 3) == 0                         # nothing to divide
```

Trap: `math.ceil(a / b)` goes through a float and is wrong once values pass
2^53. In Java, `a + b - 1` can overflow an `int`, so use `long`, or write
`(a - 1) / b + 1` for `a > 0`. This is the hours count in Koko (LC 875).

### 2-D init — one list per row

Task: build a `rows x cols` grid of zeros where every row can be changed on
its own.

```python
# shorthand: build each row inside the loop, so no two rows are the same list
def make_grid(rows, cols):
    grid = []
    for r in range(rows):
        grid.append([0] * cols)        # [0] * cols is fine: the ints don't alias, the rows would
    return grid

grid = make_grid(2, 3)
grid[0][0] = 9
assert grid == [[9, 0, 0], [0, 0, 0]]
alias = [[0] * 3] * 2
alias[0][0] = 9
assert alias == [[9, 0, 0], [9, 0, 0]]             # the trap: both rows are one list
```

Trap: `[[0] * cols] * rows` repeats a reference to one row, so writing one
cell writes the whole column. Keep the order fixed: the outer list has `rows`
entries and you index `grid[r][c]`. Java's `new int[rows][cols]` doesn't have
this problem.

### DP table — n+1 slots, row 0 is empty

Task: return the length of the longest common subsequence of two strings.

```python
# shorthand: dp[i][j] answers the prefixes a[0:i] and b[0:j]; row 0 and column 0 are the empty prefix
def lcs(a, b):  # LC 1143
    n = len(a)
    m = len(b)
    dp = []
    for i in range(n + 1):
        dp.append([0] * (m + 1))       # invariant: dp[i][j] = LCS of a[0:i] and b[0:j]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:   # dp index i is string index i - 1
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]

assert lcs("abcde", "ace") == 3
assert lcs("abc", "") == 0                         # empty string: only the sentinel row and column
```

Trap: the table is shifted one slot from the strings, so comparing `a[i]`
with `b[j]` is off by one and reads past the end on the last row. This is
"prefix with sentinel" in 2-D. Row 0 and column 0 already hold the base case,
so the loops start at 1 with no special case.
