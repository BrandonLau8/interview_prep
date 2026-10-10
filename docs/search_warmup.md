# Search warmup

This file has one short, runnable example for each idiom that explores a
space or orders its answers: backtracking, memoized recursion, heaps,
custom ordering, bit tricks, and tries. Each block ends with an `assert`, so
you can paste it into `main.py` and run it.

Assumes you know: section 0 of `docs/array_warmup.md`, and the call tree from
`docs/concepts/recursion.md`, which is the tree that backtracking walks.
Not covered: segment trees, Fenwick trees, and bottom-up DP tables (see "DP
table" in `docs/structure_warmup.md`).

How to use it: read the task, cover the code, and write it from memory. Then
run the asserts and say the invariant out loud. If you can't explain why the
trap breaks it, you memorized the code without understanding it.

    1. Backtracking
    choose, recurse, pop    path.pop() after the call; recurse on i + 1, not start + 1
    copy on record          out.append(path[:]); the bare path is emptied later
    used array              permutations scan from 0 and skip used[i]
    skip duplicates         sort, then i > start and nums[i] == nums[i - 1]
    reuse and prune         recurse on i to reuse; break once sorted values overshoot

    2. Memoized recursion
    memo check first        look up, compute, store, return; no memo={} default
    memo key                key on every argument that changes
    impossible sentinel     return infinity inside; convert to -1 once at the top

    3. Heaps and ordering
    heap of tuples          (priority, tiebreak, item), so ties never compare items
    max-heap                push -x, negate again on pop
    Dijkstra                skip stale entries: d > dist[u]
    custom sort key         negate the number to flip it; reverse=True flips everything
    upper bound             lower bound with < changed to <=
    overlap test            each starts before the other ends
    sort by end             keep the earliest finisher

    4. Bits
    get / set / clear       parenthesize every bit expression
    clear lowest bit        x & (x - 1)
    isolate lowest bit      x & -x

    5. Tries
    insert / search         a word ends only where is_end is set

    6. Counting
    n choose k              multiply, then divide, at every step; never factorials

Every idiom uses the same names, so a name tells you the variable's role:

    nums          the input array
    n             its length, computed once at the top
    path          the choices made so far on the current branch
    out           the output
    start         the first index a backtracking call may choose from
    used          used[i] = nums[i] is already in path
    memo          computed answers: arguments -> result
    key           the memo key, one tuple of every changing argument
    INF           float('inf'): "impossible" or "not reached yet"
    heap          a heapq min-heap
    entry         one tuple popped from the heap
    adj           adjacency list: adj[u] = neighbours of u
    dist          dist[v] = shortest distance found so far
    lo, hi, mid   the binary search range and its middle
    end           the end of the last kept interval
    x, i          an integer, and a bit position in it
    node, root    a trie node, and the empty-string node at the top


## 1. Backtracking

### Choose, recurse, pop

Task: return every way to choose k numbers from 1..n, each combination in
increasing order.

```python
# shorthand: add a candidate to the path, recurse on the candidates after it, remove it, try the next one
def combine(n, k):  # LC 77
    out = []
    path = []                          # invariant: path = the current choices, increasing
    def backtrack(start):
        if len(path) == k:
            out.append(path[:])        # copy: path keeps changing after this
            return
        for i in range(start, n + 1):
            path.append(i)             # choose
            backtrack(i + 1)           # recurse: only numbers after i
            path.pop()                 # un-choose
    backtrack(1)
    return out

assert combine(4, 2) == [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
assert combine(2, 0) == [[]]                       # k = 0: one way to choose nothing
```

Trap: without `path.pop()`, the next loop iteration inherits this branch's
choice, so the paths only ever grow. Recurse on `i + 1`, not `start + 1`.
With `start + 1`, choosing 3 lets the next level choose 2 again, which
produces `[3, 2]` alongside `[2, 3]`.

### Copy on record

Task: return every subset of a list of distinct values.

```python
# shorthand: record a copy of the path at every call, then extend it with each later element
def subsets(nums):  # LC 78
    n = len(nums)
    out = []
    path = []
    def backtrack(start):
        out.append(path[:])            # every call is a subset, not just the leaves
        for i in range(start, n):
            path.append(nums[i])
            backtrack(i + 1)
            path.pop()
    backtrack(0)
    return out

assert subsets([1, 2, 3]) == [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
assert subsets([]) == [[]]                         # empty input: just the empty subset

shared = []
path = [1]
shared.append(path)                    # no copy
path.pop()
assert shared == [[]]                              # the trap: the recorded list was emptied later
```

Trap: `out.append(path)` records a reference to the one list that every
branch edits. By the end, all the entries are the same emptied list. In
Java, it's `out.add(new ArrayList<>(path))`.

### Used array — permutations

Task: return every ordering of a list of distinct values.

```python
# shorthand: try every unused element in the next slot, mark it used, recurse, then unmark it
def permute(nums):  # LC 46
    n = len(nums)
    out = []
    path = []
    used = [False] * n                 # invariant: used[i] = nums[i] is in path
    def backtrack():
        if len(path) == n:
            out.append(path[:])
            return
        for i in range(n):             # from 0, not start: an earlier element can go in a later slot
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            backtrack()
            path.pop()
            used[i] = False            # undo both: the path and the mark
    backtrack()
    return out

assert permute([1, 2, 3]) == [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
assert permute([1]) == [[1]]                       # single element
```

Trap: a `start` index is for combinations, where order doesn't matter.
Permutations need every unused element at every slot, so the loop starts
at 0. If you undo the path but forget `used[i] = False`, every later branch
loses that element.

### Skip duplicates — same value, same depth

Task: return every distinct subset of a list that can contain duplicates.

```python
# shorthand: sort, then at each depth skip any element equal to the one just tried at the same depth
def subsets_with_dup(nums):  # LC 90
    nums = sorted(nums)                # equal values must sit next to each other
    n = len(nums)
    out = []
    path = []
    def backtrack(start):
        out.append(path[:])
        for i in range(start, n):
            if i > start and nums[i] == nums[i - 1]:
                continue               # same value at the same depth: that branch was already explored
            path.append(nums[i])
            backtrack(i + 1)
            path.pop()
    backtrack(0)
    return out

assert subsets_with_dup([1, 2, 2]) == [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]
assert subsets_with_dup([2, 2]) == [[], [2], [2, 2]]   # all equal: [2, 2] is kept, the second [2] is skipped
```

Trap: the condition is `i > start`, not `i > 0`. With `i > 0`, the second 2
is also skipped one level deeper, where it extends `[2]` rather than repeating
it, so `[2, 2]` is lost. Without sorting, the equal values aren't adjacent and
the check misses them.

### Reuse and prune

Task: given distinct positive values, return every combination that sums to
`target`, where each value can be used any number of times.

```python
# shorthand: sort, recurse with the same index to allow reuse, and stop the loop once a candidate overshoots
def combination_sum(nums, target):  # LC 39
    nums = sorted(nums)
    n = len(nums)
    out = []
    path = []
    def backtrack(start, remaining):
        if remaining == 0:
            out.append(path[:])
            return
        for i in range(start, n):
            if nums[i] > remaining:
                break                  # sorted: every later candidate overshoots too
            path.append(nums[i])
            backtrack(i, remaining - nums[i])   # i, not i + 1: nums[i] can be used again
            path.pop()
    backtrack(0, target)
    return out

assert combination_sum([2, 3, 6, 7], 7) == [[2, 2, 3], [7]]
assert combination_sum([2], 1) == []               # nothing fits
```

Trap: recursing on `i` allows reuse. Recursing on `0` allows reuse but also
reordering, so you get `[2, 2, 3]`, `[2, 3, 2]` and `[3, 2, 2]`. The `break`
is only safe because the values are sorted. On unsorted input, use
`continue`.


## 2. Memoized recursion

### Memo check first

Task: you climb a staircase of n steps, 1 or 2 steps at a time. Return the
number of distinct ways to reach the top.

```python
# shorthand: return the stored answer if there is one; otherwise compute it, store it, and return it
def climb_stairs(n):  # LC 70
    memo = {}                          # invariant: memo[i] = ways to climb i steps, once computed
    def ways(i):
        if i <= 1:
            return 1                   # 0 or 1 steps: one way
        if i in memo:
            return memo[i]
        result = ways(i - 1) + ways(i - 2)
        memo[i] = result               # store before returning
        return result
    return ways(n)

assert climb_stairs(5) == 8
assert climb_stairs(0) == 1                        # zero steps: one way, which is doing nothing
assert climb_stairs(80) == 37889062373143906       # without the memo, this never finishes
```

Trap: create the memo inside the wrapper. `def ways(i, memo={})` creates one
dict when the function is defined, and every later call shares it, including
calls for a different input. If you forget the store line, the code is still
correct but takes exponential time. In Java, the third answer needs a
`long`.

### Memo key — every argument that changes

Task: a robot starts at the top-left of a `rows x cols` grid and moves only
right or down. Return the number of paths to the bottom-right.

```python
# shorthand: key the memo on every argument that changes; the answer at (r, c) is the paths going down plus the paths going right
def unique_paths(rows, cols):  # LC 62
    memo = {}                          # invariant: memo[(r, c)] = paths from (r, c) to the bottom-right
    def paths(r, c):
        if r == rows - 1 or c == cols - 1:
            return 1                   # last row or column: one straight path
        key = (r, c)
        if key in memo:
            return memo[key]
        result = paths(r + 1, c) + paths(r, c + 1)
        memo[key] = result
        return result
    return paths(0, 0)

assert unique_paths(3, 7) == 28
assert unique_paths(1, 1) == 1                     # one cell: already at the goal
assert unique_paths(18, 18) == 2333606220          # too slow without the memo; past int range in Java
```

Trap: keying on `r` alone returns the first column's answer for every column.
The key holds every argument that changes between calls, and nothing that
doesn't. In Java, use an `int[rows][cols]` filled with -1, not 0, because 0
can be a real answer.

### Impossible sentinel — infinity inside, -1 outside

Task: return the fewest coins that add up to `amount`, or -1 if no
combination does. Each coin can be used any number of times.

```python
# shorthand: try each coin as the last one and take the cheapest; impossible returns infinity, converted to -1 only at the top
def coin_change(coins, amount):  # LC 322
    INF = float('inf')
    memo = {}                          # invariant: memo[a] = fewest coins summing to a, INF if impossible
    def fewest(a):
        if a == 0:
            return 0
        if a < 0:
            return INF
        if a in memo:
            return memo[a]
        best = INF
        for i in range(len(coins)):
            sub = fewest(a - coins[i])
            if sub + 1 < best:
                best = sub + 1
        memo[a] = best
        return best
    result = fewest(amount)
    if result == INF:
        return -1                      # convert once, at the top
    return result

assert coin_change([1, 2, 5], 11) == 3
assert coin_change([2], 3) == -1                   # impossible
assert coin_change([1], 0) == 0                    # amount 0: zero coins
```

Trap: returning -1 inside the recursion makes `sub + 1` equal 0, which then
wins every `min`. Keep "impossible" as a value that loses every comparison.
In Java, `Integer.MAX_VALUE + 1` overflows, so use `amount + 1` as the
sentinel. With a coin of 1, the recursion goes `amount` levels deep, which
passes Python's limit of about 1000.


## 3. Heaps and ordering

### Heap of tuples — add a tiebreak

Task: merge k sorted arrays into one sorted array.

```python
import heapq

# shorthand: push the first element of each array; pop the smallest, record it, and push the next element from the same array
def merge_k_sorted(arrays):
    heap = []                          # invariant: heap holds the next unmerged element of each array that has one
    for i in range(len(arrays)):
        if len(arrays[i]) > 0:
            heapq.heappush(heap, (arrays[i][0], i, 0))   # (value, which array, index in it)
    out = []
    while len(heap) > 0:
        entry = heapq.heappop(heap)
        val = entry[0]
        i = entry[1]
        j = entry[2]
        out.append(val)
        if j + 1 < len(arrays[i]):
            heapq.heappush(heap, (arrays[i][j + 1], i, j + 1))
    return out

assert merge_k_sorted([[1, 4, 5], [1, 3, 4], [2, 6]]) == [1, 1, 2, 3, 4, 4, 5, 6]
assert merge_k_sorted([[], [1]]) == [1]            # an empty array is never pushed
```

Trap: tuples compare element by element. With `(val, node)`, two equal values
make Python compare the nodes, which raises `TypeError`. An integer second
field breaks every tie first. In Java, use
`new PriorityQueue<int[]>((x, y) -> Integer.compare(x[0], y[0]))`.

### Max-heap — push the negative

Task: repeatedly smash the two heaviest stones together. Equal stones are
both destroyed; otherwise the difference goes back. Return the last stone's
weight, or 0.

```python
# shorthand: push negatives so the min-heap's smallest is the real largest; negate again when you pop
def last_stone_weight(stones):  # LC 1046
    heap = []                          # invariant: heap holds -w for every stone w still in play
    for i in range(len(stones)):
        heapq.heappush(heap, -stones[i])
    while len(heap) > 1:
        a = -heapq.heappop(heap)       # heaviest
        b = -heapq.heappop(heap)       # second heaviest
        if a != b:
            heapq.heappush(heap, -(a - b))
    if len(heap) == 0:
        return 0
    return -heap[0]

assert last_stone_weight([2, 7, 4, 1, 8, 1]) == 1
assert last_stone_weight([3, 3]) == 0              # equal stones destroy each other: the heap empties
```

Trap: every push negates and every pop negates. Miss one and that value
sorts backwards. In Java, use
`new PriorityQueue<>(Collections.reverseOrder())` instead of negating,
because `-Integer.MIN_VALUE` overflows.

### Dijkstra — skip stale entries

Task: given directed edges `[u, v, w]` with non-negative weights, return the
shortest distance from `src` to every node, or infinity where unreachable.

```python
# shorthand: pop the closest node, skip it if a shorter distance was already found, then relax its edges
def dijkstra(n, edges, src):
    INF = float('inf')
    adj = []
    for i in range(n):
        adj.append([])
    for i in range(len(edges)):
        adj[edges[i][0]].append((edges[i][1], edges[i][2]))
    dist = [INF] * n                   # invariant: dist[v] = shortest distance found so far
    dist[src] = 0
    heap = [(0, src)]
    while len(heap) > 0:
        entry = heapq.heappop(heap)
        d = entry[0]
        u = entry[1]
        if d > dist[u]:
            continue                   # stale: a shorter path to u was already processed
        for i in range(len(adj[u])):
            v = adj[u][i][0]
            w = adj[u][i][1]
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (dist[v], v))
    return dist

edges = [[0, 1, 4], [0, 2, 1], [2, 1, 2], [1, 3, 1]]
assert dijkstra(4, edges, 0) == [0, 3, 1, 4]       # 0 -> 2 -> 1 beats the direct 0 -> 1
assert dijkstra(2, [], 0) == [0, float('inf')]     # unreachable
```

Trap: BFS marks a node when it's pushed, but here the first push isn't always
the shortest. Node 1 is first pushed at 4, then again at 3. A node is final
only when it's popped. The heap can't update entries in place, so old ones
stay in it, and `d > dist[u]` discards them. Negative weights break the "final
when popped" rule.

### Custom sort key — negate to flip one field

Task: sort `[word, count]` pairs by count from high to low, breaking ties
alphabetically.

```python
# shorthand: sort by a tuple key; negate the number to flip its direction, and leave the tiebreak ascending
def sort_by_count(pairs):
    pairs.sort(key=lambda p: (-p[1], p[0]))   # count descending, then word ascending
    return pairs

assert sort_by_count([["b", 2], ["a", 2], ["c", 5]]) == [["c", 5], ["a", 2], ["b", 2]]
assert sort_by_count([]) == []                     # empty input
```

Trap: `reverse=True` flips every field, so the tie on 2 comes out `b, a`. You
can't negate a string, so if the string field has to descend, use
`functools.cmp_to_key`. In Java, `(x, y) -> y.count - x.count` overflows for
values far apart. Write `Integer.compare(y.count, x.count)`, then
`x.word.compareTo(y.word)`.

### Upper bound — < becomes <=

Task: `nums` is sorted. Return the first index whose value is greater than
`target`, and use it to count how many times `target` appears.

```python
# shorthand: same as lower bound, but move right past mid while it's <= target
def lower_bound(nums, target):
    lo = 0
    hi = len(nums)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def upper_bound(nums, target):
    lo = 0
    hi = len(nums)                     # invariant: nums[0:lo] <= target, nums[hi:] > target
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] <= target:        # the only change from lower bound
            lo = mid + 1
        else:
            hi = mid
    return lo

nums = [1, 2, 2, 2, 3]
assert upper_bound(nums, 2) == 4
assert upper_bound(nums, 2) - lower_bound(nums, 2) == 3    # count of 2s
assert upper_bound(nums, 2) - 1 == 3                       # last index of 2
assert upper_bound(nums, 5) - lower_bound(nums, 5) == 0    # absent: both bounds land on the same index
assert upper_bound([], 1) == 0                             # empty
```

Trap: the last occurrence is `upper_bound - 1`, which may hold a smaller value
or be -1. Check `nums[idx] == target` before trusting it (LC 34). Everything
else is the lower bound template. Change only the comparison.

### Overlap test — each starts before the other ends

Task: return whether two half-open intervals `[start, end)` overlap.

```python
# shorthand: two intervals overlap when each one starts before the other ends
def overlaps(a, b):
    return a[0] < b[1] and b[0] < a[1]

assert overlaps([1, 5], [4, 8]) is True
assert overlaps([1, 10], [3, 4]) is True           # nested: b's start is inside a, a's start isn't inside b
assert overlaps([1, 3], [3, 5]) is False           # touching: [1, 3) ends where [3, 5) starts
assert overlaps([4, 8], [1, 5]) is True            # argument order doesn't matter
```

Trap: "a's start is inside b" misses the nested case. The two-condition form
covers every arrangement. Closed intervals, where touching counts, use `<=`.
That's why merge intervals (LC 56) tests `iv[0] <= merged[-1][1]`.

### Sort by end — keep the earliest finisher

Task: return the fewest intervals to remove so the rest don't overlap.
Touching intervals don't count as overlapping.

```python
# shorthand: sort by end, keep each interval that starts at or after the last kept end, count the rest as removed
def erase_overlap_intervals(intervals):  # LC 435
    intervals = sorted(intervals, key=lambda iv: iv[1])
    removed = 0
    end = float('-inf')                # invariant: end = end of the last kept interval
    for i in range(len(intervals)):
        if intervals[i][0] >= end:     # touching is allowed
            end = intervals[i][1]
        else:
            removed += 1
    return removed

assert erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]]) == 1
assert erase_overlap_intervals([[1, 100], [2, 3], [3, 4]]) == 1   # long interval first: sort by start keeps it and removes two
assert erase_overlap_intervals([]) == 0                           # empty input
```

Trap: when you're choosing intervals, sort by end. The interval that finishes
first leaves the most room for the rest. Merging (LC 56) sorts by start
because it combines intervals instead of choosing among them. The same loop
counts the minimum arrows to burst balloons (LC 452), with `>` for closed
intervals.


## 4. Bits

### Get, set, clear, toggle — parenthesize everything

Task: read, set, clear, and flip bit i of x.

```python
# shorthand: shift a 1 to position i, then AND to test, OR to set, AND with its complement to clear, XOR to flip
def get_bit(x, i):
    return (x >> i) & 1

def set_bit(x, i):
    return x | (1 << i)

def clear_bit(x, i):
    return x & ~(1 << i)

def toggle_bit(x, i):
    return x ^ (1 << i)

x = 0b1010                             # 10
assert get_bit(x, 1) == 1
assert get_bit(x, 0) == 0
assert set_bit(x, 0) == 0b1011
assert clear_bit(x, 3) == 0b0010
assert toggle_bit(x, 1) == 0b1000
assert set_bit(x, 1) == x                          # already set: no change
```

Trap: in Java and C++, `==` binds tighter than `&`, so `x & 1 << i == 0`
parses as `x & ((1 << i) == 0)`. Python parses it the other way, which hides
the bug. Parenthesize every bit expression. In Java, `1 << 31` is negative and
`1 << 32` wraps to 1, so use `1L << i` for 64-bit masks.

### Clear the lowest set bit — x & (x - 1)

Task: count the 1 bits in x, and test whether x is a power of two.

```python
# shorthand: x & (x - 1) removes the lowest 1 bit; count how many removals it takes to reach 0
def count_bits(x):  # LC 191, x >= 0
    count = 0
    while x != 0:                      # invariant: count = 1 bits already removed from x
        x = x & (x - 1)
        count += 1
    return count

def is_power_of_two(x):  # LC 231
    return x > 0 and (x & (x - 1)) == 0

assert count_bits(0b1011) == 3
assert count_bits(0) == 0                          # zero: no bits to remove
assert is_power_of_two(16) is True
assert is_power_of_two(6) is False
assert is_power_of_two(0) is False                 # zero: 0 & -1 == 0, so the x > 0 guard is needed
```

Trap: `x - 1` flips the lowest 1 to 0 and every 0 below it to 1, so the AND
clears exactly that bit. Python integers have unbounded sign bits, so a
negative x loops forever. Mask it first with `x & 0xFFFFFFFF`. In Java, use
`Integer.bitCount`, or shift with `>>>`.

### Isolate the lowest set bit — x & -x

Task: return the value of x's lowest 1 bit.

```python
# shorthand: -x flips every bit above the lowest 1 and keeps that 1, so x & -x leaves only it
def lowest_bit(x):                     # x > 0
    return x & -x

assert lowest_bit(0b1100) == 0b0100
assert lowest_bit(7) == 1
assert lowest_bit(8) == 8                          # power of two: the bit is the number
assert lowest_bit(0) == 0                          # zero: no bit to isolate
```

Trap: two's complement makes `-x == ~x + 1`. The `+ 1` carries up to the
lowest 1 bit, and everything above it is inverted. Use it to split numbers
into two groups by one differing bit (LC 260). It's also the index step in a
Fenwick tree.


## 5. Tries

### Insert / search — the end flag

Task: build a prefix tree that supports inserting a word, searching for a
whole word, and checking whether any word starts with a prefix.

```python
# shorthand: walk one child per character, creating missing ones on insert; a word ends only where the flag is set
class TrieNode:
    def __init__(self):
        self.children = {}             # char -> TrieNode
        self.is_end = False            # a word ends here, rather than just passing through

class Trie:  # LC 208
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for i in range(len(word)):
            c = word[i]
            if c not in node.children:
                node.children[c] = TrieNode()
            node = node.children[c]
        node.is_end = True

    def walk(self, s):                 # the node that s leads to, or None
        node = self.root
        for i in range(len(s)):
            c = s[i]
            if c not in node.children:
                return None
            node = node.children[c]
        return node

    def search(self, word):
        node = self.walk(word)
        return node is not None and node.is_end

    def starts_with(self, prefix):
        return self.walk(prefix) is not None

trie = Trie()
trie.insert("apple")
assert trie.search("apple") is True
assert trie.search("app") is False                 # prefix of a word, but not a word itself
assert trie.starts_with("app") is True
trie.insert("app")
assert trie.search("app") is True                  # now it's a word: the flag is set
assert trie.starts_with("") is True                # empty prefix: the root
```

Trap: without `is_end`, `search` returns `True` for every prefix of every
word. `search` and `starts_with` share the walk and differ only in that flag.
In Java, use `TrieNode[] children = new TrieNode[26]` and index with
`c - 'a'`.


## 6. Counting

### n choose k — multiply, then divide

Task: return C(n, k), the number of ways to choose k items from n, without
computing any factorial.

```python
# shorthand: multiply by the next top factor, then divide by the next bottom factor; every step stays an exact integer
def n_choose_k(n, k):
    if k < 0 or k > n:
        return 0
    if k > n - k:
        k = n - k                      # C(n, k) == C(n, n - k): fewer steps
    result = 1                         # invariant: after step i, result = C(n - k + i, i)
    for i in range(1, k + 1):
        result = result * (n - k + i) // i    # multiply first: the product is divisible by i
    return result

assert n_choose_k(5, 2) == 10
assert n_choose_k(34, 17) == 2333606220            # unique paths on an 18 x 18 grid: C(m+n-2, m-1)
assert n_choose_k(5, 0) == 1                       # k = 0: one way to choose nothing
assert n_choose_k(3, 5) == 0                       # k > n: no way

wrong = 1
for i in range(1, 3):
    wrong *= (3 + i) // i              # divide first: 5 // 2 truncates to 2
assert wrong == 8                                  # the trap: C(5, 2) is 10
```

Trap: the order is the idiom. `result * (n - k + i)` equals `i * C(n - k + i, i)`,
so dividing that product by `i` is exact. Dividing `(n - k + i) // i` first
truncates. The factorial formula `n! / (k! (n - k)!)` overflows a Java `long`
from 21! on, even when the answer is small. If the answer must be taken mod
1e9+7, the division doesn't work under the mod. Use Pascal's rule
`C(n, k) = C(n-1, k-1) + C(n-1, k)` in a DP table instead.
