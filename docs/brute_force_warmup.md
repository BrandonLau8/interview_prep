# Brute force warmup

This file has one short, runnable pair for each brute force listed in
`docs/tells.md` ("If you can't find a tell"): the brute force, then the fix
its wasted work points to. Each block ends with `assert`s that both versions
must pass, so you can paste it into `main.py` and run it.

Assumes you know: section 0 of `docs/array_warmup.md`, and "Memo check
first" in `docs/search_warmup.md`.
Not covered: how each fix works in depth. The `Fix:` line under each block
names the warmup section that drills it. For full-size brute forces on real
LeetCode problems, see `pattern_code/19_fallbacks.py`.

How to use it: read the task, write the brute force first, and say out loud
which line repeats work. Then write the fix from memory and run the asserts
against both. The "Waste" line is the sentence an interviewer wants to hear
between the two: it names what the brute force recomputes and what stops it.

    wasted work                            fix                            the one trap

    1. Arrays
    nested loop over all pairs             hash map, or opposite ends     check the map before inserting j
    re-summing the same range              prefix with sentinel           pre[r + 1] - pre[l], not pre[r]
    rescanning to the right for each i     monotonic stack                break on the first hit in the brute
    re-finding the max of each window      monotonic deque                range(n - k + 1): the last window counts
    re-sorting after each insert           heap of size k                 min-heap for the k largest
    recomputing the same subproblem        memo check first               store before returning
    trying every value of the answer       binary search on the answer    can(x) must flip exactly once
    checking every subarray                variable-size window           decrement before moving left
    scanning a list to test membership     set                            x in list is a hidden loop
    comparing every pair of intervals      sort by start                  compare to the previous end only
    simulating every jump                  greedy scan                    check i > farthest before reading nums[i]

    2. Strings
    sorting two strings to compare them    letter counts                  length check first
    checking every substring is a          expand around center           2n - 1 centers: even ones too
      palindrome
    recursion over two strings             DP table                       dp index i is string index i - 1

    3. Lists, trees, graphs
    walking the list twice                 gap pointers                   start both at the dummy
    recomputing height at every node       return up, with a sentinel     check -1 before using a height
    a fresh search from every node         mark before you recurse        one visited array for all starts

The names follow `docs/array_warmup.md`, plus:

    _brute        suffix on the brute force; the fix has the bare name
    need          the value that would complete a pair
    queries       a list of [l, r] ranges, inclusive
    dq            a deque of indices, front = current window max
    heap          a heapq min-heap
    memo          computed answers: argument -> result
    d             a candidate answer being checked
    seen          values already passed: a list in the brute, a set in the fix
    ordered       the intervals sorted by start
    reach         reach[i] = index i is reachable (brute)
    farthest      the largest index known to be reachable (fix)
    counts        int[26] letter tally: +1 for s, -1 for t
    dp            dp[i][j] = the answer for a[0:i] and b[0:j]
    dummy         a node before the head, so removing the head is not a special case
    fast, slow    two pointers into a list, fast k nodes ahead
    node          a tree node; None is the empty tree
    adj           adjacency list: adj[u] = neighbours of u
    visited       visited[v] = v is already in a counted component


## 1. Arrays

### Nested loop over all pairs — remember what you've seen

Task: return indices `[i, j]`, i < j, whose values add up to `target`, or
`[]` if no pair does.

Waste: for each j, the inner loop rescans `nums[0:j]` looking for one value,
`target - nums[j]`. A map from value to index answers "have I seen it?" in
O(1), so the inner loop goes away.

```python
# shorthand: for each element, compare it with every element after it
def pair_with_sum_brute(nums, target):
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):      # waste: rescans values already passed
            if nums[i] + nums[j] == target:
                return [i, j]
    return []

# shorthand: for each element, look up the value it needs among earlier elements, then record it
def pair_with_sum(nums, target):  # LC 1
    n = len(nums)
    seen = {}                          # invariant: seen[v] = an index of v in nums[0:j]
    for j in range(n):
        need = target - nums[j]
        if need in seen:
            return [seen[need], j]
        seen[nums[j]] = j              # insert after the check: j never pairs with itself
    return []

for f in [pair_with_sum_brute, pair_with_sum]:
    assert f([2, 7, 11, 15], 9) == [0, 1]
    assert f([3, 2, 4], 6) == [1, 2]               # 3 + 3 = 6: index 0 must not pair with itself
    assert f([3, 3], 6) == [0, 1]                  # duplicate values: two different indices
    assert f([3], 6) == []                         # single element: no pair
```

Trap: inserting `nums[j]` before the check finds `need` at j itself, so
`[3, 2, 4]` returns `[0, 0]`. If the input is sorted, opposite ends gives the
same O(n) time in O(1) space, but it returns positions in the sorted order,
not the original indices.

    brute  O(n²) time, O(1) space   n(n-1)/2 pairs
    fix    O(n) time, O(n) space    one lookup and one insert per element

Fix: Hash map, LC 1 (`array_warmup.md` section 4); Opposite ends, LC 167
(section 1). Fallback: `pattern_code/19_fallbacks.py:568`.

### Re-summing the same range — pay for the prefix once

Task: `queries[q] = [l, r]`. Return the sum of `nums[l..r]`, inclusive, for
every query.

Waste: overlapping queries add up the same elements again. A prefix array
pays for every running sum once, and each query becomes one subtraction.

```python
# shorthand: for each query, add up the elements from l to r
def range_sums_brute(nums, queries):
    out = []
    for q in range(len(queries)):
        l = queries[q][0]
        r = queries[q][1]
        total = 0
        for i in range(l, r + 1):      # waste: re-adds elements earlier queries summed
            total += nums[i]
        out.append(total)
    return out

# shorthand: build the prefix once, then answer each query with one subtraction
def range_sums(nums, queries):  # LC 303
    n = len(nums)
    pre = [0] * (n + 1)                # invariant: pre[i] = sum(nums[0:i])
    for i in range(n):
        pre[i + 1] = pre[i] + nums[i]
    out = []
    for q in range(len(queries)):
        l = queries[q][0]
        r = queries[q][1]
        out.append(pre[r + 1] - pre[l])
    return out

for f in [range_sums_brute, range_sums]:
    assert f([2, 4, 1, 3], [[1, 2], [0, 3]]) == [5, 10]
    assert f([2, 4, 1, 3], [[2, 2]]) == [1]        # l == r: a one-element range
    assert f([2, 4, 1, 3], [[0, 0]]) == [2]        # l = 0: pre[0] = 0 removes the special case
    assert f([2, 4, 1, 3], []) == []               # no queries
```

Trap: `pre[r] - pre[l]` drops `nums[r]`, which the `[2, 2]` assert catches
by returning 0. In Java/C++, make `pre` a `long[]`: each slot is a sum of up
to n values.

    brute  O(q·n) time, O(1) space    each query walks up to n elements
    fix    O(n + q) time, O(n) space  one build, then O(1) per query

Fix: Prefix with sentinel (`array_warmup.md` section 0); Prefix sum + map,
LC 560 (section 3), when the question is "how many ranges" instead of "what
sum."

### Rescanning to the right — let the right side answer you

Task: for each element, return the first value to its right that is strictly
bigger, or -1 if there isn't one.

Waste: on a falling array, every i scans the whole rest of the array and
finds nothing. The stack flips the direction: each new element answers every
waiting element it beats, and an element waits only once.

```python
# shorthand: for each element, scan right until something is bigger
def next_greater_brute(nums):
    n = len(nums)
    out = [-1] * n
    for i in range(n):
        for j in range(i + 1, n):      # waste: rescans the same suffix for every i
            if nums[j] > nums[i]:
                out[i] = nums[j]
                break                  # first bigger, not last
    return out

# shorthand: pop every waiting element the current element beats, write it as their answer, then push the current element
def next_greater(nums):
    n = len(nums)
    out = [-1] * n
    stack = []                         # invariant: indices still waiting, values non-increasing bottom to top
    for i in range(n):
        while len(stack) > 0 and nums[stack[-1]] < nums[i]:
            j = stack.pop()
            out[j] = nums[i]
        stack.append(i)
    return out

for f in [next_greater_brute, next_greater]:
    assert f([2, 1, 3, 2, 4]) == [3, 3, 4, 4, -1]
    assert f([5, 4, 3]) == [-1, -1, -1]            # strictly falling: the brute's worst case, the stack never pops
    assert f([3, 3]) == [-1, -1]                   # equal values: strictly bigger only
    assert f([]) == []                             # empty input
```

Trap: without the `break`, the brute records the last bigger value, not the
first. When the question is "the largest value anywhere to the right" rather
than "the first bigger one," the stack is overkill: a right-to-left pass with
a running max answers it.

    brute  O(n²) time, O(1) space  a falling array scans n - 1 + n - 2 + ... elements
    fix    O(n) time, O(n) space   each index is pushed once and popped at most once

Fix: Monotonic stack, LC 739 (`array_warmup.md` section 4); Right-to-left
pass (section 0). Fallback: `pattern_code/19_fallbacks.py:462`.

### Re-finding the max of each window — keep only the candidates

Task: a window of size `k` slides across `nums`. Return the maximum inside
the window at each position.

Waste: neighbouring windows share k - 1 elements, and the brute force
re-examines all of them. A running max can't "un-max" the element that
leaves, so the fix keeps every element that could still become the max, in
a deque.

```python
# shorthand: for each window start, scan the k elements and record the max
def window_max_brute(nums, k):
    n = len(nums)
    out = []
    for start in range(n - k + 1):     # + 1: the last window starts at n - k
        best = nums[start]
        for i in range(start + 1, start + k):      # waste: k - 1 of these were in the last window
            best = max(best, nums[i])
        out.append(best)
    return out

from collections import deque

# shorthand: drop the front if it left the window, pop smaller values off the back, push the current index, record the front
def window_max(nums, k):  # LC 239
    n = len(nums)
    dq = deque()                       # invariant: indices in the window, values decreasing front to back
    out = []
    for i in range(n):
        if len(dq) > 0 and dq[0] <= i - k:
            dq.popleft()               # front fell out of the window
        while len(dq) > 0 and nums[dq[-1]] <= nums[i]:
            dq.pop()                   # can never be a max while nums[i] is in the window
        dq.append(i)
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out

for f in [window_max_brute, window_max]:
    assert f([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
    assert f([4, 2, 7], 1) == [4, 2, 7]            # k = 1: each element is its own window
    assert f([4, 2, 7], 3) == [7]                  # k == n: exactly one window
    assert f([9, 8, 7, 6], 2) == [9, 8, 7]         # falling: the max always leaves through the front
```

Trap: `range(n - k)` in the brute drops the last window. In the fix, evict
by index (`dq[0] <= i - k`), not by value: two equal values in the window
are different elements.

    brute  O(n·k) time, O(1) space  n - k + 1 windows, k elements each
    fix    O(n) time, O(k) space    each index enters and leaves the deque once

Fix: Monotonic deque, LC 239 (`array_warmup.md` section 4); Fixed-size
window (section 0) for the `i - k` eviction.

### Re-sorting after each insert — keep a heap of size k

Task: numbers arrive one at a time. Once at least `k` have arrived, record the
k-th largest so far after each arrival.

Waste: everything already seen is in order, and the sort reorders all of it
to place one new number. Worse, only the top k ever matter. A min-heap holds
exactly those k, and its top is the k-th largest.

```python
# shorthand: append the number, sort everything, read k from the end
def kth_largest_stream_brute(nums, k):
    n = len(nums)
    seen = []
    out = []
    for i in range(n):
        seen.append(nums[i])
        seen.sort()                    # waste: re-sorts values that were already in order
        if len(seen) >= k:
            out.append(seen[len(seen) - k])
    return out

import heapq

# shorthand: push the number, pop the smallest if there are more than k, record the top
def kth_largest_stream(nums, k):  # LC 703
    n = len(nums)
    heap = []                          # invariant: the k largest of nums[0:i+1], smallest on top
    out = []
    for i in range(n):
        heapq.heappush(heap, nums[i])
        if len(heap) > k:
            heapq.heappop(heap)        # it has k bigger values: it can never be the k-th largest again
        if len(heap) == k:
            out.append(heap[0])
    return out

for f in [kth_largest_stream_brute, kth_largest_stream]:
    assert f([4, 5, 8, 2, 3, 5, 10], 3) == [4, 4, 4, 5, 5]
    assert f([3, 1, 2], 1) == [3, 3, 3]            # k = 1: the running max
    assert f([5, 5, 5], 2) == [5, 5]               # duplicates: each copy is its own entry
    assert f([1, 2], 3) == []                      # fewer than k arrivals: nothing to record
```

Trap: the k largest live in a min-heap, not a max-heap. The heap's job is to
throw out the smallest of its k + 1 values, so the smallest has to be on top.
Pop when the size passes k, and record only once it equals k.

    brute  O(n² log n) time, O(n) space  n sorts of up to n values
    fix    O(n log k) time, O(k) space   one push and at most one pop per arrival, on k values

Fix: Heap, LC 215 (`array_warmup.md` section 4); Max-heap
(`search_warmup.md` section 3) when the question flips to the k smallest.
Fallback: `pattern_code/19_fallbacks.py:344`.

### Recomputing the same subproblem — look it up first

Task: you climb n steps, taking 1, 2, or 3 at a time. Return the number of
distinct ways to reach the top.

Waste: `ways(5)` calls `ways(4)`, `ways(3)`, `ways(2)`, and `ways(4)` calls
`ways(3)` and `ways(2)` again. The brute force rebuilds each of those
subtrees every time. There are only n + 1 distinct arguments, so storing each
answer once makes every repeat a lookup.

```python
# shorthand: the ways to climb i are the ways from i - 1, i - 2, and i - 3, added up
def climb_three_brute(n):
    if n < 0:
        return 0                       # overshot: not a way
    if n == 0:
        return 1                       # landed exactly: one way
    return climb_three_brute(n - 1) + climb_three_brute(n - 2) + climb_three_brute(n - 3)   # waste: same n, recomputed

# shorthand: return the stored answer if there is one; otherwise compute it, store it, and return it
def climb_three(n):  # LC 1137 shape
    memo = {}                          # invariant: memo[i] = ways to climb i steps, once computed
    def ways(i):
        if i < 0:
            return 0
        if i == 0:
            return 1
        if i in memo:
            return memo[i]
        result = ways(i - 1) + ways(i - 2) + ways(i - 3)
        memo[i] = result               # store before returning
        return result
    return ways(n)

for f in [climb_three_brute, climb_three]:
    assert f(3) == 4                               # 1+1+1, 1+2, 2+1, 3
    assert f(4) == 7
    assert f(0) == 1                               # zero steps: one way, which is doing nothing
    assert f(1) == 1                               # i - 2 and i - 3 go negative: the n < 0 base case
assert climb_three(60) == 4680045560037375         # the brute force would make about 10^16 calls here
```

Trap: the `n < 0` base case has to exist, or `ways(1)` calls `ways(-2)` and
recurses forever. Create `memo` inside the wrapper, never as a
`memo={}` default. In Java, the last answer needs a `long`.

    brute  O(3^n) time, O(n) space  each call branches three ways; the stack is n deep
    fix    O(n) time, O(n) space    each ways(i) computed once, O(1) work, n + 1 memo entries

Fix: Memo check first, LC 70 (`search_warmup.md` section 2); DP over
indices, LC 198 (`array_warmup.md` section 6) to drop the recursion.
Fallback: `pattern_code/19_fallbacks.py:319`.

### Trying every value of the answer — binary search the flip

Task: pick a positive divisor `d`, divide every element of `nums` by it, and
round each result up. Return the smallest `d` whose rounded results add up
to at most `threshold`. `threshold >= len(nums)`, so `d = max(nums)` always
works.

Waste: the brute force checks d = 1, 2, 3, ... in order. But the check goes
false, false, ..., true, true: a bigger divisor never makes the total larger.
One check at the middle rules out half the range.

```python
def total_after(nums, d):              # monotone: bigger d never raises the total
    n = len(nums)
    total = 0
    for i in range(n):
        total += (nums[i] + d - 1) // d            # ceil division
    return total

# shorthand: try each divisor from 1 upward until the total fits
def smallest_divisor_brute(nums, threshold):
    d = 1
    while total_after(nums, d) > threshold:        # waste: one check per candidate, in order
        d += 1
    return d

# shorthand: check the middle divisor; if it fits, keep it and look left, otherwise move right past it
def smallest_divisor(nums, threshold):  # LC 1283
    lo = 1
    hi = max(nums)                     # invariant: the answer is in [lo, hi]; hi always fits
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if total_after(nums, mid) <= threshold:
            hi = mid                   # mid fits: it might be the answer, keep it
        else:
            lo = mid + 1               # mid is too small: the answer is to its right
    return lo

for f in [smallest_divisor_brute, smallest_divisor]:
    assert f([1, 2, 5, 9], 6) == 5
    assert f([2, 3, 5, 7, 11], 11) == 3
    assert f([44, 22, 33, 11, 1], 5) == 44         # threshold == n: only max(nums) fits, hi must include it
    assert f([4, 9], 100) == 1                     # huge threshold: d = 1 already fits
```

Trap: binary search on the answer is only valid because `total_after` is
monotone in d. If a larger value could fail after a smaller one works, the
search skips answers. `hi` starts at a value known to fit, not one past it.
In Java, `nums[i] + d - 1` can overflow `int`, so write
`(nums[i] - 1) / d + 1` or use `long`.

    brute  O(n·M) time, O(1) space      M = max(nums): up to M checks of n elements
    fix    O(n log M) time, O(1) space  about log2(M) checks

Fix: Binary search on the answer, LC 875 (`array_warmup.md` section 5);
Lower bound (section 0) for the `lo < hi` / `hi = mid` template.

### Checking every subarray — grow and shrink one window

Task: return the length of the longest substring of `s` with no repeated
character.

Waste: when start i hits a repeat at j, start i + 1 rebuilds the set for
`s[i+1..j-1]`, which it already knows is repeat-free. A window keeps that
set and only drops characters off the left until the repeat is gone.

```python
# shorthand: for each start, extend right until a character repeats, record the length
def longest_unique_brute(s):
    n = len(s)
    best = 0
    for i in range(n):
        seen = set()
        for j in range(i, n):          # waste: re-adds characters the last start already checked
            if s[j] in seen:
                break
            seen.add(s[j])
            best = max(best, j - i + 1)
    return best

# shorthand: add the right character, drop characters from the left while it repeats, record the length
def longest_unique(s):  # LC 3
    n = len(s)
    freq = {}                          # invariant: freq = counts in s[left:right+1], no zero entries
    left = 0
    best = 0
    for right in range(n):
        if s[right] in freq:
            freq[s[right]] += 1
        else:
            freq[s[right]] = 1
        while freq[s[right]] > 1:      # invalid: s[right] repeats
            freq[s[left]] -= 1
            if freq[s[left]] == 0:
                del freq[s[left]]
            left += 1
        best = max(best, right - left + 1)
    return best

for f in [longest_unique_brute, longest_unique]:
    assert f("abcabcbb") == 3
    assert f("pwwkew") == 3                        # the answer "wke" starts after the repeat
    assert f("bbbbb") == 1                         # every character repeats
    assert f("abba") == 2                          # a last-seen map would jump left backwards here
    assert f("") == 0                              # empty input
```

Trap: decrement `freq[s[left]]` before `left += 1`, or you drop the wrong
character. If you write the faster last-seen version instead
(`left = last[c] + 1`), take `max(left, last[c] + 1)`: on "abba", the second
`a`'s last index is behind `left`, and jumping back re-admits the `b`s.

    brute  O(n²) time, O(k) space  n starts, each extending up to k distinct characters
    fix    O(n) time, O(k) space   left and right each move forward at most n times

Fix: Window with counts (`array_warmup.md` section 0); Sliding window,
LC 209 (section 1). Precondition: the window only works when shrinking can
restore validity, which fails for sums with negative values (`tells.md`,
"When the tell lies"). Fallback: `pattern_code/19_fallbacks.py:80`.

### Scanning a list to test membership — use a set

Task: return True if any value appears at least twice in `nums`.

Waste: `x in seen` on a list walks the whole list, so the "one loop" brute
force is really two. A set answers the same question in O(1) on average. The
code is the same; only the container changes.

```python
# shorthand: for each element, look for it among the earlier ones, then remember it
def has_duplicate_brute(nums):
    n = len(nums)
    seen = []
    for i in range(n):
        if nums[i] in seen:            # waste: `in` on a list is a hidden loop over seen
            return True
        seen.append(nums[i])
    return False

# shorthand: same loop, but remember values in a set
def has_duplicate(nums):  # LC 217
    n = len(nums)
    seen = set()                       # invariant: seen = the values in nums[0:i]
    for i in range(n):
        if nums[i] in seen:
            return True
        seen.add(nums[i])
    return False

for f in [has_duplicate_brute, has_duplicate]:
    assert f([1, 2, 3, 1]) == True
    assert f([1, 2, 3]) == False
    assert f([0, 0]) == True                       # duplicate at the very start
    assert f([]) == False                          # empty input
```

Trap: the brute force reads as O(n) and isn't. Say the cost of every `in`
out loud: list O(n), set and dict O(1) average. In Java, it's
`ArrayList.contains` versus `HashSet.contains`. If O(1) extra space is
required, sort first and compare neighbours, for O(n log n).

    brute  O(n²) time, O(n) space        i lookups of up to i elements each
    fix    O(n) time, O(n) space         one O(1) lookup and one insert per element

Fix: Frequency count (`array_warmup.md` section 0); Adjacent pairs
(section 0) for the sort-first version.

### Comparing every pair of intervals — sort by start

Task: `intervals[i] = [start, end]` is a meeting. Return True if a person can
attend all of them: no two overlap. A meeting ending at 2 and one starting
at 2 don't overlap.

Waste: once the intervals are sorted by start, an overlap anywhere means an
overlap between neighbours. So n - 1 neighbour checks replace n(n-1)/2 pair
checks.

```python
def overlaps(a, b):                    # each starts before the other ends
    return a[0] < b[1] and b[0] < a[1]

# shorthand: test every pair of intervals for overlap
def can_attend_brute(intervals):
    n = len(intervals)
    for i in range(n):
        for j in range(i + 1, n):      # waste: most pairs are far apart in time
            if overlaps(intervals[i], intervals[j]):
                return False
    return True

# shorthand: sort by start, then compare each interval with the one before it
def can_attend(intervals):  # LC 252
    n = len(intervals)
    ordered = sorted(intervals, key=lambda iv: iv[0])
    for i in range(1, n):
        if ordered[i][0] < ordered[i - 1][1]:      # starts before the previous one ends
            return False
    return True

for f in [can_attend_brute, can_attend]:
    assert f([[0, 30], [5, 10], [15, 20]]) == False
    assert f([[7, 10], [2, 4]]) == True            # unsorted input: sorting finds the order
    assert f([[1, 2], [2, 3]]) == True             # touching endpoints: < not <=
    assert f([]) == True                           # no meetings
```

Trap: `<` versus `<=` decides whether touching intervals overlap; read the
problem. Comparing only neighbours works for "is there any overlap." For
merging (LC 56), compare with the end of the last merged interval instead,
because one long interval can cover several after it.

    brute  O(n²) time, O(1) space      n(n-1)/2 pairs
    fix    O(n log n) time, O(n) space  the sort; then one pass of n - 1 checks

Fix: Sort first, LC 56 (`array_warmup.md` section 5); Overlap test
(`search_warmup.md` section 3). Fallback: `pattern_code/19_fallbacks.py:403`.

### Simulating every jump — track the farthest reach

Task: `nums[i]` is the longest jump you can make from index i. Starting at
index 0, return True if you can reach the last index.

Waste: the brute force marks every cell each jump lands on, and the same
cells are marked again and again. The reachable cells are always a prefix
`0..farthest`, so one number replaces the whole array.

```python
# shorthand: from every reachable index, mark every index it can jump to
def can_jump_brute(nums):
    n = len(nums)
    reach = [False] * n
    reach[0] = True
    for i in range(n):
        if reach[i]:
            for step in range(1, nums[i] + 1):     # waste: re-marks cells earlier jumps marked
                if i + step < n:
                    reach[i + step] = True
    return reach[n - 1]

# shorthand: walk left to right, give up if this index is out of reach, otherwise extend the farthest reach
def can_jump(nums):  # LC 55
    n = len(nums)
    farthest = 0                       # invariant: every index in [0, farthest] is reachable
    for i in range(n):
        if i > farthest:
            return False               # a gap: nothing before i reaches it
        farthest = max(farthest, i + nums[i])
    return True

for f in [can_jump_brute, can_jump]:
    assert f([2, 3, 1, 1, 4]) == True
    assert f([3, 2, 1, 0, 4]) == False             # every path lands on the 0 at index 3
    assert f([0]) == True                          # single element: already at the end
    assert f([0, 1]) == False                      # stuck at the start
```

Trap: check `i > farthest` before reading `nums[i]`: an unreachable index
can't extend anything. The greedy is safe only because reachability is a
prefix. "Fewest jumps" (LC 45) needs the BFS-by-levels version, and anything
with costs needs DP.

    brute  O(n·M) time, O(n) space  M = max(nums): up to M marks per reachable index
    fix    O(n) time, O(1) space    one pass, one max per index

Fix: Greedy scan, LC 55 (`array_warmup.md` section 5). Next: LC 45
`08_greedy.py:111`. Fallback: `pattern_code/19_fallbacks.py:427`.


## 2. Strings

### Sorting two strings to compare them — count letters

Task: `s` and `t` are lowercase. Return True if `t` is an anagram of `s`: the
same letters, the same number of times, in any order.

Waste: sorting puts every letter in order, but the question only needs how
many of each. With 26 letters, a tally is O(n) and needs no copy of either
string.

```python
# shorthand: sort both strings and compare them
def is_anagram_brute(s, t):
    return sorted(s) == sorted(t)      # waste: orders the letters when only their counts matter

# shorthand: add one for each letter of s, subtract one for each letter of t, check every slot is zero
def is_anagram(s, t):  # LC 242
    if len(s) != len(t):
        return False
    n = len(s)
    counts = [0] * 26                  # invariant: counts[c] = (c in s[0:i]) - (c in t[0:i])
    for i in range(n):
        counts[ord(s[i]) - ord('a')] += 1
        counts[ord(t[i]) - ord('a')] -= 1
    for c in range(26):
        if counts[c] != 0:
            return False
    return True

for f in [is_anagram_brute, is_anagram]:
    assert f("anagram", "nagaram") == True
    assert f("rat", "car") == False
    assert f("a", "ab") == False                   # different lengths: the loop alone would miss the b
    assert f("", "") == True                       # empty strings
```

Trap: without the length check, the one loop over `len(s)` never looks at
`t`'s extra letters. `int[26]` assumes lowercase a-z. For Unicode or mixed
case, use a dict, which is still O(n).

    brute  O(n log n) time, O(n) space  two sorts, two sorted copies
    fix    O(n) time, O(1) space        one pass; 26 slots don't grow with n

Fix: Char to index (`structure_warmup.md` section 4). Next: LC 49
`14_strings.py:81`, LC 438 `02_sliding_window.py:239`.

### Checking every substring is a palindrome — expand around each center

Task: return the longest substring of `s` that reads the same both ways.

Waste: checking `s[i..j]` redoes the check of `s[i+1..j-1]`, which is that
same substring with its two ends removed. Growing outward from a center
reuses the inner check: each step outward is one comparison.

```python
def is_pal(s, lo, hi):                 # s[lo..hi] inclusive
    while lo < hi:
        if s[lo] != s[hi]:
            return False
        lo += 1
        hi -= 1
    return True

# shorthand: check every substring, keep the longest palindrome
def longest_palindrome_brute(s):
    n = len(s)
    best_lo = 0
    best_len = 0
    for i in range(n):
        for j in range(i, n):
            if j - i + 1 > best_len and is_pal(s, i, j):   # waste: re-checks the inside of s[i..j]
                best_lo = i
                best_len = j - i + 1
    return s[best_lo:best_lo + best_len]

def expand(s, lo, hi):                 # length of the palindrome grown from this center
    n = len(s)
    while lo >= 0 and hi < n and s[lo] == s[hi]:
        lo -= 1
        hi += 1
    return hi - lo - 1                 # the loop overshot by one on each side

# shorthand: from every center, odd and even, grow outward while the ends match, keep the longest
def longest_palindrome(s):  # LC 5
    n = len(s)
    best_lo = 0
    best_len = 0
    for c in range(n):
        odd = expand(s, c, c)          # center on a character: "aba"
        if odd > best_len:
            best_len = odd
            best_lo = c - odd // 2
        even = expand(s, c, c + 1)     # center between two characters: "abba"
        if even > best_len:
            best_len = even
            best_lo = c - even // 2 + 1
    return s[best_lo:best_lo + best_len]

for f in [longest_palindrome_brute, longest_palindrome]:
    assert f("forgeeksskeegfor") == "geeksskeeg"
    assert f("cbbd") == "bb"                       # even length: needs the between-characters center
    assert f("abc") == "a"                         # no repeats: any single character
    assert f("") == ""                             # empty input
```

Trap: there are 2n - 1 centers, n on characters and n - 1 between them.
Skip the even ones and "cbbd" returns "c". `expand` returns `hi - lo - 1`
because the loop stops one step past each end.

    brute  O(n³) time, O(1) space  n²/2 substrings, an O(n) check each
    fix    O(n²) time, O(1) space  2n - 1 centers, each grows up to n/2 steps

Fix: Opposite ends (`array_warmup.md` section 0), run outward instead of
inward. Reference: LC 5 `01_two_pointers.py:293`. Next: LC 647
`01_two_pointers.py:314`.

### Recursion over two strings — fill a table

Task: return the length of the longest common subsequence of `a` and `b`. A
subsequence keeps the characters' order but can skip characters.

Waste: on a mismatch, the recursion tries dropping a's character and
dropping b's, and both branches reach `go(i + 1, j + 1)`. Overlapping
branches make it exponential. There are only (n + 1)(m + 1) distinct
`(i, j)` pairs, so a table fills each one once.

```python
# shorthand: if the first characters match, take both; otherwise the best of skipping one from either string
def lcs_brute(a, b):
    n = len(a)
    m = len(b)
    def go(i, j):                      # LCS of a[i:] and b[j:]
        if i == n or j == m:
            return 0
        if a[i] == b[j]:
            return 1 + go(i + 1, j + 1)
        return max(go(i + 1, j), go(i, j + 1))     # waste: both branches reach go(i + 1, j + 1)
    return go(0, 0)

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

for f in [lcs_brute, lcs]:
    assert f("abcde", "ace") == 3
    assert f("abc", "def") == 0                    # nothing in common
    assert f("abc", "abc") == 3                    # identical strings
    assert f("", "abc") == 0                       # empty string: only the sentinel row
assert lcs("abc" * 20, "cab" * 20) == 59           # the brute force branches on every mismatch and never finishes
```

Trap: the table is shifted one slot from the strings. Compare `a[i - 1]` with
`b[j - 1]`, or the last row reads past the end. Build each row inside the
loop: `[[0] * (m + 1)] * (n + 1)` makes every row the same list. Memoizing
`go` with key `(i, j)` is an equally good fix.

    brute  O(2^(n+m)) time, O(n + m) space  two branches per mismatch; the stack is n + m deep
    fix    O(n·m) time, O(n·m) space        each cell filled once from three neighbours

Fix: DP table, LC 1143 (`structure_warmup.md` section 4); Memo key
(`search_warmup.md` section 2). Next: LC 72 `05_dp.py:297`.


## 3. Lists, trees, graphs

### Setup — run this first

The idioms below use these classes and builders, the same ones as
`docs/structure_warmup.md`.

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

def build_adj(n, edges):               # undirected
    adj = []
    for i in range(n):
        adj.append([])
    for i in range(len(edges)):
        u = edges[i][0]
        v = edges[i][1]
        adj[u].append(v)
        adj[v].append(u)
    return adj
```

### Walking the list twice — open a gap

Task: remove the k-th node from the end of a linked list (k = 1 is the last
node) and return the head. `1 <= k <= length`.

Waste: the brute force walks the list once to count it, then again to stop
before the target. Both are O(n). The waste is the second pass, which the
"one pass" follow-up forbids. Starting a second pointer k nodes behind the
first does both walks at once.

```python
# shorthand: count the nodes, then walk to the node before the target and unlink it
def remove_nth_brute(head, k):
    length = 0
    cur = head
    while cur is not None:
        length += 1
        cur = cur.next
    dummy = ListNode(0, head)
    prev = dummy
    for i in range(length - k):        # waste: re-walks nodes the count already passed
        prev = prev.next
    prev.next = prev.next.next
    return dummy.next

# shorthand: move fast k nodes ahead, move both until fast is on the last node, unlink slow's next
def remove_nth_from_end(head, k):  # LC 19
    dummy = ListNode(0, head)
    fast = dummy
    slow = dummy
    for i in range(k):
        fast = fast.next               # open the gap
    while fast.next is not None:       # invariant: fast is k nodes ahead of slow
        fast = fast.next
        slow = slow.next
    slow.next = slow.next.next         # slow is the node before the target
    return dummy.next

for f in [remove_nth_brute, remove_nth_from_end]:
    assert to_array(f(build_list([1, 2, 3, 4, 5]), 2)) == [1, 2, 3, 5]
    assert to_array(f(build_list([1, 2]), 1)) == [1]           # remove the tail
    assert to_array(f(build_list([1, 2]), 2)) == [2]           # remove the head: dummy covers it
    assert to_array(f(build_list([1]), 1)) == []               # single node: list becomes empty
```

Trap: start both pointers at `dummy` and stop when `fast.next` is None, so
`slow` lands on the node before the target. Start at `head` instead and
removing the head needs a special case.

    brute  O(n) time, O(1) space  two passes
    fix    O(n) time, O(1) space  one pass; same bound, but it answers the follow-up

Fix: Kth from end, Dummy head (`structure_warmup.md` section 1). Reference:
LC 19 `01_two_pointers.py:145`.

### Recomputing height at every node — return it up once

Task: return True if a binary tree is height-balanced: at every node, the
heights of the left and right subtrees differ by at most 1.

Waste: the brute force calls `height` at every node, and each `height` call
walks the whole subtree. A node at depth d gets measured once per ancestor,
d times. Returning the height up from one post-order pass measures each node
once.

```python
def height(node):
    if node is None:
        return 0
    return 1 + max(height(node.left), height(node.right))

# shorthand: at each node, compare the two subtree heights, then check both subtrees the same way
def is_balanced_brute(node):
    if node is None:
        return True
    if abs(height(node.left) - height(node.right)) > 1:   # waste: re-walks subtrees for every ancestor
        return False
    return is_balanced_brute(node.left) and is_balanced_brute(node.right)

# shorthand: return each subtree's height, or -1 as soon as any subtree is unbalanced
def is_balanced(root):  # LC 110
    def check(node):                   # height of node's subtree, or -1 if it's unbalanced
        if node is None:
            return 0
        left = check(node.left)
        if left == -1:
            return -1
        right = check(node.right)
        if right == -1:
            return -1
        if abs(left - right) > 1:
            return -1
        return 1 + max(left, right)
    return check(root) != -1

for f in [is_balanced_brute, is_balanced]:
    assert f(build_tree([3, 9, 20, None, None, 15, 7])) == True
    assert f(build_tree([1, 2, 2, 3, 3, None, None, 4, 4])) == False
    assert f(build_tree([1, None, 2, None, 3])) == False       # chain: the brute's O(n²) shape
    assert f(build_tree([1, 2, 2, 3, None, None, 3, 4, None, None, 4])) == False   # root's heights match; a child's don't
    assert f(None) == True                                     # empty tree
```

Trap: check for -1 before using a height. `1 + max(-1, 3)` turns "unbalanced"
into a real-looking height of 4. The parent needs the height, but the answer
is a yes/no, so the sentinel carries the no up through the height channel.

    brute  O(n²) time, O(h) space  a chain measures n + (n-1) + ... nodes; O(n log n) if balanced
    fix    O(n) time, O(h) space   each node visited once; h = tree height, for the stack

Fix: Return up (`structure_warmup.md` section 2). Next: LC 543
`03_trees.py:286`, LC 124 `03_trees.py:312`.

### A fresh search from every node — mark before you recurse

Task: return the number of connected components in an undirected graph with
nodes 0..n-1.

Waste: the brute force runs a full search from every node with a fresh
visited set, and treats u as a new component only if it's the smallest node
it reaches. A component of size s gets walked s times. One visited array
shared by all the starts walks each component once.

```python
def reachable(adj, src):               # every node src reaches
    visited = set()
    stack = [src]
    visited.add(src)
    while len(stack) > 0:
        u = stack.pop()
        for i in range(len(adj[u])):
            v = adj[u][i]
            if v not in visited:
                visited.add(v)         # mark on push: no node is pushed twice
                stack.append(v)
    return visited

# shorthand: search from every node; it starts a new component only if it's the smallest node it reaches
def count_components_brute(n, edges):
    adj = build_adj(n, edges)
    count = 0
    for u in range(n):
        if min(reachable(adj, u)) == u:            # waste: re-walks the whole component for each of its nodes
            count += 1
    return count

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

for f in [count_components_brute, count_components]:
    assert f(5, [[0, 1], [1, 2], [3, 4]]) == 2
    assert f(3, []) == 3                           # no edges: every node is its own component
    assert f(3, [[0, 1], [1, 2], [2, 0]]) == 1     # cycle: marking first stops it looping
    assert f(1, []) == 1                           # single node
```

Trap: mark a node when you first reach it, not when you finish it, or a
cycle sends the DFS around forever. Visited is still needed in the brute
force; what's wasted there is throwing it away between starts.

    brute  O(n·(n + e)) time, O(n + e) space  n full searches
    fix    O(n + e) time, O(n + e) space      each node and edge handled once overall

Fix: Mark before you recurse, LC 323 (`structure_warmup.md` section 3);
Union-find (section 3) when edges arrive over time.
