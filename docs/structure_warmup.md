# Structure warmup

This file has one short, runnable example for each idiom you need once the
input stops being a flat array: linked lists, trees, graphs, and the string
and number tricks that come up alongside them. Each block ends with an
`assert`, so you can paste it into `main.py` and run it.

Assumes you know: section 0 of `docs/array_warmup.md` (several idioms here
reuse its loop shapes), and recursion (`docs/concepts/recursion.md`).
Not covered: segment trees. Dijkstra, tries, and heaps are in
`docs/search_warmup.md`.

How to use it: read the task and the "Spot it by" line, cover the code, and
write it from memory. Then run the asserts, step through the trace, and say
the invariant out loud. If you can't explain why the trap breaks it, you
memorized the code without understanding it. The Time / Space block says
where each bound comes from, which is the sentence an interviewer wants to
hear.

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

Task: return the number of nodes in a singly linked list.

    input    head    the first node, or None for an empty list
    output   count   how many nodes there are

Example: `1 -> 2 -> 3` has length 3. An empty list (`None`) has length 0.

Spot it by: anything that has to look at every node once: length, sum,
search, or printing. A linked list has no indices, so the only way through is
following `.next` until it runs out.

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

Trace of `length(1 -> 2 -> 3)`:

    cur    cur is not None?  count after  cur after
    1      yes               1            2
    2      yes               2            3
    3      yes               3            None
    None   no: stop                                  return 3

The last node is counted because the test is on `cur`, not `cur.next`.

Trap: `while cur.next is not None` stops on the last node without counting
it, and it crashes on an empty list. Use that form only when you need to stop
at the last node, for example to append after it. Walk with `cur`, never with
`head`, or you lose the start of the list.

    Time   O(n)  one step per node
    Space  O(1)  count and cur

### Dummy head — return dummy.next

Task: remove every node whose value is `val`, including the head if it
matches, and return the head of what's left.

    input    head   the first node of the list
             val    the value to remove
    output   head   the new first node; None if every node was removed

Example: `1 -> 2 -> 1 -> 3` with `val = 1` becomes `2 -> 3`. The head itself
was removed, so the answer starts at a different node.

Spot it by: the head itself might be deleted or replaced, or you're building
a new list from nothing. A fake node in front gives every real node a
predecessor, so "delete the head" is no longer a special case.

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

Trace of `remove_value(1 -> 2 -> 1 -> 3, 1)`. `D` is the dummy:

    prev  prev.next  match?  action            list from D
    D     1          yes     unlink, prev stays  D -> 2 -> 1 -> 3
    D     2          no      prev = 2            D -> 2 -> 1 -> 3
    2     1          yes     unlink, prev stays  D -> 2 -> 3
    2     3          no      prev = 3            D -> 2 -> 3
    3     None       -       stop                return dummy.next = 2

Row 1 deletes the real head, and the code doesn't notice. It's just
`prev.next` like any other node.

Trap: returning `head` returns a deleted node whenever the head matched. The
dummy exists so the head is never a special case. Advancing `prev` after a
delete skips the next node, which breaks on two matches in a row. It's the
same asymmetry as Dutch flag's `hi` swap: after a delete, the node in front of
you hasn't been checked.

    Time   O(n)  each step either unlinks a node or moves prev forward, n steps in total
    Space  O(1)  dummy and prev; nodes are relinked, not copied

### Reverse in place — save next first

Task: reverse a singly linked list by relinking its nodes, and return the new
head.

    input    head   the first node, or None
    output   head   the old last node, now first; None for an empty list

Example: `1 -> 2 -> 3` becomes `3 -> 2 -> 1`.

Spot it by: "reverse" a list or part of one (LC 92, LC 25), or a palindrome
check on a list (LC 234), where you reverse the second half and compare. Any
time an arrow has to point the other way, use this.

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

Trace of `reverse_list(1 -> 2 -> 3)`:

    cur  nxt saved  after cur.next = prev   prev after  cur after
    1    2          1 -> None               1           2
    2    3          2 -> 1 -> None          2           3
    3    None       3 -> 2 -> 1 -> None     3           None     return prev = 3

At every row, `prev` heads the reversed part and `nxt` holds the rest. Without
`nxt`, the rest of the list would be unreachable after the rewire.

Trap: without `nxt`, `cur.next = prev` cuts off the rest of the list. This is
swap with tmp for pointers. Return `prev`, not `cur`, because `cur` is `None`
when the loop ends. The four lines go in a fixed order: save, rewire, step
prev, step cur.

    Time   O(n)  each node is rewired once
    Space  O(1)  three pointers. The recursive version is O(n) stack

### Fast / slow — the middle

Task: return the middle node of a list. For an even length, return the second
of the two middles.

    input    head   the first node; the list has at least one node
    output   node   the middle node

Example: `1 -> 2 -> 3` returns the node 2. `1 -> 2 -> 3 -> 4` returns the
node 3, the second middle.

Spot it by: you need a position defined relative to the list's length
(the middle, a half) or a cycle check, and you don't know the length. A
walker that moves at double speed reaches the end exactly when the other is
halfway.

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

Trace of both lengths:

    list              step   slow  fast   why the loop stops
    1 -> 2 -> 3       start  1     1
                      1      2     3      fast.next is None: return 2
    1 -> 2 -> 3 -> 4  start  1     1
                      1      2     3
                      2      3     None   fast is None: return 3

Odd lengths stop on `fast.next`, even lengths on `fast`. That's why both
checks are needed.

Trap: `fast is not None` has to come first in the `and`, or an even-length
list reads `None.next`. To split a list in half (LC 148, LC 234), you want the
first middle, so start with `fast = head.next`. The same loop detects a cycle
(LC 141): if `slow == fast` after a step, there is one.

    Time   O(n)  n/2 iterations; fast covers the list once
    Space  O(1)  two pointers. Copying into an array to index the middle is O(n)

### Kth from end — open the gap first

Task: return the k-th node from the end of a list, where `1 <= k <= length`.
The last node is 1st from the end.

    input    head   the first node
             k      position counted from the end, 1-indexed
    output   node   the k-th node from the end

Example: in `1 -> 2 -> 3 -> 4 -> 5`, the 2nd from the end is the node 4.

Spot it by: "from the end" in a singly linked list. You can't walk
backwards, and counting the length first takes two passes. Two pointers k
apart reach the right spot in one.

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

Trace of `kth_from_end(1 -> 2 -> 3 -> 4 -> 5, 2)`:

    phase        slow  fast
    gap of k=2   -     3       fast moved 1 -> 2 -> 3
    start both   1     3
    step         2     4
    step         3     5
    step         4     None    fast fell off: return 4

Trap: when fast falls off the end, slow is exactly k nodes from it. To delete
the k-th from the end (LC 19), you need the node before it, so start both
walkers at a dummy. Then `k == length` deletes the head without a special
case.

    Time   O(n)  fast walks the whole list once; slow walks n - k of it
    Space  O(1)  two pointers

### Merge two sorted — attach the leftover

Task: merge two sorted linked lists into one sorted list by relinking their
nodes (no new nodes), and return its head.

    input    a, b   heads of two lists, each sorted ascending; either may be None
    output   head   the merged list, sorted ascending

Example: `1 -> 4` and `2 -> 3 -> 5` merge into `1 -> 2 -> 3 -> 4 -> 5`.

Spot it by: two sorted sequences that have to become one, as lists. It's the
merge step of merge sort on lists (LC 148), and the building block of merging
k lists (LC 23).

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

Trace of `merge_lists(1 -> 4, 2 -> 3 -> 5)`:

    a     b     take  merged so far
    1     2     1     1
    4     2     2     1 -> 2
    4     3     3     1 -> 2 -> 3
    4     5     4     1 -> 2 -> 3 -> 4
    None  5     -     a ran out: tail.next = b    1 -> 2 -> 3 -> 4 -> 5

The last row is one assignment. If `b` had a thousand nodes left, it would
still be one.

Trap: forget `tail = tail.next` and every node overwrites the same slot.
Compare this with merging arrays, where you have to copy the leftovers one at
a time. Here a single assignment attaches the whole remaining chain.

    Time   O(n + m)  each loop iteration attaches one node; the leftover is O(1)
    Space  O(1)      dummy and tail; the existing nodes are relinked


## 2. Trees

### Base case first — None returns the identity

Task: return the maximum depth of a binary tree: the number of nodes on the
longest path from the root down to a leaf.

    input    node    the root, or None for an empty tree
    output   depth   0 for an empty tree; 1 for a single node

Example: `[3, 9, 20, None, None, 15, 7]` is 3 with children 9 and 20, and 20
has children 15 and 7. The longest path, 3 -> 20 -> 15, has 3 nodes.

Spot it by: a value for the whole tree that you can combine from the same
value for each subtree: depth, size, sum, "is balanced," "are all nodes X."
Write it as recursion where the empty tree returns the identity.

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

Trace of `max_depth([3, 9, 20, None, None, 15, 7])`. Indentation is call
depth, and calls on `None` return 0:

    max_depth(3)
      max_depth(9)       left 0, right 0      returns 1 + 0 = 1
      max_depth(20)
        max_depth(15)    left 0, right 0      returns 1
        max_depth(7)     left 0, right 0      returns 1
                         left 1, right 1      returns 1 + 1 = 2
                         left 1, right 2      returns 1 + 2 = 3

No call checks whether a child exists. The `None` calls answer 0, and the
`max` takes care of the rest.

Trap: testing `node.left is None` and `node.right is None` before each call
turns one base case into four branches. Let the call on `None` return the
identity instead: 0 for a count or depth, `True` for "all nodes satisfy,"
`float('-inf')` for a max.

    Time   O(n)  one call per node, plus one per missing child (at most n + 1 of those)
    Space  O(h)  h = tree height, the recursion depth: about log n when balanced, n when
                 every node has one child

### Pass down — state rides in the arguments

Task: return whether some root-to-leaf path has values that sum to `target`.

    input    node        the root
             remaining   the target sum, passed in at the root
    output   found       True if at least one root-to-leaf path sums to target

Example: in `[5, 4, 8, 11, None, 13, 4, 7, 2]`, the path 5 -> 4 -> 11 -> 2
sums to 22, so `has_path_sum(tree, 22)` is True.

Spot it by: each node's answer depends on its ancestors, the path from the
root down to it: a running sum, the max so far, the depth. That information
flows down, so it goes in the arguments.

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

Trace of `has_path_sum(tree, 22)`. The tree:

            5
          /   \
         4     8
        /     / \
      11     13  4
     /  \
    7    2

    node  remaining after subtracting  leaf?  result
    5     22 - 5 = 17                  no     try left
    4     17 - 4 = 13                  no     try left
    11    13 - 11 = 2                  no     try left
    7     2 - 7 = -5                   yes    False: try 11's right
    2     2 - 2 = 0                    yes    True: stop

The `or` short-circuits, so the whole right subtree under 8 is never
visited.

Trap: test for the leaf explicitly. If you return `remaining == 0` at `None`
instead, then `[1, 2]` with target 1 returns `True` through the missing right
child, which is a path that ends at a node that isn't a leaf. Each call gets
its own `remaining`, so there's nothing to undo on the way back up.

    Time   O(n)  each node is visited at most once
    Space  O(h)  recursion depth; remaining is one int per frame

### Return up — return one side, record both

Task: return the diameter of a binary tree: the number of edges on the
longest path between any two nodes. The path doesn't have to pass through
the root.

    input    root       the root of the tree
    output   diameter   edges on the longest path; 0 for a single node

Example: in `[1, 2, 3, 4, 5]`, the path 4 -> 2 -> 1 -> 3 has 3 edges, the
longest there is.

Spot it by: the answer is a path that can bend at any node, but the parent
can only extend a path that goes straight down. Each node therefore computes
two things: what it returns (one side) and what it records (both sides).
Max path sum (LC 124) has the same shape.

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

Trace of the second assert. The tree:

            1
           /
          2
         / \
        3   4
       /   /
      5   6

    node  left  right  record left + right  returns 1 + max  best
    5     0     0      0                    1                0
    3     1     0      1                    2                1
    6     0     0      0                    1                1
    4     1     0      1                    2                1
    2     2     2      4                    3                4     bends at 2: 5-3-2-4-6
    1     3     0      3                    4                4

The root records only 3. The best path bends at 2, below the root, which is
why every node records a candidate.

Trap: what you return and what you record are different values. Returning
`left + right` to the parent is wrong, because a path that already bends at
this node can't be extended upward. The answer counts edges, and the height
counts nodes, which is why `left + right` needs no `- 1`. LC 124 is the same
shape with sums and a `max(0, ...)` that drops negative branches.

    Time   O(n)  one call per node. Computing height from scratch at every node is O(n²)
    Space  O(h)  recursion depth

### BFS by level — freeze the size

Task: return the tree's values level by level, left to right, as a list of
lists.

    input    root   the root, or None
    output   out    out[d] = values at depth d, left to right

Example: `[3, 9, 20, None, None, 15, 7]` returns `[[3], [9, 20], [15, 7]]`.

Spot it by: "level by level," "each depth," "rightmost node per level"
(LC 199), "minimum depth," or anything that counts distance from the root
in steps. A queue visits nodes in order of depth.

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

Trace of `level_order([3, 9, 20, None, None, 15, 7])`:

    queue at top  size  pops       pushes      level     queue after
    [3]           1     3          9, 20       [3]       [9, 20]
    [9, 20]       2     9, 20      15, 7       [9, 20]   [15, 7]
    [15, 7]       2     15, 7      -           [15, 7]   []

During row 2 the queue briefly holds 20, 15, 7. `size` was frozen at 2, so
15 and 7 wait for the next row.

Trap: in Java, `for (int i = 0; i < queue.size(); i++)` re-reads the size on
every iteration, so the children you push join the current level. Python's
`range(len(queue))` happens to evaluate once, which hides the bug. Use
`deque.popleft()`, not `list.pop(0)`, which is O(n). In Java, use
`ArrayDeque` with `offer` and `poll`.

    Time   O(n)  each node is pushed once and popped once
    Space  O(w)  w = the widest level, which the queue holds at once: up to about n/2
                 for a full tree's bottom level, so O(n) in the worst case

### Iterative inorder — left spine, pop, go right

Task: return the inorder traversal of a binary tree (left subtree, then the
node, then the right subtree) without recursion.

    input    root   the root, or None
    output   out    values in inorder

Example: `[4, 2, 6, 1, 3, 5, 7]` is a BST, so its inorder is sorted:
`[1, 2, 3, 4, 5, 6, 7]`.

Spot it by: you need nodes in sorted order from a BST (k-th smallest, LC 230;
a BST iterator, LC 173), or you must avoid recursion because the tree can be
too deep for the call stack.

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

Trace of `inorder([1, None, 2, 3])`: 1 has right child 2, and 2 has left
child 3.

    cur at top  push left spine   stack after push  pop  out        cur = popped.right
    1           1                 [1]               1    [1]        2
    2           2, 3              [2, 3]            3    [1, 3]     None
    None        -                 [2]               2    [1, 3, 2]  None
    None        -                 []                -    stop: cur is None and stack is empty

Row 3 starts with `cur = None` but a non-empty stack, which is why the outer
loop needs both conditions.

Trap: the outer loop needs both conditions. With `while stack` alone, the
loop never starts, because the stack begins empty. With `while cur` alone, it
stops at the first leaf's missing right child. On a BST, inorder visits values
in sorted order, which is why this shape solves k-th smallest (LC 230).

    Time   O(n)  each node is pushed once and popped once
    Space  O(h)  the stack holds one root-to-node path at most

### BST bounds — pass the range down

Task: return whether a binary tree is a valid BST, where every node is
strictly greater than everything in its left subtree and strictly less than
everything in its right subtree.

    input    node     the root
             lo, hi   the open range the node must fall in; call with -inf and inf
    output   valid    True if the whole tree obeys the BST rule

Example: `[2, 1, 3]` is valid. `[5, 1, 6, None, None, 3, 7]` is not: 3 sits
in 5's right subtree but is less than 5.

Spot it by: a rule that compares a node with all of its ancestors, not just
its parent. Every ancestor narrows the allowed range, so the range is what
you pass down.

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

Trace of the second assert:

    node  range (lo, hi)  inside?  children get
    5     (-inf, inf)     yes      left (-inf, 5), right (5, inf)
    1     (-inf, 5)       yes      leaf
    6     (5, inf)        yes      left (5, 6), right (6, inf)
    3     (5, 6)          no: 3 <= 5   return False

3's parent is 6, and 3 < 6 is fine. The lower bound 5 came from the
grandparent, through the range.

Trap: comparing each node only with its own children accepts the second tree,
because 3 < 6 is fine locally. The bound from 5, two levels up, is what
rejects it. In Java, `Integer.MIN_VALUE` can be a real node value, so use
`long` bounds or nullable `Integer`s.

    Time   O(n)  each node is checked once; the and stops at the first failure
    Space  O(h)  recursion depth


## 3. Graphs

### Adjacency list — one list per node

Task: given n nodes numbered 0..n-1 and a list of undirected edges `[u, v]`,
build each node's list of neighbours.

    input    n       number of nodes
             edges   [u, v] pairs; each connects u and v both ways
    output   adj     adj[u] = list of u's neighbours

Example: `build_adj(3, [[0, 1], [1, 2]])` returns `[[1], [0, 2], [1]]`. Node
1 sits in the middle, so it has two neighbours.

Spot it by: the input is an edge list, and the algorithm needs "the
neighbours of u" again and again (DFS, BFS, topological sort). Scanning the
whole edge list each time is O(e) per lookup, so you index the edges once.

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

Trace of `build_adj(3, [[0, 1], [1, 2]])`:

    step         adj after
    init         [[], [], []]
    edge [0, 1]  [[1], [0], []]        1 added to 0's list, 0 to 1's
    edge [1, 2]  [[1], [0, 2], [1]]

Each undirected edge shows up twice, once from each end.

Trap: `[[]] * n` creates n references to one list, so every node ends up with
every neighbour. Size the list from n, not from the edges, or a node with no
edges never gets a slot.

    Time   O(n + e)  n empty lists, then O(1) per edge
    Space  O(n + e)  n lists holding 2e entries in total

### Mark before you recurse — count components

Task: return the number of connected components in an undirected graph: the
groups of nodes where every node can reach every other.

    input    n       number of nodes, 0..n-1
             edges   undirected [u, v] pairs
    output   count   number of connected components

Example: 5 nodes with edges `0-1, 1-2, 3-4` form 2 components, `{0, 1, 2}`
and `{3, 4}`.

Spot it by: "how many groups," "connected," "provinces" (LC 547), or "is
everything reachable." Every DFS started from a node no earlier DFS reached
is a new group.

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

Trace of `count_components(5, [[0, 1], [1, 2], [3, 4]])`. Here
`adj = [[1], [0, 2], [1], [4], [3]]`:

    outer u  visited?  DFS visits (marks on entry)       count
    0        no        0 -> 1 -> 2  (1 sees 0: marked)   1
    1        yes       -                                 1
    2        yes       -                                 1
    3        no        3 -> 4  (4 sees 3: marked)        2
    4        yes       -                                 2

The "sees 0: marked" step is the cycle guard. In the triangle graph, 2 sees 0
and stops there instead of going around again.

Trap: if you mark `u` after the neighbour loop, a cycle sends the DFS around
it forever. Python's recursion limit is about 1000, so a long path graph
crashes. Switch to an explicit stack, or call `sys.setrecursionlimit`, when n
can be large.

    Time   O(n + e)  each node is marked once, and each of the 2e adjacency entries is
                     looked at once
    Space  O(n + e)  adj, plus visited and a recursion that can be n deep

### Grid DFS — bounds, check, mark, spread

Task: given a grid of 1 (land) and 0 (water), count the islands. Land cells
connect up, down, left, and right, not diagonally.

    input    grid    rows x cols of 0 and 1; it gets modified
    output   count   number of islands

Example: in
`[[1, 1, 0], [0, 1, 0], [0, 0, 1]]`, the top-left three cells form one
island and the bottom-right cell is another, so the answer is 2.

Spot it by: a 2-D grid where cells "connect" to their neighbours: islands,
flood fill (LC 733), enclosed regions (LC 130), or the area of the largest
island (LC 695). It's a graph whose nodes are the cells and whose edges are
the four directions.

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

Trace of the first assert. Each `sink` tries down, up, right, left:

    call         result
    sink(0, 0)   land: sink it, spread
      (1, 0)     water: return
      (-1, 0)    off the grid: return
      (0, 1)     land: sink it, spread
        (1, 1)   land: sink it; its down, up, right, left are water or already sunk
        (-1, 1)  off the grid
        (0, 2)   water
        (0, 0)   already sunk: return       count = 1
    sink(2, 2)   land: sink it; every neighbour is off the grid or water
                                            count = 2

Grid after the first island and after the second:

    0 0 0      0 0 0
    0 0 0      0 0 0
    0 0 1      0 0 0

After the first sink, the scan passes (0, 1) and (1, 1) without stopping,
because they're already 0. That's how one island is counted once.

Trap: the order is the idiom. A check before the bounds test reads
`grid[-1]`, which Python silently wraps to the last row (see "Grid
neighbours" in `docs/array_warmup.md`). Spreading before marking lets a
neighbour spread back into this cell forever. If you can't modify the input,
use a separate `visited` grid.

    Time   O(rows · cols)  each cell is sunk at most once, and each sunk cell makes 4 calls
                           that return in O(1)
    Space  O(rows · cols)  the recursion depth when the whole grid is one snaking island

### BFS shortest path — mark on push

Task: in an unweighted, undirected graph, return the fewest edges on a path
from `src` to `dst`, or -1 if `dst` can't be reached.

    input    n          number of nodes, 0..n-1
             edges      undirected [u, v] pairs, all the same cost
             src, dst   start and goal
    output   steps      fewest edges from src to dst; -1 if unreachable

Example: with edges `0-1, 1-2, 0-3, 3-2, 2-4`, the shortest path from 0 to 4
is 0 -> 1 -> 2 -> 4, which is 3 edges.

Spot it by: "fewest steps," "minimum moves," or "shortest path" where every
move costs the same: word ladder (LC 127), a maze, knight moves. BFS reaches
nodes in order of distance, so the first time it reaches a node is the
shortest way there.

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

Trace of the first assert. Here
`adj = [[1, 3], [0, 2], [1, 3, 4], [0, 2], [2]]`:

    pop  neighbours  newly pushed (dist)   queue after   dist
    0    1, 3        1 (1), 3 (1)          [1, 3]        [0, 1, -1, 1, -1]
    1    0, 2        2 (2)                 [3, 2]        [0, 1, 2, 1, -1]
    3    0, 2        - (2 already pushed)  [2]           [0, 1, 2, 1, -1]
    2    1, 3, 4     4 (3)                 [4]           [0, 1, 2, 1, 3]
    4    2           -                     []            return dist[4] = 3

Row 3 is mark-on-push at work. 3 also reaches 2, but `dist[2]` is already
set, so 2 is not queued twice.

Trap: marking on pop lets several neighbours push the same node before it
comes out. In the first graph, both 1 and 3 would push 2. BFS gives shortest
paths only because every edge costs 1. Weighted edges need Dijkstra.

    Time   O(n + e)  each node is pushed and popped once; each adjacency entry is read once
    Space  O(n + e)  adj, dist, and a queue of up to n nodes

### Topological sort (Kahn) — count what you emit

Task: given directed edges `[u, v]` meaning u must come before v, return an
order of all n nodes that respects every edge, or `[]` if there's a cycle
and no such order exists.

    input    n       number of nodes, 0..n-1
             edges   directed [u, v] pairs: u before v
    output   order   every node once, each after all of its prerequisites; [] on a cycle

Example: edges `0->1, 0->2, 1->3, 2->3` give `[0, 1, 2, 3]`. 0 has no
prerequisites, and 3 needs both 1 and 2.

Spot it by: "prerequisites," "dependencies," "build order," "course
schedule" (LC 207, LC 210), or "can all of these be finished." You need an
order that respects arrows, and a cycle means it's impossible.

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

Trace of the first assert. Starting indegrees are `[0, 1, 1, 2]`, so the
queue starts as `[0]`:

    pop  out           indegree changes         queue after
    0    [0]           1: 1 -> 0, 2: 1 -> 0     [1, 2]
    1    [0, 1]        3: 2 -> 1                [2]
    2    [0, 1, 2]     3: 1 -> 0                [3]
    3    [0, 1, 2, 3]  -                        []        4 emitted == n: no cycle

For the cycle `0->1, 1->0`, both start at indegree 1, so the queue starts
empty. Nothing is emitted, 0 < 2, and the result is `[]`.

Trap: LC 207 and LC 210 give prerequisites as `[a, b]`, meaning b comes
before a, which is the reverse of this task's edges. Read the edge direction
before you write `indegree[...] += 1`. The cycle check is free: nodes in a
cycle wait on each other, so they never get emitted.

    Time   O(n + e)  each node is queued once, and each edge decrements one indegree once
    Space  O(n + e)  adj, indegree, and the queue

### Union-find — link roots, not nodes

Task: nodes are 1..n. The edges, in order, form a tree plus one extra edge.
Return the first edge that connects two nodes that are already connected.

    input    edges   [u, v] pairs over nodes 1..n; n = len(edges)
    output   edge    the first edge whose two ends were already connected

Example: `[[1, 2], [1, 3], [2, 3]]`. After `1-2` and `1-3`, nodes 2 and 3 are
already connected through 1, so `[2, 3]` is redundant.

Spot it by: edges arrive one at a time, and you keep asking "are these two
already connected?" Redundant connection, accounts merge (LC 721), number of
provinces, and Kruskal's MST all fit. Running a DFS per edge would be O(n)
each; union-find is close to O(1).

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

Trace of the second assert. `parent` is shown for nodes 1..5:

    edge    find(a)  find(b)  same?  action          parent[1..5] after
    -       -        -        -      init            [1, 2, 3, 4, 5]
    [1, 2]  1        2        no     parent[1] = 2   [2, 2, 3, 4, 5]
    [2, 3]  2        3        no     parent[2] = 3   [2, 3, 3, 4, 5]
    [3, 4]  3        4        no     parent[3] = 4   [2, 3, 4, 4, 5]
    [1, 4]  4        4        yes    return [1, 4]

`find(1)` in the last row walks 1 -> 2 -> 3 -> 4. Path halving rewires along
the way, so afterwards `parent[1] = 3` and `parent[3] = 4`, and the next
`find(1)` takes two hops instead of three.

Trap: `parent[a] = b` relinks a single node and leaves the rest of a's set
behind. Always link the two roots. Every node has to start as its own parent,
so skipping the init loop makes everything look connected to node 0. This
handles undirected graphs only. For directed cycles, use three colours.

    Time   O(e log n)  path halving alone gives O(log n) amortized per find. Adding union by
                       size or rank brings it to O(α(n)), which is under 5 for any real n
    Space  O(n)        the parent array

### Three colours — directed cycle check

Task: return whether a directed graph contains a cycle.

    input    n       number of nodes, 0..n-1
             edges   directed [u, v] pairs
    output   cycle   True if following the arrows can bring you back to a node

Example: `0->1, 1->2, 2->0` is a cycle. The diamond `0->1, 0->2, 1->2` is
not, even though 2 can be reached two ways.

Spot it by: a directed graph and the question "is there a cycle," "is there
a deadlock," or "can this order be completed" when you're already doing a
DFS. Kahn's algorithm answers the same question with BFS.

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

Trace of both asserts. `state` is shown for nodes 0, 1, 2:

    graph      event                         state
    diamond    enter 0                       [1, 0, 0]
               enter 1 (from 0)              [1, 1, 0]
               enter 2 (from 1)              [1, 1, 1]
               finish 2: no edges out        [1, 1, 2]
               finish 1                      [1, 2, 2]
               0 -> 2: state 2, skip         [1, 2, 2]     done, not on the path
               finish 0: no cycle            [2, 2, 2]
    triangle   enter 0, 1, 2                 [1, 1, 1]
               2 -> 0: state 1               return True   0 is still on the path

The diamond's second visit to 2 finds state 2. The triangle's edge back to 0
finds state 1. A plain boolean would see both as "visited."

Trap: a plain `visited` boolean reports the diamond as a cycle, because
reaching 2 a second time looks the same as looping back. Only a node that is
still on the current path proves a cycle. In undirected graphs every edge
leads back to its parent, so use union-find there, or skip the parent.

    Time   O(n + e)  each node is entered once (state 0 -> 1), and each edge is read once
    Space  O(n + e)  adj, state, and a recursion up to n deep


## 4. Strings and numbers

### Char to index — 26 slots

Task: return whether two lowercase strings are anagrams, meaning they use the
same letters the same number of times.

    input    s, t      strings of lowercase letters a..z
    output   anagram   True if t is a rearrangement of s

Example: "anagram" and "nagaram" are anagrams (three a's, one each of n, g,
r, m). "rat" and "car" are not.

Spot it by: counting letters when the alphabet is small and fixed: anagrams,
"first unique character" (LC 387), ransom note (LC 383), or a sliding window
with letter counts. An `int[26]` is faster and simpler than a map.

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

Trace of `is_anagram("anagram", "nagaram")`. Only nonzero slots are shown:

    i  s[i]  t[i]  nonzero freq after
    0  a     n     a: 1, n: -1
    1  n     a     {}
    2  a     g     a: 1, g: -1
    3  g     a     {}
    4  r     r     {}
    5  a     a     {}
    6  m     m     {}            every slot 0: True

`ord('g') - ord('a')` is 6, so g lives in `freq[6]`.

Trap: `ord(c)` without `- ord('a')` indexes 97..122 and overruns 26 slots. In
Java, it's `c - 'a'` directly. The array only works for a fixed alphabet; for
arbitrary characters, use a map.

    Time   O(n)  one pass over both strings, then a fixed 26-slot check.
                 Sorting both and comparing is O(n log n)
    Space  O(1)  26 counters no matter how long the strings are

### Build, then join

Task: run-length encode a string: write each run of equal characters as the
character followed by the run's length.

    input    s     any string
    output   enc   each run written as char + count; "" for an empty string

Example: `"aaabcc"` becomes `"a3b1c2"`.

Spot it by: you build an output string piece by piece in a loop: encoding,
formatting, serializing a tree (LC 297), or reversing words. Collect the
pieces in a list, then join them once.

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

Trace of `compress("aaabcc")`:

    i  j after inner loop  run    parts after
    0  3                   "aaa"  ["a", "3"]
    3  4                   "b"    ["a", "3", "b", "1"]
    4  6                   "cc"   ["a", "3", "b", "1", "c", "2"]
    6  -                   stop   join -> "a3b1c2"

The string is built once, at the end, no matter how many pieces there are.

Trap: `out += piece` in a loop copies the whole string every time, which is
O(n^2). CPython sometimes optimizes it in place, but Java never does. Use a
`StringBuilder` there. The inner loop is run grouping from
`docs/array_warmup.md`.

    Time   O(n)  i and j each move forward across the string once; the join is linear
                 in the output length
    Space  O(n)  parts; the output is at most 2n characters

### Multi-digit parse — num * 10 + digit

Task: decode a run-length string where each letter is followed by its count.
A count can be more than one digit.

    input    s     a letter, then its count in decimal, repeated
    output   dec   each letter written count times

Example: `"a3b12"` becomes three a's followed by twelve b's. The count after
b is 12, not a 1 and then a 2.

Spot it by: digits that arrive one character at a time and have to be read
as one number: calculators (LC 224, LC 227), decode string (LC 394), atoi
(LC 8). Each new digit shifts the number left one decimal place.

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

Trace of `decode_rle("a3b12")`:

    c      action                          letter  num  output so far
    a      flush 0 copies of ''            a       0    ""
    3      num = 0 * 10 + 3                a       3    ""
    b      flush 3 a's, reset              b       0    "aaa"
    1      num = 0 * 10 + 1                b       1    "aaa"
    2      num = 1 * 10 + 2                b       12   "aaa"
    (end)  flush 12 b's                    -       -    "aaa" + 12 b's

The `(end)` row is the flush after the loop. Without it, the twelve b's never
get written.

Trap: the last run has no letter after it to trigger its flush, so without
the loop after the main loop, `"a3b2"` decodes to `"aaa"`. Reset `num` at every
letter, or the counts run together. The first letter flushes `num = 0`
copies, so it needs no special case. In Java, `num * 10 + (c - '0')`
overflows `int` past 10 digits. LC 8 clamps it, and LC 394 and LC 224 parse
numbers with this same line.

    Time   O(n + m)  n = len(s) to parse, m = output length to write
    Space  O(m)      parts holds the decoded output

### Digit extraction — % 10, then // 10

Task: return the sum of the decimal digits of a non-negative integer.

    input    x       an integer, x >= 0
    output   total   sum of x's digits; 0 for x = 0

Example: `digit_sum(1234)` is 1 + 2 + 3 + 4 = 10.

Spot it by: anything that looks at a number's digits without converting it
to a string: digit sums, happy number (LC 202), reversing an integer (LC 7),
palindrome numbers (LC 9).

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

Trace of `digit_sum(1234)`:

    x     x % 10  total after  x // 10
    1234  4       4            123
    123   3       7            12
    12    2       9            1
    1     1       10           0      x is 0: stop

The digits come out last to first. For a sum that doesn't matter, but for
reversing a number it's the whole point.

Trap: negatives behave differently. Python gives `-7 // 10 == -1` and
`-7 % 10 == 3`, while Java gives `0` and `-7`. Take `abs` first and handle
the sign separately (see `docs/modulo.md`). "Count the digits" with this loop
returns 0 for `x = 0`, but 0 has one digit.

    Time   O(d)  d = number of digits = about log10(x)
    Space  O(1)

### Ceil division — add b - 1

Task: return a / b rounded up to the next integer, for `a >= 0` and `b > 0`,
using integer math only.

    input    a   the dividend, a >= 0
             b   the divisor, b > 0
    output   q   the smallest integer q with q * b >= a

Example: `ceil_div(7, 3)` is 3, because two groups of 3 hold only 6. 6 / 3 is
exactly 2, so `ceil_div(6, 3)` stays 2.

Spot it by: "how many groups," "how many trips," "how many hours" when a
partial group still counts as a whole one: Koko's hours per pile (LC 875),
ship capacity (LC 1011), or the number of pages.

```python
# shorthand: add b - 1 before dividing, so any remainder pushes the result up by one
def ceil_div(a, b):
    return (a + b - 1) // b

assert ceil_div(7, 3) == 3
assert ceil_div(6, 3) == 2                         # exact: b - 1 isn't enough to push it over
assert ceil_div(0, 3) == 0                         # nothing to divide
```

Trace of the three asserts with b = 3, so b - 1 = 2:

    a  a % b  a + 2  // 3  result
    7  1      9      3     3      any remainder >= 1 plus 2 crosses the next multiple of 3
    6  0      8      2     2      remainder 0 plus 2 stays short of 9
    0  0      2      0     0

Trap: `math.ceil(a / b)` goes through a float and is wrong once values pass
2^53. In Java, `a + b - 1` can overflow an `int`, so use `long`, or write
`(a - 1) / b + 1` for `a > 0`. This is the hours count in Koko (LC 875).

    Time   O(1)  one add and one integer divide
    Space  O(1)

### 2-D init — one list per row

Task: build a `rows x cols` grid of zeros where each row is its own list, so
writing one cell changes only that cell.

    input    rows, cols   the grid's size
    output   grid         rows lists of cols zeros, indexed grid[r][c]

Example: `make_grid(2, 3)` gives `[[0, 0, 0], [0, 0, 0]]`. After
`grid[0][0] = 9`, only row 0 changes.

Spot it by: any 2-D DP table, visited grid, or matrix you create yourself in
Python. Java's `new int[r][c]` is safe; Python's shortcut `*` is not.

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

Trace of both versions. `A` and `B` name distinct list objects:

    code                  row 0  row 1  after [0][0] = 9
    make_grid(2, 3)       A      B      A = [9, 0, 0], B = [0, 0, 0]
    [[0] * 3] * 2         A      A      A = [9, 0, 0], shown twice

`[0] * cols` is fine because ints are immutable: writing a cell replaces the
int, so there's nothing shared to change. A list is mutable, so a shared row
really is shared.

Trap: `[[0] * cols] * rows` repeats a reference to one row, so writing one
cell writes the whole column. Keep the order fixed: the outer list has `rows`
entries and you index `grid[r][c]`. Java's `new int[rows][cols]` doesn't have
this problem.

    Time   O(rows · cols)  every cell is created once
    Space  O(rows · cols)  the grid

### DP table — n+1 slots, row 0 is empty

Task: return the length of the longest common subsequence of two strings. A
subsequence keeps the characters' order but can skip characters.

    input    a, b     two strings
    output   length   length of the longest string that is a subsequence of both

Example: `lcs("abcde", "ace")` is 3, because "ace" is a subsequence of both.

Spot it by: two strings (or arrays) compared prefix by prefix: LCS, edit
distance (LC 72), interleaving (LC 97), distinct subsequences (LC 115). The
answer for two prefixes depends on the answers for slightly shorter
prefixes, so you fill a 2-D table.

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

Trace of `lcs("abcde", "ace")`, the full table. Rows are prefixes of a,
columns are prefixes of b:

            ""  a   c   e
    ""      0   0   0   0
    a       0   1   1   1      a == a: diagonal 0 + 1
    b       0   1   1   1      b matches nothing: copy the max of up and left
    c       0   1   2   2      c == c: diagonal 1 + 1
    d       0   1   2   2
    e       0   1   2   3      e == e: diagonal 2 + 1 -> answer dp[5][3] = 3

Each match steps diagonally (both prefixes grow), and each mismatch inherits
the better of dropping a's last character or b's.

Trap: the table is shifted one slot from the strings, so comparing `a[i]`
with `b[j]` is off by one and reads past the end on the last row. This is
"prefix with sentinel" in 2-D. Row 0 and column 0 already hold the base case,
so the loops start at 1 with no special case.

    Time   O(n · m)  every cell is filled once in O(1). Trying every subsequence is O(2^n)
    Space  O(n · m)  the table. Each row only reads the row above it, so two rows of
                     m + 1 bring it to O(m)
