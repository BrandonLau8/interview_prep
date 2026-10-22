# Search warmup

This file has one short, runnable example for each idiom that explores a
space or orders its answers: backtracking, memoized recursion, heaps,
custom ordering, bit tricks, and tries. Each block ends with an `assert`, so
you can paste it into `main.py` and run it.

Assumes you know: section 0 of `docs/array_warmup.md`, and the call tree from
`docs/concepts/recursion.md`, which is the tree that backtracking walks.
Not covered: segment trees, Fenwick trees, and bottom-up DP tables (see "DP
table" in `docs/structure_warmup.md`).

How to use it: read the task and the "Spot it by" line, cover the code, and
write it from memory. Then run the asserts, step through the trace, and say
the invariant out loud. If you can't explain why the trap breaks it, you
memorized the code without understanding it. The Time / Space block says
where each bound comes from, which is the sentence an interviewer wants to
hear.

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
    adj           adjacency list: adj[u] = a (v, w) pair for each edge out of u
    u, v, w       an edge from u to v that costs w: v is a node, used as an index
                  (dist[v]); w is a cost, added to a distance (d + w)
    d             the distance a heap entry was pushed with
    dist          dist[v] = shortest distance found so far
    lo, hi, mid   the binary search range and its middle
    end           the end of the last kept interval
    x, i          an integer, and a bit position in it
    node, root    a trie node, and the empty-string node at the top


## 1. Backtracking

### Choose, recurse, pop

Task: return every way to choose k different numbers from 1..n. Order
doesn't matter, so `[1, 2]` and `[2, 1]` are the same combination and appear
once.

    input    n      the numbers to choose from are 1, 2, ..., n
             k      how many to choose
    output   out    every combination, each listed in increasing order

Example: `combine(4, 2)` returns `[[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]`,
the 6 ways to pick 2 of 4.

Spot it by: "return all combinations" or "choose k." The output is every
selection, so there's no shortcut: you have to generate each one. Order
doesn't matter, so each call only picks from numbers after the last pick.

```python
# shorthand: add a candidate to the path, recurse on the candidates after it, remove it, try the next one
def combine(n: int, k: int) -> list[list[int]]:  # LC 77
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

Trace of `combine(4, 2)`. Indentation is call depth; `+x` is choose x, and
the pop after each call is implied:

    backtrack(1)   path []
      +1           path [1]
        +2         path [1, 2]    len 2: record
        +3         path [1, 3]    record
        +4         path [1, 4]    record
      +2           path [2]
        +3         path [2, 3]    record
        +4         path [2, 4]    record
      +3           path [3]
        +4         path [3, 4]    record
      +4           path [4]       range(5, 5) is empty: dead end, nothing recorded

Each level only offers numbers bigger than the last choice, which is why
`[2, 1]` can never be built.

Trap: without `path.pop()`, the next loop iteration inherits this branch's
choice, so the paths only ever grow. Recurse on `i + 1`, not `start + 1`.
With `start + 1`, choosing 3 lets the next level choose 2 again, which
produces `[3, 2]` alongside `[2, 3]`.

    Time   O(k · C(n, k))  C(n, k) leaves, each copied in O(k); the internal calls that
                           lead to them are bounded by the same order
    Space  O(k)            path and the recursion depth both stop at k; out isn't counted

### Copy on record

Task: return every subset of a list of distinct values, including the empty
subset and the whole list.

    input    nums   distinct values
    output   out    every subset, 2^n of them; each keeps the input's order

Example: `subsets([1, 2, 3])` returns 8 subsets, from `[]` to `[1, 2, 3]`.

Spot it by: "all subsets" or "power set." Each element is either in or out.
Unlike combinations of a fixed size, every partial path is already an answer,
so you record at every call, not only when the path reaches some length.

```python
# shorthand: record a copy of the path at every call, then extend it with each later element
def subsets(nums: list[int]) -> list[list[int]]:  # LC 78
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

Trace of `subsets([1, 2, 3])`. Every call records first, then extends:

    backtrack(0)               record []
      +1  backtrack(1)         record [1]
        +2  backtrack(2)       record [1, 2]
          +3  backtrack(3)     record [1, 2, 3]
        +3  backtrack(3)       record [1, 3]
      +2  backtrack(2)         record [2]
        +3  backtrack(3)       record [2, 3]
      +3  backtrack(3)         record [3]

8 calls, 8 records, in the same order as the assert. The calls at depth 3
have `range(3, 3)`, so they record and return.

Trap: `out.append(path)` records a reference to the one list that every
branch edits. By the end, all the entries are the same emptied list. In
Java, it's `out.add(new ArrayList<>(path))`.

    Time   O(n · 2^n)  2^n calls, one per subset, and each copies a path of up to n
    Space  O(n)        path and the recursion depth; out isn't counted

### Used array — permutations

Task: return every ordering of a list of distinct values. Unlike a
combination, order matters here, so `[1, 2]` and `[2, 1]` are both answers.

    input    nums   distinct values
    output   out    every permutation, n! of them; each uses every value exactly once

Example: `permute([1, 2, 3])` returns the 6 orderings, from `[1, 2, 3]` to
`[3, 2, 1]`.

Spot it by: "all orderings" or "arrangements," where `[1, 2]` and `[2, 1]`
both count. Any element not yet placed can fill the next slot, so you track
what's used rather than a start index.

```python
# shorthand: try every unused element in the next slot, mark it used, recurse, then unmark it
def permute(nums: list[int]) -> list[list[int]]:  # LC 46
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

Trace of `permute([1, 2, 3])`. `used` is shown as T/F for indices 0, 1, 2:

    path          used    note
    []            F F F
      [1]         T F F
        [1, 2]    T T F
          [1, 2, 3]  T T T   record
        [1, 3]    T F T   2 was un-used on the way back up
          [1, 3, 2]  T T T   record
      [2]         F T F   1 is free again
        [2, 1]    T T F
          [2, 1, 3]  T T T   record
        [2, 3]    F T T
          [2, 3, 1]  T T T   record
      [3]         F F T
        [3, 1]    T F T
          [3, 1, 2]  T T T   record
        [3, 2]    F T T
          [3, 2, 1]  T T T   record

At `[2]`, the loop starts at 0 and puts the 1 in slot 2. A `start` index
would have skipped it.

Trap: a `start` index is for combinations, where order doesn't matter.
Permutations need every unused element at every slot, so the loop starts
at 0. If you undo the path but forget `used[i] = False`, every later branch
loses that element.

    Time   O(n · n!)  n! leaves, each copied in O(n); every call also scans all n slots
                      of used, and there are about e · n! calls in total
    Space  O(n)       path, used, and the recursion depth; out isn't counted

### Skip duplicates — same value, same depth

Task: return every subset of a list that may contain repeated values, with
each distinct subset listed only once.

    input    nums   values, possibly repeated, in any order
    output   out    every distinct subset, each in sorted order

Example: `subsets_with_dup([1, 2, 2])` returns 6 subsets. `[1, 2]` appears
once, even though either 2 could fill it.

Spot it by: the input "may contain duplicates" and the output "must not
contain duplicate subsets" (or combinations, or permutations). Sorting puts
equal values side by side, so a duplicate branch is just "the same value as
the sibling I just tried."

```python
# shorthand: sort, then at each depth skip any element equal to the one just tried at the same depth
def subsets_with_dup(nums: list[int]) -> list[list[int]]:  # LC 90
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

Trace of `subsets_with_dup([1, 2, 2])` (already sorted):

    backtrack(0)               record []
      i=0 +1  backtrack(1)     record [1]
        i=1 +2  backtrack(2)   record [1, 2]
          i=2 +2 backtrack(3)  record [1, 2, 2]
        i=2: 2 > start 1 and nums[2] == nums[1]: skip     would repeat [1, 2]
      i=1 +2  backtrack(2)     record [2]
        i=2: 2 == start 2, not skipped
          +2  backtrack(3)     record [2, 2]
      i=2: 2 > start 0 and nums[2] == nums[1]: skip       would repeat [2] and [2, 2]

The two `i=2` decisions under `[2]` and at the top are the same value at
different depths. The one at the top is skipped; the one under `[2]` isn't,
because there it's the first choice at its depth.

Trap: the condition is `i > start`, not `i > 0`. With `i > 0`, the second 2
is also skipped one level deeper, where it extends `[2]` rather than repeating
it, so `[2, 2]` is lost. Without sorting, the equal values aren't adjacent and
the check misses them.

    Time   O(n · 2^n)  the worst case is all-distinct input, where nothing is skipped;
                       the O(n log n) sort is smaller
    Space  O(n)        the sorted copy, path, and the recursion depth; out isn't counted

### Reuse and prune

Task: return every combination of values that adds up to `target`. Each
value can be used any number of times.

    input    nums     distinct positive values
             target   the sum to reach
    output   out      every combination that sums to target, each in sorted order

Example: `combination_sum([2, 3, 6, 7], 7)` returns `[[2, 2, 3], [7]]`. The
first combination uses 2 twice.

Spot it by: "sum to target," "may be used an unlimited number of times,"
and positive values. Reuse means recursing on `i` instead of `i + 1`.
Positive values that are sorted mean the first candidate that overshoots
ends the loop.

```python
# shorthand: sort, recurse with the same index to allow reuse, and stop the loop once a candidate overshoots
def combination_sum(nums: list[int], target: int) -> list[list[int]]:  # LC 39
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

Trace of `combination_sum([2, 3, 6, 7], 7)`. Each call shows
`(start, remaining)`:

    (0, 7)  path []
      +2 (0, 5)  path [2]
        +2 (0, 3)  path [2, 2]
          +2 (0, 1)  path [2, 2, 2]     2 > 1: break
          +3 (1, 0)  path [2, 2, 3]     remaining 0: record
          6 > 3: break
        +3 (1, 2)  path [2, 3]          3 > 2: break
        6 > 5: break
      +3 (1, 4)  path [3]
        +3 (1, 1)  path [3, 3]          3 > 1: break
        6 > 4: break
      +6 (2, 1)  path [6]               6 > 1: break
      +7 (3, 0)  path [7]               record

`+2 (0, 5)` keeps start at 0, which is the reuse. `+3 (1, 4)` starts at 1,
so `[3, 2, ...]` is never tried, which keeps every path sorted.

Trap: recursing on `i` allows reuse. Recursing on `0` allows reuse but also
reordering, so you get `[2, 2, 3]`, `[2, 3, 2]` and `[3, 2, 2]`. The `break`
is only safe because the values are sorted. On unsorted input, use
`continue`.

    Time   O(n^(T/m))  T = target, m = smallest value: the tree is at most T/m deep and
                       branches at most n ways per level. Pruning cuts most of it in practice
    Space  O(T/m)      the recursion depth and path length; out isn't counted


## 2. Memoized recursion

### Memo check first

Task: you climb a staircase of n steps, taking 1 or 2 steps at a time.
Return the number of distinct ways to reach the top.

    input    n       steps in the staircase, n >= 0
    output   count   distinct sequences of 1s and 2s that add up to n

Example: `climb_stairs(3)` returns 3: 1 + 1 + 1, 1 + 2, and 2 + 1. Order
matters, so 1 + 2 and 2 + 1 count separately.

Spot it by: a recursive answer that calls itself on the same smaller inputs
again and again. `ways(5)` needs `ways(4)` and `ways(3)`, and `ways(4)` needs
`ways(3)` again. Counting, min, or max over choices, with repeated
subproblems, means memoize.

```python
# shorthand: return the stored answer if there is one; otherwise compute it, store it, and return it
def climb_stairs(n: int) -> int:  # LC 70
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

Trace of `climb_stairs(5)`. Indentation is call depth, and `ways(i - 1)` runs
before `ways(i - 2)`.

    ways(5)                       miss
      ways(4)                     miss
        ways(3)                   miss
          ways(2)                 miss
            ways(1)               base: 1
            ways(0)               base: 1
          ways(2) = 1 + 1 = 2               store {2: 2}
          ways(1)                 base: 1
        ways(3) = 2 + 1 = 3                 store {2: 2, 3: 3}
        ways(2)                   hit: 2
      ways(4) = 3 + 2 = 5                   store {2: 2, 3: 3, 4: 5}
      ways(3)                     hit: 3
    ways(5) = 5 + 3 = 8                     store {2: 2, 3: 3, 4: 5, 5: 8}

That's 9 calls. Plain recursion makes 15, because each hit replaces a whole
subtree: `ways(2)` is 3 calls and `ways(3)` is 5. The first descent goes
straight down to `ways(0)` and fills the memo, so every `ways(i - 2)` after
that is a base case or a hit.

Trap: create the memo inside the wrapper. `def ways(i, memo={})` creates one
dict when the function is defined, and every later call shares it, including
calls for a different input. If you forget the store line, the code is still
correct but takes exponential time. In Java, the third answer needs a
`long`.

    Time   O(n)  each ways(i) is computed once, doing O(1) work; every later call is a hit.
                 Without the memo the call tree is O(2^n) (about 1.6^n)
    Space  O(n)  the memo holds n - 1 entries, and the first descent is n calls deep

### Memo key — every argument that changes

Task: a robot starts at the top-left of a `rows x cols` grid and moves one
cell right or one cell down at a time. Return the number of paths to the
bottom-right.

    input    rows, cols   the grid's size
    output   count        paths from (0, 0) to (rows - 1, cols - 1)

Example: `unique_paths(2, 3)` returns 3: right-right-down, right-down-right,
and down-right-right.

Spot it by: the recursion has more than one argument that changes between
calls, here a row and a column. The memo key has to be all of them together.
"Count the paths through a grid, moving only right or down" is the classic
case.

```python
# shorthand: key the memo on every argument that changes; the answer at (r, c) is the paths going down plus the paths going right
def unique_paths(rows: int, cols: int) -> int:  # LC 62
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

Trace of `unique_paths(3, 3)`. Down, `(r + 1, c)`, runs before right,
`(r, c + 1)`.

    paths(0,0)                    miss
      paths(1,0)                  miss
        paths(2,0)                last row: 1
        paths(1,1)                miss
          paths(2,1)              last row: 1
          paths(1,2)              last col: 1
        paths(1,1) = 1 + 1 = 2              store {(1,1): 2}
      paths(1,0) = 1 + 2 = 3                store {(1,1): 2, (1,0): 3}
      paths(0,1)                  miss
        paths(1,1)                hit: 2
        paths(0,2)                last col: 1
      paths(0,1) = 2 + 1 = 3                store {.., (0,1): 3}
    paths(0,0) = 3 + 3 = 6                  store {.., (0,0): 6}

Cell `(1,1)` is reached twice, once from above and once from the left, and
the second visit is a hit. On a 3 x 3 grid that saves only 2 calls (9 against
11). By 18 x 18, plain recursion needs about 4.7 billion calls.
If the memo is keyed on `r` alone, `paths(1,0)` overwrites `memo[1]` with 3, so
the later `paths(1,1)` hit returns 3 instead of 2, and the total comes out 7.

Trap: keying on `r` alone returns the first column's answer for every column.
The key holds every argument that changes between calls, and nothing that
doesn't. In Java, use an `int[rows][cols]` filled with -1, not 0, because 0
can be a real answer.

    Time   O(rows · cols)  one computation per distinct (r, c) key, O(1) work each
    Space  O(rows · cols)  the memo; the recursion is at most rows + cols deep

### Impossible sentinel — infinity inside, -1 outside

Task: return the fewest coins that add up to `amount`, or -1 if no
combination does. Each coin can be used any number of times.

    input    coins    coin values
             amount   the total to make
    output   count    fewest coins that sum to amount; -1 if no combination does

Example: `coin_change([1, 2, 5], 11)` returns 3, for 5 + 5 + 1.
`coin_change([2], 3)` returns -1, because 2s only make even totals.

Spot it by: "fewest" or "minimum," plus "return -1 if it's impossible." The
min over choices needs a value for "impossible" that loses every comparison.
The -1 is only the output format, so it appears once, at the top.

```python
# shorthand: try each coin as the last one and take the cheapest; impossible returns infinity, converted to -1 only at the top
def coin_change(coins: list[int], amount: int) -> int:  # LC 322
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

Trace of `coin_change([1, 2], 3)`. Coins are tried in order, so coin 1 comes
before coin 2.

    fewest(3)                     miss
      fewest(2)                   via coin 1, miss
        fewest(1)                 via coin 1, miss
          fewest(0)               via coin 1: 0
          fewest(-1)              via coin 2: INF
        fewest(1) = min(0 + 1, INF + 1) = 1       store {1: 1}
        fewest(0)                 via coin 2: 0
      fewest(2) = min(1 + 1, 0 + 1) = 1           store {1: 1, 2: 1}
      fewest(1)                   via coin 2: hit, 1
    fewest(3) = min(1 + 1, 1 + 1) = 2             store {1: 1, 2: 1, 3: 2}

Trace of `coin_change([2], 3)`, where no combination works:

    fewest(3)                     miss
      fewest(1)                   via coin 2, miss
        fewest(-1)                via coin 2: INF
      fewest(1) = INF + 1 = INF                   store {1: INF}
    fewest(3) = INF + 1 = INF                     store {1: INF, 3: INF}
    top level: INF -> return -1

Now replace the INF with -1 inside the recursion. `fewest(1)` becomes
`-1 + 1 = 0`, so `fewest(3)` becomes 1, a wrong answer that claims one coin
pays 3.

Trap: returning -1 inside the recursion makes `sub + 1` equal 0, which then
wins every `min`. Keep "impossible" as a value that loses every comparison.
In Java, `Integer.MAX_VALUE + 1` overflows, so use `amount + 1` as the
sentinel. With a coin of 1, the recursion goes `amount` levels deep, which
passes Python's limit of about 1000.

    Time   O(amount · c)  c = len(coins): each of the amount + 1 values is computed once,
                          trying all c coins
    Space  O(amount)      the memo, and a recursion up to amount deep (with a coin of 1)


## 3. Heaps and ordering

### Heap of tuples — add a tiebreak

Task: merge k sorted arrays into one sorted array.

    input    arrays   k lists, each sorted ascending; any of them may be empty
    output   out      every value from every array, sorted ascending, with duplicates kept

Example: `merge_k_sorted([[1, 4, 5], [1, 3, 4], [2, 6]])` returns
`[1, 1, 2, 3, 4, 4, 5, 6]`.

Spot it by: "merge k sorted lists," or "the smallest item across k sorted
streams." Each output is the smallest of k front elements. A heap of size k
gives you that in O(log k) instead of an O(k) scan.

```python
import heapq

# shorthand: push the first element of each array; pop the smallest, record it, and push the next element from the same array
def merge_k_sorted(arrays: list[list[int]]) -> list[int]:
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

Trace of `merge_k_sorted([[1, 4, 5], [1, 3, 4], [2, 6]])`. Entries are
`(value, array, index)`, and the heap is listed in pop order:

    pop         out                       push        heap after
    -           []                        seed        (1,0,0) (1,1,0) (2,2,0)
    (1,0,0)     [1]                       (4,0,1)     (1,1,0) (2,2,0) (4,0,1)
    (1,1,0)     [1, 1]                    (3,1,1)     (2,2,0) (3,1,1) (4,0,1)
    (2,2,0)     [1, 1, 2]                 (6,2,1)     (3,1,1) (4,0,1) (6,2,1)
    (3,1,1)     [1, 1, 2, 3]              (4,1,2)     (4,0,1) (4,1,2) (6,2,1)
    (4,0,1)     [1, 1, 2, 3, 4]           (5,0,2)     (4,1,2) (5,0,2) (6,2,1)
    (4,1,2)     [1, 1, 2, 3, 4, 4]        array 1 done (5,0,2) (6,2,1)
    (5,0,2)     [1, 1, 2, 3, 4, 4, 5]     array 0 done (6,2,1)
    (6,2,1)     [1, 1, 2, 3, 4, 4, 5, 6]  array 2 done

The heap never holds more than k = 3 entries. The ties on 1 and 4 are broken
by the array number, the second field.

Trap: tuples compare element by element. With `(val, node)`, two equal values
make Python compare the nodes, which raises `TypeError`. An integer second
field breaks every tie first. In Java, use
`new PriorityQueue<int[]>((x, y) -> Integer.compare(x[0], y[0]))`.

    Time   O(N log k)  N = total elements: each is pushed and popped once, and the heap
                       holds at most k entries. Concatenating and sorting is O(N log N)
    Space  O(k)        the heap; out isn't counted

### Max-heap — push the negative

Task: each turn, smash the two heaviest stones together. If they weigh the
same, both are destroyed. Otherwise the lighter one is destroyed, and the
heavier one loses the lighter one's weight and goes back. Repeat until at
most one stone is left.

    input    stones   positive weights
    output   weight   the last stone's weight, or 0 if no stone is left

Example: `last_stone_weight([2, 7, 4, 1, 8, 1])` returns 1. Smashing 8 and 7
leaves 1, then 4 and 2 leave 2, then 2 and 1 leave 1, and then two 1s destroy
each other. One stone of weight 1 is left.

Spot it by: you repeatedly "take the largest" (or the two largest) and
sometimes put something back. That's a max-heap, and Python's `heapq` is
min-only, so you store negatives.

```python
# shorthand: push negatives so the min-heap's smallest is the real largest; negate again when you pop
def last_stone_weight(stones: list[int]) -> int:  # LC 1046
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

Trace of `last_stone_weight([2, 7, 4, 1, 8, 1])`. Stones are shown heaviest
first; the heap actually stores their negatives:

    a  b  result        stones after         heap stores
    -  -  -             [8, 7, 4, 2, 1, 1]   [-8, -7, -4, -2, -1, -1]
    8  7  push 1        [4, 2, 1, 1, 1]      [-4, -2, -1, -1, -1]
    4  2  push 2        [2, 1, 1, 1]         [-2, -1, -1, -1]
    2  1  push 1        [1, 1, 1]            [-1, -1, -1]
    1  1  both gone     [1]                  [-1]
    one stone left: return -heap[0] = 1

Trap: every push negates and every pop negates. Miss one and that value
sorts backwards. In Java, use
`new PriorityQueue<>(Collections.reverseOrder())` instead of negating,
because `-Integer.MIN_VALUE` overflows.

    Time   O(n log n)  n pushes to build the heap; every round removes at least one stone,
                       so at most n - 1 rounds of O(log n) pops and pushes
    Space  O(n)        the heap

### Dijkstra — skip stale entries

Task: in a weighted, one-way graph, return the cheapest total cost from `src`
to every node.

    input    n        number of nodes, labelled 0 .. n-1
             edges    each [u, v, w] is a one-way edge from u to v that costs w >= 0
             src      the start node
    output   dist     dist[v] = cheapest cost from src to v; inf if v can't be reached

The example below is `dijkstra(4, [[0, 1, 4], [0, 2, 1], [2, 1, 2], [1, 3, 1]], 0)`:

    0 --4--> 1 --1--> 3
     \       ^
      1      2
       \     |
        `--> 2

It returns `[0, 3, 1, 4]`. Going to node 1 through node 2 costs 1 + 2 = 3,
which beats the direct edge's 4.

Spot it by: "cheapest," "shortest," or "minimum total cost" path, with
weights that are non-negative and not all equal. If every edge costs the
same, plain BFS is enough. If some weights are negative, use Bellman-Ford.

```python
# shorthand: group edges by start node, seed the heap with (0, src); pop the closest node, skip it if a shorter distance was already found, then relax its edges
def dijkstra(n: int, edges: list[list[int]], src: int) -> list[float]:   # inf where unreachable
    INF = float('inf')
    # 1. group edges by start node: adj[u] = [(v, w), ...]
    adj = []
    for i in range(n):
        adj.append([])
    for i in range(len(edges)):
        adj[edges[i][0]].append((edges[i][1], edges[i][2]))
    # 2. seed: only src is reached, at distance 0
    dist = [INF] * n                   # invariant: dist[v] = shortest distance found so far
    dist[src] = 0
    heap = [(0, src)]
    # 3. pop the closest node, skip it if stale, relax its edges
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

Here is the same loop with Python unpacking, which drops `entry` and `i`.
Only `adj`, `dist` and `heap` last across passes. The other names label the
node just popped and one of its edges. In an interview, write the explicit
form above, because Java has no tuple unpacking.

```python
while heap:
    d, u = heapq.heappop(heap)          # u is reachable for d
    if d > dist[u]:                     # already found cheaper: skip
        continue
    for v, w in adj[u]:                 # each edge u -> v of cost w
        if d + w < dist[v]:             # cheaper to reach v through u?
            dist[v] = d + w
            heapq.heappush(heap, (dist[v], v))
```

Trace of the example. Setup files each `[u, v, w]` as a `(v, w)` pair
under `adj[u]`:

    adj[0]  [(1, 4), (2, 1)]
    adj[1]  [(3, 1)]
    adj[2]  [(1, 2)]
    adj[3]  []

The heap is listed in pop order, smallest first.

    start         dist [0, inf, inf, inf]   heap [(0, 0)]
    pop (0, 0)    0 = dist[0]: current
      0 -> 1      0 + 4 = 4 < inf: dist[1] = 4, push (4, 1)
      0 -> 2      0 + 1 = 1 < inf: dist[2] = 1, push (1, 2)
                  dist [0, 4, 1, inf]       heap [(1, 2), (4, 1)]
    pop (1, 2)    1 = dist[2]: current
      2 -> 1      1 + 2 = 3 < 4: dist[1] = 3, push (3, 1)
                  dist [0, 3, 1, inf]       heap [(3, 1), (4, 1)]
    pop (3, 1)    3 = dist[1]: current
      1 -> 3      3 + 1 = 4 < inf: dist[3] = 4, push (4, 3)
                  dist [0, 3, 1, 4]         heap [(4, 1), (4, 3)]
    pop (4, 1)    4 > dist[1] = 3: stale, skip
    pop (4, 3)    4 = dist[3]: current, no edges out
    heap empty    return [0, 3, 1, 4]

Node 1 is pushed twice, first at 4 and then at 3. The heap can't edit an
entry in place, so `(4, 1)` stays in it until it's popped, and the stale
check throws it away. It pops before `(4, 3)` because the costs tie and the
tuple comparison falls back to the node number.

Trap: BFS treats a node as done when it's pushed, but here the first push
isn't always the cheapest. A node is final only when it's popped. Leaving out
`d > dist[u]` still gives the right answer, but every stale pop rescans its
edges. Negative weights break "final when popped", so use Bellman-Ford for
those. Build `adj` with the loop, not `[[]] * n`, which makes n references to
one list, so every edge lands under every node.

    Time   O((V + E) log E)  V = n nodes, E = edges: each edge pushes at most once, so the
                             heap holds at most E entries and each push or pop is O(log E).
                             Usually written O((V + E) log V), since log E <= 2 log V
    Space  O(V + E)          adj holds every edge, and the heap can hold up to E entries

### Custom sort key — negate to flip one field

Task: sort `[word, count]` pairs by count from high to low, breaking ties
alphabetically.

    input    pairs   [word, count] lists
    output   pairs   the same list, sorted in place: count high to low, then word A to Z

Example: `[["b", 2], ["a", 2], ["c", 5]]` becomes
`[["c", 5], ["a", 2], ["b", 2]]`. The 5 comes first, and the tie on 2 goes
alphabetically.

Spot it by: "sort by X descending, then by Y ascending," meaning two keys
that sort in opposite directions. It shows up in top-k frequent words
(LC 692) and in leaderboards.

```python
# shorthand: sort by a tuple key; negate the number to flip its direction, and leave the tiebreak ascending
def sort_by_count(pairs: list[list[str | int]]) -> list[list[str | int]]:   # each pair is [word, count]
    pairs.sort(key=lambda p: (-p[1], p[0]))   # count descending, then word ascending
    return pairs

assert sort_by_count([["b", 2], ["a", 2], ["c", 5]]) == [["c", 5], ["a", 2], ["b", 2]]
assert sort_by_count([]) == []                     # empty input
```

Trace of `sort_by_count([["b", 2], ["a", 2], ["c", 5]])`. The sort compares
the keys, not the pairs:

    pair        key (-count, word)
    ["b", 2]    (-2, "b")
    ["a", 2]    (-2, "a")
    ["c", 5]    (-5, "c")

    keys sorted ascending   (-5, "c")  (-2, "a")  (-2, "b")
    result                  ["c", 5]   ["a", 2]   ["b", 2]

-5 < -2 puts the bigger count first. The two -2 keys tie on the first field,
so the second field settles it in A to Z order.

Trap: `reverse=True` flips every field, so the tie on 2 comes out `b, a`. You
can't negate a string, so if the string field has to descend, use
`functools.cmp_to_key`. In Java, `(x, y) -> y.count - x.count` overflows for
values far apart. Write `Integer.compare(y.count, x.count)`, then
`x.word.compareTo(y.word)`.

    Time   O(n log n · L)  n log n comparisons; a tie compares two words of length up to L
    Space  O(n)            one key per pair, plus Timsort's working buffer

### Upper bound — < becomes <=

Task: `nums` is sorted. Return the first index whose value is greater than
`target`, and use it to count how many times `target` appears.

    input    nums     sorted ascending, repeats allowed
             target   the value to look up; it doesn't have to be in nums
    output   index    first i with nums[i] > target; len(nums) if there is none

Example: in `[1, 2, 2, 2, 3]`, `upper_bound(nums, 2)` is 4, the index of the
3. `lower_bound(nums, 2)` is 1, the first 2, so 2 appears 4 - 1 = 3 times.

Spot it by: on sorted input, "count the occurrences of," "the last position
of," or "the first element greater than." Lower bound finds the first index
with a value >= target, upper bound finds the first with a value > target,
and the gap between them is the run of target.

```python
# shorthand: same as lower bound, but move right past mid while it's <= target
def lower_bound(nums: list[int], target: int) -> int:
    lo = 0
    hi = len(nums)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def upper_bound(nums: list[int], target: int) -> int:
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

Trace of both bounds on `[1, 2, 2, 2, 3]` with target 2:

    bound  lo  hi  mid  nums[mid]  test            move
    upper  0   5   2    2          2 <= 2          lo = 3
    upper  3   5   4    3          3 <= 2? no      hi = 4
    upper  3   4   3    2          2 <= 2          lo = 4
    upper  4   4   -    -          lo == hi        return 4
    lower  0   5   2    2          2 < 2? no       hi = 2
    lower  0   2   1    2          2 < 2? no       hi = 1
    lower  0   1   0    1          1 < 2           lo = 1
    lower  1   1   -    -          lo == hi        return 1

On a 2, upper moves right past it and lower keeps it as a candidate. That one
comparison is the whole difference.

Trap: the last occurrence is `upper_bound - 1`, which may hold a smaller value
or be -1. Check `nums[idx] == target` before trusting it (LC 34). Everything
else is the lower bound template. Change only the comparison.

    Time   O(log n)  each iteration halves hi - lo; a count is two searches, still O(log n),
                     where scanning the run of target would be O(n)
    Space  O(1)      lo, hi, mid

### Overlap test — each starts before the other ends

Task: return whether two half-open intervals `[start, end)` overlap.
Half-open means the interval includes `start` but not `end`.

    input    a, b      intervals as [start, end]
    output   overlap   True if some point lies inside both

Example: `[1, 5)` and `[4, 8)` overlap, because 4 is in both. `[1, 3)` and
`[3, 5)` don't, because 3 isn't in `[1, 3)`.

Spot it by: any question about whether two intervals, bookings, or meetings
conflict. It's the check inside meeting rooms (LC 252), calendar booking
(LC 729), and interval merging.

```python
# shorthand: two intervals overlap when each one starts before the other ends
def overlaps(a: list[int], b: list[int]) -> bool:
    return a[0] < b[1] and b[0] < a[1]

assert overlaps([1, 5], [4, 8]) is True
assert overlaps([1, 10], [3, 4]) is True           # nested: b's start is inside a, a's start isn't inside b
assert overlaps([1, 3], [3, 5]) is False           # touching: [1, 3) ends where [3, 5) starts
assert overlaps([4, 8], [1, 5]) is True            # argument order doesn't matter
```

Trace of the four asserts:

    a        b       a[0] < b[1]   b[0] < a[1]   overlap
    [1, 5]   [4, 8]  1 < 8 yes     4 < 5 yes     True
    [1, 10]  [3, 4]  1 < 4 yes     3 < 10 yes    True     nested
    [1, 3]   [3, 5]  1 < 5 yes     3 < 3 no      False    touching
    [4, 8]   [1, 5]  4 < 5 yes     1 < 8 yes     True     same as row 1, swapped

Row 2 is the one the one-sided test gets wrong: 1 is not inside `[3, 4)`, yet
the intervals overlap.

Trap: "a's start is inside b" misses the nested case. The two-condition form
covers every arrangement. Closed intervals, where touching counts, use `<=`.
That's why merge intervals (LC 56) tests `iv[0] <= merged[-1][1]`.

    Time   O(1)  two comparisons
    Space  O(1)

### Sort by end — keep the earliest finisher

Task: return the fewest intervals to remove so the rest don't overlap.
Touching intervals, like `[1, 2]` and `[2, 3]`, don't count as overlapping.

    input    intervals   [start, end] pairs, in any order
    output   removed     fewest intervals to delete so that no two of the rest overlap

Example: `erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]])` returns 1.
Delete `[1, 3]`, and the other three only touch.

Spot it by: "fewest to remove so none overlap," "the most non-overlapping
intervals," or "the minimum number of arrows." You're choosing a subset of
intervals, and always keeping the one that finishes first is the greedy you
can prove safe.

```python
# shorthand: sort by end, keep each interval that starts at or after the last kept end, count the rest as removed
def erase_overlap_intervals(intervals: list[list[int]]) -> int:  # LC 435
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

Trace of `erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]])`. After
sorting by end: `[[1, 2], [2, 3], [1, 3], [3, 4]]`.

    interval  start >= end?    action   end after  removed
    [1, 2]    1 >= -inf        keep     2          0
    [2, 3]    2 >= 2           keep     3          0       touching is allowed
    [1, 3]    1 >= 3? no       remove   3          1
    [3, 4]    3 >= 3           keep     4          1

For the second assert, sorting by end gives `[[2, 3], [3, 4], [1, 100]]`:
keep, keep, remove. Sorting by start would keep `[1, 100]` first and then
have to remove both short ones.

Trap: when you're choosing intervals, sort by end. The interval that finishes
first leaves the most room for the rest. Merging (LC 56) sorts by start
because it combines intervals instead of choosing among them. The same loop
counts the minimum arrows to burst balloons (LC 452), with `>` for closed
intervals.

    Time   O(n log n)  the sort dominates; the scan after it is O(n)
    Space  O(n)        sorted() makes a copy; sorting in place would leave Timsort's buffer


## 4. Bits

### Get, set, clear, toggle — parenthesize everything

Task: read, set, clear, and flip bit i of x.

    input    x        a non-negative integer
             i        a bit position; 0 is the lowest bit (the 1s place)
    output   get      0 or 1, the value of bit i
             set      x with bit i forced to 1
             clear    x with bit i forced to 0
             toggle   x with bit i flipped

Example: 10 is `0b1010`. Bit 1 is 1 and bit 0 is 0. Setting bit 0 gives
`0b1011`, which is 11.

Spot it by: a set of yes/no flags stored in one integer. Bitmask subsets
(`docs/array_warmup.md` section 6), visited sets in bitmask DP, and
permission flags all read and write single bits.

```python
# shorthand: shift a 1 to position i, then AND to test, OR to set, AND with its complement to clear, XOR to flip
def get_bit(x: int, i: int) -> int:   # 0 or 1
    return (x >> i) & 1

def set_bit(x: int, i: int) -> int:
    return x | (1 << i)

def clear_bit(x: int, i: int) -> int:
    return x & ~(1 << i)

def toggle_bit(x: int, i: int) -> int:
    return x ^ (1 << i)

x = 0b1010                             # 10
assert get_bit(x, 1) == 1
assert get_bit(x, 0) == 0
assert set_bit(x, 0) == 0b1011
assert clear_bit(x, 3) == 0b0010
assert toggle_bit(x, 1) == 0b1000
assert set_bit(x, 1) == x                          # already set: no change
```

Trace on `x = 0b1010` (10):

    call              mask (1 << i)   operation                      result
    get_bit(x, 1)     -               x >> 1 = 0b101, & 1            1
    get_bit(x, 0)     -               x >> 0 = 0b1010, & 1           0
    set_bit(x, 0)     0b0001          0b1010 | 0b0001                0b1011  (11)
    clear_bit(x, 3)   0b1000          0b1010 & ~0b1000 = & ...0111   0b0010  (2)
    toggle_bit(x, 1)  0b0010          0b1010 ^ 0b0010                0b1000  (8)

The mask has a single 1 in position i. OR forces that bit on, AND with the
inverted mask forces it off, and XOR flips it. The other bits pass through
unchanged.

Trap: in Java and C++, `==` binds tighter than `&`, so `x & 1 << i == 0`
parses as `x & ((1 << i) == 0)`. Python parses it the other way, which hides
the bug. Parenthesize every bit expression. In Java, `1 << 31` is negative and
`1 << 32` wraps to 1, so use `1L << i` for 64-bit masks.

    Time   O(1)  one shift and one logical operation on a fixed-width word
    Space  O(1)

### Clear the lowest set bit — x & (x - 1)

Task: count the 1 bits in x, and test whether x is a power of two.

    input    x                  a non-negative integer
    output   count_bits         how many 1s are in x's binary form
             is_power_of_two    True if x is 1, 2, 4, 8, ...; these have exactly one 1 bit

Example: 11 is `0b1011`, so `count_bits(11)` is 3. 16 is `0b10000`, which has
a single 1 bit, so it's a power of two.

Spot it by: "number of 1 bits," "power of two," or a loop that should run
once per set bit rather than once per bit position.

```python
# shorthand: x & (x - 1) removes the lowest 1 bit; count how many removals it takes to reach 0
def count_bits(x: int) -> int:  # LC 191, x >= 0
    count = 0
    while x != 0:                      # invariant: count = 1 bits already removed from x
        x = x & (x - 1)
        count += 1
    return count

def is_power_of_two(x: int) -> bool:  # LC 231
    return x > 0 and (x & (x - 1)) == 0

assert count_bits(0b1011) == 3
assert count_bits(0) == 0                          # zero: no bits to remove
assert is_power_of_two(16) is True
assert is_power_of_two(6) is False
assert is_power_of_two(0) is False                 # zero: 0 & -1 == 0, so the x > 0 guard is needed
```

Trace of `count_bits(0b1011)`:

    x      x - 1   x & (x - 1)   count
    1011   1010    1010          1
    1010   1001    1000          2
    1000   0111    0000          3      x is 0: stop

And `is_power_of_two`: 16 is `10000`, and `10000 & 01111 = 0`, so True. 6 is
`110`, and `110 & 101 = 100`, which isn't 0, so False.

Each row removes exactly one 1, so the loop runs 3 times for 3 bits, not 4
times for 4 positions.

Trap: `x - 1` flips the lowest 1 to 0 and every 0 below it to 1, so the AND
clears exactly that bit. Python integers have unbounded sign bits, so a
negative x loops forever. Mask it first with `x & 0xFFFFFFFF`. In Java, use
`Integer.bitCount`, or shift with `>>>`.

    Time   O(b)  b = number of 1 bits, at most 32 for a 32-bit int. Testing every
                 position is always 32. is_power_of_two is O(1)
    Space  O(1)

### Isolate the lowest set bit — x & -x

Task: return the value of x's lowest 1 bit.

    input    x       a non-negative integer
    output   value   the lowest 1 bit as a number, which is a power of two, not its
                     position; 0 if x is 0

Example: 12 is `0b1100`. Its lowest 1 bit is `0b0100`, so `lowest_bit(12)` is
4, not the position 2.

Spot it by: you need the lowest set bit as a number. Splitting values into
two groups by one differing bit (LC 260), stepping through a Fenwick tree,
and visiting set bits one at a time all use it.

```python
# shorthand: -x flips every bit above the lowest 1 and keeps that 1, so x & -x leaves only it
def lowest_bit(x: int) -> int:         # x > 0
    return x & -x

assert lowest_bit(0b1100) == 0b0100
assert lowest_bit(7) == 1
assert lowest_bit(8) == 8                          # power of two: the bit is the number
assert lowest_bit(0) == 0                          # zero: no bit to isolate
```

Trace of `lowest_bit(12)`, in 8 bits:

    x            0000 1100    12
    ~x           1111 0011    every bit flipped
    -x = ~x + 1  1111 0100    the +1 carries through the two 1s and stops at bit 2
    x & -x       0000 0100    4

Above bit 2, `x` and `-x` are opposites, so the AND is 0 there. Below it,
both are 0. Only bit 2 is 1 in both.

Trap: two's complement makes `-x == ~x + 1`. The `+ 1` carries up to the
lowest 1 bit, and everything above it is inverted. Use it to split numbers
into two groups by one differing bit (LC 260). It's also the index step in a
Fenwick tree.

    Time   O(1)  one negation and one AND
    Space  O(1)


## 5. Tries

### Insert / search — the end flag

Task: build a prefix tree, a tree that stores words one character per level,
so words with the same start share a path.

    insert(word)          store word; returns nothing
    search(word)          True if word itself was inserted
    starts_with(prefix)   True if any inserted word begins with prefix

Example: after `insert("apple")`, `search("app")` is False because "app" was
never inserted, but `starts_with("app")` is True.

Spot it by: many words that share prefixes, with queries by prefix:
autocomplete, "starts with," word search on a board (LC 212), or replacing
words with their shortest root (LC 648). A hash set answers "is this a
word?" but not "is this the start of a word?"

```python
# shorthand: walk one child per character, creating missing ones on insert; a word ends only where the flag is set
class TrieNode:
    def __init__(self):
        self.children = {}             # char -> TrieNode
        self.is_end = False            # a word ends here, rather than just passing through

class Trie:  # LC 208
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for i in range(len(word)):
            c = word[i]
            if c not in node.children:
                node.children[c] = TrieNode()
            node = node.children[c]
        node.is_end = True

    def walk(self, s: str) -> TrieNode | None:   # the node that s leads to, or None
        node = self.root
        for i in range(len(s)):
            c = s[i]
            if c not in node.children:
                return None
            node = node.children[c]
        return node

    def search(self, word: str) -> bool:
        node = self.walk(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
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

Trace of the asserts. After `insert("apple")`, the trie is one chain, with
`*` marking `is_end`:

    root -a-> . -p-> . -p-> . -l-> . -e-> *

    call                  walk                         result
    insert("apple")       creates a, p, p, l, e        marks the e node
    search("apple")       a p p l e: reaches e node    is_end True: True
    search("app")         a p p: reaches 2nd p node    is_end False: False
    starts_with("app")    a p p: reaches 2nd p node    node exists: True
    insert("app")         a p p: all exist already     marks the 2nd p node
    search("app")         a p p: reaches 2nd p node    is_end True: True
    starts_with("")       no steps: stays at root      node exists: True

The second insert creates no nodes. "app" and "apple" share all three, and
only the flag tells them apart.

Trap: without `is_end`, `search` returns `True` for every prefix of every
word. `search` and `starts_with` share the walk and differ only in that flag.
In Java, use `TrieNode[] children = new TrieNode[26]` and index with
`c - 'a'`.

    Time   O(L)  per call, L = length of the word or prefix: one child step per
                 character, no matter how many words are stored
    Space  O(C)  C = total characters inserted, in the worst case where no prefixes
                 are shared; each node is a dict (or a 26-slot array in Java)


## 6. Counting

### n choose k — multiply, then divide

Task: return C(n, k), the number of ways to choose k items from n when order
doesn't matter, without computing any factorial.

    input    n        how many items there are
             k        how many to choose
    output   result   C(n, k); 0 if k < 0 or k > n

Example: `n_choose_k(5, 2)` returns 10, because 5 people can form 10
different pairs.

Spot it by: a count that turns out to be a binomial coefficient: grid paths
(C(m+n-2, m-1)), ways to choose k of n, or a row of Pascal's triangle.
Factorials overflow long before the answer does, so build the value up a
step at a time.

```python
# shorthand: multiply by the next top factor, then divide by the next bottom factor; every step stays an exact integer
def n_choose_k(n: int, k: int) -> int:
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

Trace of `n_choose_k(5, 2)`. k = 2 is already the smaller side (n - k = 3):

    i  factor n - k + i  result * factor  // i  result = C(n - k + i, i)
    1  4                 1 * 4 = 4        4     C(4, 1) = 4
    2  5                 4 * 5 = 20       10    C(5, 2) = 10

The product before each division is i times a binomial, so it always divides
evenly: 4 / 1 and 20 / 2. The broken version divides 5 // 2 first and loses
the half.

Trap: the order is the idiom. `result * (n - k + i)` equals `i * C(n - k + i, i)`,
so dividing that product by `i` is exact. Dividing `(n - k + i) // i` first
truncates. The factorial formula `n! / (k! (n - k)!)` overflows a Java `long`
from 21! on, even when the answer is small. If the answer must be taken mod
1e9+7, the division doesn't work under the mod. Use Pascal's rule
`C(n, k) = C(n-1, k-1) + C(n-1, k)` in a DP table instead.

    Time   O(min(k, n - k))  one multiply and one divide per step, after the k = n - k swap
    Space  O(1)              result and i (a Java long, until the answer itself overflows)
