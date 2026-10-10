# Array warmup

This file has one short, runnable example for each array technique, each built
around the smallest problem that still makes you write the technique. Each
block ends with an `assert`, so you can paste it into `main.py` and run it.

Assumes you know: Python basics and Big-O.
Not covered: linked lists, trees, graphs (`docs/structure_warmup.md`), and
backtracking, memoization, heaps, bits (`docs/search_warmup.md`). For the
mixed daily rotation, see `docs/daily_warmup.md`.

How to use it: read the tell, cover the code, and write it yourself. Then
compare, and read "Why it works." If you can't restate that explanation out
loud, you memorized the code without understanding it. After that, the `Next:` line lists harder problems that use the same
mechanism, with their answer keys in `pattern_code/`.

Section 0 is smaller than a problem: the loop shapes that every later section
is built from. Drill those first. Most off-by-one bugs live in the loop
itself, not in picking the technique.


## 0. Loop idioms

Each idiom is a few lines with an invariant and the one trap that breaks it.
Read the task, cover the code, and write it from memory. Then run the
asserts and say the invariant out loud.
They run simplest first: no loop, then one index, nested indices, carried
state, two moving indices, and finally a helper stack.

    swap with tmp           save before you overwrite; a, b = b, a doesn't port
    adjacent pairs          start at 1 and look back, or stop at n-1 and look ahead
    frequency count         check the key before incrementing
    all pairs               j starts at i + 1: each pair once, never i with itself
    grid neighbours         bounds check before the read; -1 silently wraps in Python
    running sum, inclusive  add, then write: out[i] includes nums[i]
    running sum, exclusive  write, then add: out[i] excludes nums[i]
    right-to-left pass      range(n-1, -1, -1): the stop is -1, not 0
    prefix with sentinel    pre has n+1 slots; sum(l..r) = pre[r+1] - pre[l]
    min so far              order of "use running" and "update running" decides i < j
    opposite ends           hi = n - 1, while lo < hi, move one side per step
    reader / writer         write never passes read, so overwriting is safe
    run grouping            j < n first in the and; then i = j
    merge two sorted        main loop, then drain both leftovers
    fixed-size window       remove when i >= k, record when i >= k - 1
    variable-size window    subtract nums[left] before moving left
    window with counts      delete a key when its count hits 0
    lower bound             hi = n, lo < hi, hi = mid: the three go together
    monotonic stack         empty check first; store indices, not values

Every idiom uses the same names, so a name tells you the variable's role:

    nums          the input array, even when the problem calls it diff or prices
    a, b          the two inputs when there are two
    n, m          lengths, computed once at the top
    i, j          loop indices; j is the second index in a nested loop or run
    lo, hi        the ends of a range that closes inward
    read, write   the reader / writer indices
    left, right   the window edges
    r, c          a grid cell; rows, cols are the grid size
    running       the state carried from one index to the next: a sum, min, or max
    best          the answer so far
    out           the output array
    pre           the prefix array, n+1 slots
    count         an integer tally
    freq          a dict tally: value -> how many times it appeared
    stack         indices still waiting for their answer
    tmp           the value saved during a swap

### Swap with tmp — save before you overwrite

Task: swap `nums[i]` and `nums[j]` in place.

```python
# shorthand: save the first element, copy the second over it, put the saved element in the second slot
def swap(nums, i, j):
    tmp = nums[i]                      # save it: the next line destroys nums[i]
    nums[i] = nums[j]
    nums[j] = tmp

nums = [1, 2, 3]
swap(nums, 0, 2)
assert nums == [3, 2, 1]
swap(nums, 1, 1)
assert nums == [3, 2, 1]                           # i == j: swapping with itself changes nothing
```

Trap: without `tmp`, `nums[i] = nums[j]` then `nums[j] = nums[i]` leaves
both slots holding the old `nums[j]`. Python's `a, b = b, a` hides the
problem, and it doesn't port to Java/C++.

Used in: Reader / writer, LC 283 (section 1), Partition, LC 75 (section 2), Reverse / rotate, LC 189 (section 2).

### Adjacent pairs — look back from 1

Task: count the positions where a value is bigger than the one before it.

```python
# shorthand: from the second element on, compare the current element with the previous one
def count_increases(nums):
    n = len(nums)
    count = 0
    for i in range(1, n):              # start at 1 so nums[i - 1] exists
        if nums[i] > nums[i - 1]:
            count += 1
    return count

assert count_increases([1, 3, 2, 4, 5]) == 3
assert count_increases([7]) == 0                   # single element: no pairs
```

Trap: pick one form and keep it. `range(1, n)` with `nums[i - 1]` and
`range(n - 1)` with `nums[i + 1]` are both correct. Mixing them,
`range(1, n)` with `nums[i + 1]`, reads past the end.

Used in: Sort first, LC 56 (section 5), which compares each interval to the last merged one.

### Frequency count — check the key first

Task: return a dict that maps each value to how many times it appears.

```python
# shorthand: for each element, add one to its count, starting the count at one if it's new
def frequency(nums):
    n = len(nums)
    freq = {}                          # invariant: freq[v] = times v appears in nums[0:i]
    for i in range(n):
        if nums[i] in freq:
            freq[nums[i]] += 1
        else:
            freq[nums[i]] = 1
    return freq

assert frequency([2, 1, 2]) == {2: 2, 1: 1}
assert frequency([]) == {}                         # empty input
```

Trap: `freq[nums[i]] += 1` on a missing key raises `KeyError`. In Java, it's
`freq.put(nums[i], freq.getOrDefault(nums[i], 0) + 1)`.

Used in: Prefix sum + map, LC 560 (section 3), Hash map, LC 1 (section 4).

### All pairs — j starts at i + 1

Task: count the index pairs i < j whose values add up to `target`.

```python
# shorthand: for each element, compare it with every element after it
def count_pairs_with_sum(nums, target):
    n = len(nums)
    count = 0
    for i in range(n):
        for j in range(i + 1, n):      # j > i: each pair once, never i with itself
            if nums[i] + nums[j] == target:
                count += 1
    return count

assert count_pairs_with_sum([1, 2, 3, 2], 4) == 2  # (1, 3) and (2, 2)
assert count_pairs_with_sum([2], 4) == 0           # single element: it can't pair with itself
```

Trap: `for j in range(n)` counts every pair twice and pairs each `i` with
itself, so `[2]` would return 1. This is the O(n^2) baseline that the hash
map beats.

Used in: Hash map, LC 1 (section 4), as the naive version. Brute forces in `pattern_code/19_fallbacks.py`.

### Grid neighbours — bounds before the read

Task: given a 0/1 grid and a cell (r, c), count how many of its four
neighbours (up, down, left, right) are 1.

```python
# shorthand: move in each of the four directions, skip moves off the grid, check the element there
def count_land_neighbours(grid, r, c):
    rows = len(grid)
    cols = len(grid[0])
    dr = [-1, 1, 0, 0]                 # up, down, left, right
    dc = [0, 0, -1, 1]
    count = 0
    for d in range(4):
        nr = r + dr[d]
        nc = c + dc[d]
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
            count += 1
    return count

grid = [[1, 1, 0],
        [0, 1, 1]]
assert count_land_neighbours(grid, 0, 1) == 2      # (0, 0) and (1, 1)
assert count_land_neighbours(grid, 0, 0) == 1      # corner: two of the four neighbours are off the grid
```

Trap: check bounds before `grid[nr][nc]`. In Python, `nr = -1` doesn't
crash. It silently reads the last row. Swapping `rows` and `cols` only
breaks non-square grids, so test on one (this grid is 2 x 3). Java has no
chained comparison, so write `0 <= nr && nr < rows`.

Used in: Matrix, LC 48 (section 2). Next: LC 200 `04_graphs.py:15`.

### Running sum, inclusive — add, then write

Task: return a running total. `out[i]` is the sum of `nums[0]` through
`nums[i]`, including `nums[i]` itself:

    nums  3  0  -1  2
    out   3  3   2  4      out[2] = 3 + 0 + (-1)

This is the last step of a difference array (section 3), which stores
changes and turns them back into values this way.

```python
# shorthand: add the current element to the running total, then write it to the output
def accumulate(nums):                  # nums is a difference array
    n = len(nums)
    out = [0] * n
    running = 0                        # invariant: after the add, running = sum(nums[0..i])
    for i in range(n):
        running += nums[i]
        out[i] = running
    return out

assert accumulate([3, 0, -1, 2]) == [3, 3, 2, 4]
assert accumulate([]) == []                        # empty input: loop never runs
```

Trap: if you swap the two lines, every value shifts right by one. That's the
next idiom, and here it's a bug. In Java/C++, make `running` a `long`.

Used in: Difference array (section 3), the Kadane `cur` in Running best (section 3).

### Running sum, exclusive — write, then add

Task: return a running total that leaves out the current element. `out[i]` is
the sum of `nums[0]` through `nums[i - 1]`, so `out[0] = 0`, because nothing
comes before index 0:

    nums  3  1  2
    out   0  3  4      out[2] = 3 + 1, without the 2 at index 2

Compare it with running sum, inclusive, on the same input, `[3, 4, 6]`. Every
value is shifted one slot right.

```python
# shorthand: write the running total to the output, then add the current element to it
def exclusive_prefix(nums):
    n = len(nums)
    out = [0] * n
    running = 0                        # invariant: at the write, running = sum(nums[0:i]), i excluded
    for i in range(n):
        out[i] = running
        running += nums[i]
    return out

assert exclusive_prefix([3, 1, 2]) == [0, 3, 4]
```

Trap: the order of the two lines is the idiom. Write first whenever the answer
at i must exclude `nums[i]`.

Used in: Prefix + suffix passes, LC 238 (section 3).

### Right-to-left pass — the stop is -1

Task: `out[i]` is the largest value at index i or anywhere to its right.

```python
# shorthand: from the last element to the first, update the running max, then write it to the output
def suffix_max(nums):
    n = len(nums)
    out = [0] * n
    running = float('-inf')            # invariant: after the max, running = max(nums[i:])
    for i in range(n - 1, -1, -1):
        running = max(running, nums[i])
        out[i] = running
    return out

assert suffix_max([3, 1, 4, 1, 2]) == [4, 4, 4, 2, 2]
assert suffix_max([5]) == [5]                      # single element: index 0 must be visited
```

Trap: `range(n - 1, 0, -1)` skips index 0. The stop is exclusive, so it has to
be -1. In Java: `for (int i = n - 1; i >= 0; i--)`.

Used in: the right pass of LC 238 (section 3), Overwrite from the back, LC 88 (section 2).

### Prefix with sentinel — n+1 slots

Task: build a prefix array, then answer any inclusive range sum `nums[l..r]`
with one subtraction.

```python
# shorthand: start the prefix with a zero, each slot is the previous slot plus the current element
def build_prefix(nums):
    n = len(nums)
    pre = [0] * (n + 1)                # invariant: pre[i] = sum(nums[0:i])
    for i in range(n):
        pre[i + 1] = pre[i] + nums[i]
    return pre

def range_sum(pre, l, r):              # inclusive l..r
    return pre[r + 1] - pre[l]

pre = build_prefix([2, 4, 1, 3])
assert pre == [0, 2, 6, 7, 10]
assert range_sum(pre, 1, 2) == 5
assert range_sum(pre, 0, 3) == 10                  # l = 0: pre[0] = 0 removes the special case
```

Trap: `pre[r] - pre[l]` drops `nums[r]`. Read `pre[i]` as "sum of the first
i elements," and `r + 1` follows.

Used in: Prefix sum + map, LC 560 (section 3), where the map plays the role of `pre`.

### Min so far — use, then update

Task: `nums[i]` is a stock's price on day i. Buy once and sell on a later day.
Return the best profit, or 0 if no trade makes money.

```python
# shorthand: record the best of the current element minus the running min, then update the running min
def max_profit(nums):  # LC 121, nums = prices
    n = len(nums)
    running = nums[0]                  # invariant: at the use, running = min(nums[0:i]), i excluded
    best = 0
    for i in range(1, n):
        best = max(best, nums[i] - running)
        running = min(running, nums[i])
    return best

assert max_profit([7, 1, 5, 3, 6, 4]) == 5
assert max_profit([7, 6, 4, 1]) == 0               # strictly falling: never trade
```

Trap: using `running` before updating it pairs i only with earlier indices
(j < i). Updating first lets i pair with itself. Here that's harmless, because
it only adds a profit of 0. In "pair of distinct elements" problems, it's a
wrong answer. Kadane goes the other way (update `cur`, then record `best`)
because there the subarray is supposed to include i.

Used in: Running best, LC 53 (section 3). Next: LC 121 `08_greedy.py:132`.

### Opposite ends — while lo < hi

Task: reverse `nums` in place.

```python
# shorthand: start at both ends, swap the two elements, move both inward until they meet
def reverse(nums):
    n = len(nums)
    lo = 0
    hi = n - 1                         # invariant: everything outside [lo, hi] is already reversed
    while lo < hi:
        tmp = nums[lo]
        nums[lo] = nums[hi]
        nums[hi] = tmp
        lo += 1
        hi -= 1
    return nums

assert reverse([1, 2, 3, 4]) == [4, 3, 2, 1]
assert reverse([1, 2, 3]) == [3, 2, 1]             # odd length: the middle stays put
assert reverse([]) == []                           # empty: hi = -1, loop never runs
```

Trap: `hi` starts at `n - 1`, not `n`. Using `lo <= hi` is harmless here,
because it only swaps the middle with itself. In pair problems (LC 167), it
pairs an element with itself.

Used in: Opposite ends, LC 167 (section 1), Reverse / rotate, LC 189 (section 2).

### Reader / writer — write never passes read

Task: remove every copy of `val` in place, keep the rest in their original
order, and return how many are left.

```python
# shorthand: for each element, if it's kept, copy it to the write slot and move the write slot forward
def remove_element(nums, val):  # LC 27
    n = len(nums)
    write = 0                          # invariant: nums[0:write] = kept elements, in order
    for read in range(n):
        if nums[read] != val:
            nums[write] = nums[read]
            write += 1
    return write

nums = [3, 2, 2, 3]
assert remove_element(nums, 3) == 2
assert nums[0:2] == [2, 2]
assert remove_element([3, 3], 3) == 0              # everything removed: write never moves
```

Trap: return `write`, the count, not `write - 1`. Overwriting is safe because
`write <= read`, so you only clobber a slot you already read.

Used in: Reader / writer, LC 283 (section 1).

### Run grouping — inner while, then jump

Task: return the length of each run of equal values that sit next to each
other.

```python
# shorthand: from the start of a run, move forward while elements match, write the run's length to the output, jump to the run's end
def run_lengths(nums):
    n = len(nums)
    out = []
    i = 0
    while i < n:
        j = i                          # invariant: nums[i:j] all equal nums[i]
        while j < n and nums[j] == nums[i]:
            j += 1
        out.append(j - i)
        i = j                          # the next run starts where this one ended
    return out

assert run_lengths([1, 1, 2, 3, 3, 3]) == [2, 1, 3]
assert run_lengths([5]) == [1]                     # single element: one run of length 1
```

Trap: `j < n` has to come first in the `and`. Otherwise, the last run reads
`nums[n]`. If you forget `i = j`, the loop never ends. It's O(n) despite the
nesting, because `j` visits each index once.

Used in: Adjacent pairs, extended from pairs to whole runs. Next: LC 26 `01_two_pointers.py:183`.

### Merge two sorted — then drain

Task: merge two sorted arrays into one sorted array.

```python
# shorthand: write the smaller front element to the output until one side runs out, then copy the rest
def merge_sorted(a, b):
    n = len(a)
    m = len(b)
    out = []
    i = 0                              # invariant: out = sorted merge of a[0:i] and b[0:j]
    j = 0
    while i < n and j < m:
        if a[i] <= b[j]:               # <= takes a first on ties (stable)
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    while i < n:                       # drain: at most one of these two loops runs
        out.append(a[i])
        i += 1
    while j < m:
        out.append(b[j])
        j += 1
    return out

assert merge_sorted([1, 4, 6], [2, 3, 7, 8]) == [1, 2, 3, 4, 6, 7, 8]
assert merge_sorted([], [1, 2]) == [1, 2]          # one side empty: only the drain runs
```

Trap: forget the drain loops and you silently drop the tail of the longer
array. The first assert catches it, because `7, 8` are left over.

Used in: Overwrite from the back, LC 88 (section 2), which runs this backward so it needs no extra array.

### Fixed-size window — add i, remove i - k

Task: return the largest sum of any k consecutive elements.

```python
# shorthand: add the current element to the running total, drop the element k back, record the best once the window is full
def max_sum_window(nums, k):
    n = len(nums)
    running = 0                        # invariant: once i >= k - 1, running = sum(nums[i-k+1:i+1])
    best = float('-inf')
    for i in range(n):
        running += nums[i]
        if i >= k:
            running -= nums[i - k]     # the element that just left the window
        if i >= k - 1:                 # the window is full
            best = max(best, running)
    return best

assert max_sum_window([1, 12, -5, -6, 50, 3], 4) == 51
assert max_sum_window([5, 1], 2) == 6              # k == n: exactly one window
```

Trap: there are two different guards. Remove when `i >= k`, and record when
`i >= k - 1`. If you use one guard for both, you either record partial
windows or skip the first full one. Unlike the variable-size window, there's no
`while`, because the size never changes. In Java/C++, make `running` a
`long`.

Used in: Monotonic deque, LC 239 (section 4), which evicts with the same `i - k`.

### Variable-size window — subtract before moving

Task: all values are non-negative. Return the length of the longest subarray
whose sum is at most `limit`.

```python
# shorthand: add the current element to the running total, drop elements from the left while too big, record the best length
def longest_sum_at_most(nums, limit):  # values non-negative
    n = len(nums)
    left = 0
    running = 0                        # invariant: running = sum(nums[left:right+1])
    best = 0
    for right in range(n):
        running += nums[right]
        while running > limit:         # invalid: shrink until valid
            running -= nums[left]
            left += 1
        best = max(best, right - left + 1)
    return best

assert longest_sum_at_most([1, 2, 1, 0, 1, 1, 0], 4) == 5
assert longest_sum_at_most([5], 4) == 0            # one element over the limit: window empties, left = right + 1
```

Trap: `left += 1` before `running -= nums[left]` subtracts the wrong element.
Where you record also matters. Longest records after the `while`, once the
window is valid. Shortest (LC 209) records inside the `while`, while the
window is still valid.

Used in: Sliding window, LC 209 (section 1).

### Window with counts — delete at zero

Task: return the length of the longest substring of `s` that has at most `k`
distinct characters.

```python
# shorthand: add the right character to the counts, drop characters from the left while there are too many distinct ones, record the best length
def longest_k_distinct(s, k):  # LC 340
    n = len(s)
    freq = {}                          # invariant: freq = counts in s[left:right+1], no zero entries
    left = 0
    best = 0
    for right in range(n):
        if s[right] in freq:
            freq[s[right]] += 1
        else:
            freq[s[right]] = 1
        while len(freq) > k:           # invalid: too many distinct characters
            freq[s[left]] -= 1
            if freq[s[left]] == 0:
                del freq[s[left]]      # a key at 0 would still count as distinct
            left += 1
        best = max(best, right - left + 1)
    return best

assert longest_k_distinct("eceba", 2) == 3         # "ece"
assert longest_k_distinct("aa", 1) == 2
assert longest_k_distinct("abc", 0) == 0           # k = 0: every window shrinks to empty
```

Trap: without the `del`, `len(freq)` never goes down, so the `while` runs
`left` off the end of the string. Decrement first, then delete at zero. In
Java, it's `map.remove(c)` once `map.get(c) == 0`. When the alphabet is fixed,
an `int[26]` plus a separate `distinct` counter avoids the map.

Used in: Sliding window (section 1), when the window's validity depends on
counts instead of a sum (LC 3, LC 76).

### Lower bound — hi = n, lo < hi, hi = mid

Task: `nums` is sorted. Return the first index whose value is >= `target`, or
n if there isn't one. That is where `target` would be inserted.

```python
# shorthand: check the middle element; if too small, move right past it, otherwise keep it and move left
def lower_bound(nums, target):
    n = len(nums)
    lo = 0
    hi = n                             # invariant: the answer is in [lo, hi]; hi = n means "past the end"
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] < target:
            lo = mid + 1               # mid is too small: the answer is to its right
        else:
            hi = mid                   # mid might be the answer: keep it
    return lo

assert lower_bound([1, 3, 5, 6], 5) == 2
assert lower_bound([1, 3, 5, 6], 7) == 4           # past the end: hi = n leaves room for it
assert lower_bound([], 3) == 0                     # empty: loop never runs
```

Trap: the three choices go together: `hi = n`, `lo < hi`, `hi = mid`. Don't
mix them with the `lo <= hi` / `hi = mid - 1` form. With `lo <= hi`,
`hi = mid` loops forever once `lo == hi`. Write `mid` as `lo + (hi - lo) // 2`
so it ports to Java without `int` overflow.

Used in: Binary search (lower bound), LC 35 (section 5), Binary search on the answer, LC 875 (section 5).

### Monotonic stack — while, then push

Task: for each element, return the first value to its right that is strictly
bigger, or -1 if there isn't one.

```python
# shorthand: pop every waiting element the current element beats, write it to the output as their answer, then push the current element
def next_greater(nums):
    n = len(nums)
    out = [-1] * n
    stack = []                         # invariant: indices still waiting, values non-increasing bottom to top
    for i in range(n):
        while len(stack) > 0 and nums[stack[-1]] < nums[i]:
            j = stack.pop()
            out[j] = nums[i]           # nums[i] is the first bigger value right of j
        stack.append(i)
    return out

assert next_greater([2, 1, 3, 2, 4]) == [3, 3, 4, 4, -1]
assert next_greater([3, 3]) == [-1, -1]            # equal values: strict < leaves both waiting
```

Trap: the emptiness check has to come before `stack[-1]` in the `and`.
Store indices, not values, because the answer often needs a distance
(LC 739). Choosing `<` or `<=` decides what happens to equal values.

Used in: Monotonic stack, LC 739 (section 4), Monotonic deque, LC 239 (section 4).

## 1. Pointers

### Opposite ends — LC 167 Two Sum II (sorted)

Tell: the array is sorted and you need a pair that meets a target.

```python
def two_sum_sorted(nums, target):
    lo = 0
    hi = len(nums) - 1
    while lo < hi:
        s = nums[lo] + nums[hi]
        if s == target:
            return [lo + 1, hi + 1]    # 1-indexed per LC
        if s < target:
            lo += 1                    # need bigger: nums[lo] can't pair with anything <= hi
        else:
            hi -= 1                    # need smaller: nums[hi] can't pair with anything >= lo
    return []

assert two_sum_sorted([2, 7, 11, 15], 9) == [1, 2]
```

Why it works: because the array is sorted, `nums[lo]` is the smallest value
still in play and `nums[hi]` is the largest. If the sum is too small, then
even the largest partner can't lift `nums[lo]` to the target, so no pair that
uses `lo` can work, and you discard it.

The same argument works in reverse for `hi` when the sum is too big. Each step
safely discards one element.

Time O(n), space O(1).

Next: LC 11 `01_two_pointers.py:70`, LC 15 `01_two_pointers.py:35`

### Reader / writer — LC 283 Move Zeroes

Tell: the problem says "in place," and you need to keep some elements and
drop others.

```python
def move_zeroes(nums):
    write = 0                                  # invariant: nums[0:write] = nonzeros, in order
    for read in range(len(nums)):
        if nums[read] != 0:
            tmp = nums[write]
            nums[write] = nums[read]
            nums[read] = tmp
            write += 1
    return nums

assert move_zeroes([0, 1, 0, 3, 12]) == [1, 3, 12, 0, 0]
```

Why it works: `read` visits every element, and `write` marks where the next
nonzero belongs. Each nonzero gets swapped down to `write`, so the nonzeros
keep their relative order. The zero they displace moves right.

Swapping, rather than overwriting and zero-filling afterward, handles both
halves of the array in a single pass.

Time O(n), space O(1).

Next: LC 26 `01_two_pointers.py:183`, LC 844 `01_two_pointers.py:246`

### Fast / slow on indices — LC 287 Find the Duplicate

Tell: values are in 1..n and you can't modify the array. Treat each value as
a "next" pointer.

```python
def find_duplicate(nums):
    slow = nums[0]
    fast = nums[0]
    while True:                        # phase 1: meet inside the cycle
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    slow = nums[0]                     # phase 2: meet at the cycle entrance
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow

assert find_duplicate([1, 3, 4, 2, 2]) == 2
```

Why it works: treat index i as a node with an edge to `nums[i]`. There are
n+1 indices pointing into the range 1..n, so two of them point at the
duplicate value. A node with two incoming edges is the entrance to a cycle.

Phase 1 is Floyd's algorithm. `fast` gains one step on `slow` every round, so
the two must meet somewhere inside the cycle. Phase 2 relies on a fact: the
distance from the start to the cycle entrance equals the distance from the
meeting point to the entrance (counting around the cycle). So when both move
one step at a time from those two spots, they meet at the entrance, which is
the duplicate.

Time O(n), space O(1), and the array is never modified.

Next: LC 141 `01_two_pointers.py:100` (the linked-list original)

### Sliding window — LC 209 Minimum Size Subarray Sum

Tell: you need the longest or shortest contiguous subarray, and all values
are non-negative.

```python
def min_subarray_len(target, nums):
    best = len(nums) + 1
    left = 0
    total = 0                          # invariant: total = sum(nums[left:right+1])
    for right in range(len(nums)):
        total += nums[right]
        while total >= target:         # valid -> record, then try shrinking
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    if best == len(nums) + 1:
        return 0
    return best

assert min_subarray_len(7, [2, 3, 1, 2, 4, 3]) == 2
assert min_subarray_len(100, [1, 2]) == 0          # no valid window
```

Why it works: with non-negative values, growing the window never lowers the
sum and shrinking it never raises the sum. That makes greedy shrinking safe.
Once `[left, right]` is valid, any longer window that ends at `right` is only
worse, so you record the length and drop `left`.

The `while` loop is nested, but each index enters the window once and leaves
it once.

Time O(n), space O(1).

Next: LC 1004 `02_sliding_window.py:170`, LC 3 `02_sliding_window.py:40`.
Negative values break the shrink step, so use a prefix sum instead (see
section 3).


## 2. Rearranging in place

### Reverse / rotate — LC 189 Rotate Array

Tell: shift everything by k, with O(1) extra space.

```python
def reverse(nums, lo, hi):
    while lo < hi:
        tmp = nums[lo]
        nums[lo] = nums[hi]
        nums[hi] = tmp
        lo += 1
        hi -= 1

def rotate(nums, k):
    n = len(nums)
    k = k % n                          # k can exceed n
    reverse(nums, 0, n - 1)
    reverse(nums, 0, k - 1)
    reverse(nums, k, n - 1)
    return nums

assert rotate([1, 2, 3, 4, 5, 6, 7], 3) == [5, 6, 7, 1, 2, 3, 4]
assert rotate([1, 2], 3) == [2, 1]                 # k > n
```

Why it works: rotating right by k moves the last k elements to the front.
Reversing the whole array does put them at the front, but backwards, and the
rest of the array ends up behind them, also backwards. Reversing each part
separately restores the order inside it.

`k % n` is needed because rotating by n does nothing, and without it
`reverse(0, k-1)` would index past the end of the array.

Time O(n), space O(1).

Next: LC 151 `01_two_pointers.py:332`

### Partition (Dutch flag) — LC 75 Sort Colors

Tell: only 2 or 3 distinct values, and the problem wants one pass.

```python
def sort_colors(nums):
    lo = 0                             # invariant: nums[0:lo] are all 0
    mid = 0                            # invariant: nums[lo:mid] are all 1
    hi = len(nums) - 1                 # invariant: nums[hi+1:] are all 2
    while mid <= hi:
        if nums[mid] == 0:
            tmp = nums[lo]; nums[lo] = nums[mid]; nums[mid] = tmp
            lo += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            tmp = nums[hi]; nums[hi] = nums[mid]; nums[mid] = tmp
            hi -= 1                    # NOT mid += 1: the swapped-in value is unchecked
    return nums

assert sort_colors([2, 0, 2, 1, 1, 0]) == [0, 0, 1, 1, 2, 2]
```

Why it works: the three pointers split the array into four regions: 0s, 1s,
unknown (`mid..hi`), and 2s. Each step classifies `nums[mid]` and shrinks the
unknown region by one. The loop ends when that region is empty.

The asymmetry is the whole trick. A swap with `lo` brings back a value that
has already been classified, so `mid` can advance. A swap with `hi` brings in
a value nobody has looked at, so `mid` has to stay and check it.

One pass. Time O(n), space O(1).

Next: `01_two_pointers.py:219`

### Index marking — LC 448 Find All Disappeared Numbers

Tell: values are in 1..n and you're asked for O(1) extra space. Each index
can store a "seen" flag for the value that belongs there.

```python
def find_disappeared(nums):
    for i in range(len(nums)):
        idx = abs(nums[i]) - 1         # abs: this slot may already be negated
        if nums[idx] > 0:
            nums[idx] = -nums[idx]     # mark value idx+1 as seen
    out = []
    for i in range(len(nums)):
        if nums[i] > 0:
            out.append(i + 1)
    return out

assert find_disappeared([4, 3, 2, 7, 8, 2, 3, 1]) == [5, 6]
```

Why it works: the values are 1..n and the indices are 0..n-1, so every value v
owns slot v-1. Negating `nums[v-1]` records "v appeared" without destroying
the number stored in that slot, and `abs()` gets it back.

After the pass, any slot that is still positive belongs to a value that never
appeared.

Time O(n), space O(1) not counting the output.

Next: LC 442 `13_array_matrix.py:297`, LC 41 `13_array_matrix.py:274`

### Overwrite from the back — LC 88 Merge Sorted Array

Tell: the destination array has free space at its end.

```python
def merge(nums1, m, nums2, n):
    i = m - 1
    j = n - 1
    w = m + n - 1                      # invariant: nums1[w+1:] is final
    while j >= 0:                      # once nums2 is drained, nums1's rest is in place
        if i >= 0 and nums1[i] > nums2[j]:
            nums1[w] = nums1[i]
            i -= 1
        else:
            nums1[w] = nums2[j]
            j -= 1
        w -= 1
    return nums1

assert merge([1, 2, 3, 0, 0, 0], 3, [2, 5, 6], 3) == [1, 2, 2, 3, 5, 6]
assert merge([0], 0, [1], 1) == [1]                # nums1 starts empty
```

Why it works: filling from the front would overwrite `nums1` values that
haven't been merged yet. The back of `nums1` is free space. `w` can never
overtake `i`, because `w - i = j + 1`, which stays positive while `nums2`
still has elements.

Each step takes the larger of the two tails. When `j` goes negative, whatever
is left in `nums1[0..i]` is already in place. If `i` runs out first, the
`else` branch copies the rest of `nums2`.

Time O(m + n), space O(1).

Next: LC 977 `13_array_matrix.py:248`

### Matrix — LC 48 Rotate Image

Tell: rotate or flip a 2-D grid in place.

```python
def rotate_image(m):
    n = len(m)
    for i in range(n):                 # transpose across the main diagonal
        for j in range(i + 1, n):
            tmp = m[i][j]; m[i][j] = m[j][i]; m[j][i] = tmp
    for i in range(n):                 # reverse each row
        lo = 0
        hi = n - 1
        while lo < hi:
            tmp = m[i][lo]; m[i][lo] = m[i][hi]; m[i][hi] = tmp
            lo += 1
            hi -= 1
    return m

assert rotate_image([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
```

Why it works: a 90° clockwise rotation sends cell (i, j) to (j, n-1-i).
Transposing sends (i, j) to (j, i), and reversing each row then sends (j, i)
to (j, n-1-i). Doing both gives the rotation.

The transpose loop starts at `j = i + 1`, so each pair is swapped exactly
once. If it started at 0, every pair would be swapped twice, which undoes the
transpose.

Time O(n²), space O(1).

Next: LC 54 `13_array_matrix.py:51`, LC 73 `13_array_matrix.py:84`


## 3. Precomputing

### Prefix sum + map — LC 560 Subarray Sum Equals K

Tell: count subarrays whose sum equals k, when values can be negative.

```python
def subarray_sum(nums, k):
    count = {0: 1}                     # empty prefix: lets subarrays start at index 0
    prefix = 0                         # Java/C++: make this a long
    result = 0
    for x in nums:
        prefix += x
        if prefix - k in count:        # some earlier prefix p with prefix - p == k
            result += count[prefix - k]
        if prefix in count:
            count[prefix] += 1
        else:
            count[prefix] = 1
    return result

assert subarray_sum([1, 1, 1], 2) == 2
assert subarray_sum([1, -1, 0], 0) == 3            # negatives: a sliding window fails here
```

Trace of `subarray_sum([1, -1, 0], 0)`:

    x    prefix  need (prefix - k)  count[need]  result  count after insert
    -    0       -                  -            0       {0: 1}
    1    1       1                  0            0       {0: 1, 1: 1}
    -1   0       0                  1            1       {0: 2, 1: 1}    finds [1, -1]
    0    0       0                  2            3       {0: 3, 1: 1}    finds [1, -1, 0] and [0]

The last row is the point: two earlier prefixes equal 0 (the empty prefix and
the one after `-1`), so one step adds two subarrays.

Why it works: `sum(nums[i+1..j]) = prefix[j] - prefix[i]`. So a subarray
ending at j sums to k exactly when some earlier prefix equals
`prefix[j] - k`. The map counts how many earlier prefixes had each value,
which means each j finds all its matches in O(1).

`{0: 1}` stands for the empty prefix before index 0, so subarrays that start
at index 0 get counted. Check the map before inserting the current prefix. If
you insert first, then with k = 0 the current prefix matches itself and you
count an empty subarray.

Time O(n), space O(n).

Next: LC 724 `18_prefix_sum.py:202`, LC 525 `18_prefix_sum.py:164`, LC 974 `18_prefix_sum.py:94`

### Prefix + suffix passes — LC 238 Product Except Self

Tell: the answer at i depends on everything to the left and everything to
the right.

```python
def product_except_self(nums):
    n = len(nums)
    out = [1] * n
    left = 1                           # invariant: product of nums[0:i]
    for i in range(n):
        out[i] = left
        left *= nums[i]
    right = 1                          # invariant: product of nums[i+1:]
    for i in range(n - 1, -1, -1):
        out[i] *= right
        right *= nums[i]
    return out

assert product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6]
assert product_except_self([0, 1, 2]) == [2, 0, 0]  # zero present, no division
```

Trace of `product_except_self([1, 2, 3, 4])`:

    pass   i  nums[i]  running before  out[i]         running after
    left   0  1        1               1              1
    left   1  2        1               1              2
    left   2  3        2               2              6
    left   3  4        6               6              24
    right  3  4        1               6 * 1 = 6      4
    right  2  3        4               2 * 4 = 8      12
    right  1  2        12              1 * 12 = 12    24
    right  0  1        24              1 * 24 = 24    24

`out[i]` always reads the running product before `nums[i]` is multiplied in.
After the left pass, `out = [1, 1, 2, 6]`, which is the left products alone.

Why it works: `out[i]` = (product of everything left of i) × (product of
everything right of i). The first pass writes the running left product into
`out[i]` before multiplying `nums[i]` in, so position i is excluded. The
second pass does the same from the right and multiplies its product in.

There's no division, so zeros need no special case.

Time O(n), space O(1) besides the output.

Next: LC 845 `13_array_matrix.py:163`, LC 42 Trapping Rain Water (no reference in the repo)

### Difference array — LC 1109 Corporate Flight Bookings

Tell: many range updates, then you read every position once at the end.

```python
def corp_flight_bookings(bookings, n):
    diff = [0] * (n + 1)               # +1 so diff[last] never goes out of range
    for b in bookings:
        first = b[0]
        last = b[1]
        seats = b[2]
        diff[first - 1] += seats
        diff[last] -= seats
    out = [0] * n
    running = 0
    for i in range(n):
        running += diff[i]
        out[i] = running
    return out

assert corp_flight_bookings([[1, 2, 10], [2, 3, 20], [2, 5, 25]], 5) == [10, 55, 45, 25, 25]
```

Trace of `corp_flight_bookings([[1, 2, 10], [2, 3, 20], [2, 5, 25]], 5)`.
Phase 1 writes the markers:

    booking       +seats at  -seats at  diff after
    [1, 2, 10]    0          2          [10,  0, -10,   0, 0,   0]
    [2, 3, 20]    1          3          [10, 20, -10, -20, 0,   0]
    [2, 5, 25]    1          5          [10, 45, -10, -20, 0, -25]

Phase 2 runs the sum:

    i  diff[i]  running = out[i]
    0  10       10
    1  45       55     all three bookings active
    2  -10      45     booking 1 ends
    3  -20      25     booking 2 ends
    4  0        25

`diff[5] = -25` is never read. It is the `+1` slot that absorbs a booking
ending at the last flight.

Why it works: adding `seats` to every flight in `[first, last]` one at a time
costs O(range) per booking. A difference array records only where each change
starts (`+seats` at `first-1`) and where it stops (`-seats` at `last`).

A running sum over `diff` turns those markers back into totals. Every index
between the two markers picks up `+seats`, and the `-seats` cancels it for
every index after the range.

Time O(n + bookings), space O(n).

Next: LC 370 `17_difference_array.py:22`, LC 1094 `17_difference_array.py:64`

### Running best — LC 53 Maximum Subarray (Kadane)

Tell: find the best contiguous sum, where each element either extends the
current run or starts a new one.

```python
def max_subarray(nums):
    cur = nums[0]                      # invariant: best sum of a subarray ending at i
    best = nums[0]
    for i in range(1, len(nums)):
        cur = max(nums[i], cur + nums[i])
        best = max(best, cur)
    return best

assert max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
assert max_subarray([-3, -1, -2]) == -1            # all negative: don't return 0
```

Trace of `max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4])`:

    i  x   restart (x)  extend (cur + x)  cur  best
    0  -2  -            -                 -2   -2
    1  1   1            -2 + 1 = -1       1    1     restart wins
    2  -3  -3           1 - 3 = -2        -2   1
    3  4   4            -2 + 4 = 2        4    4     restart wins
    4  -1  -1           4 - 1 = 3         3    4
    5  2   2            3 + 2 = 5         5    5
    6  1   1            5 + 1 = 6         6    6     best run: [4, -1, 2, 1]
    7  -5  -5           6 - 5 = 1         1    6
    8  4   4            1 + 4 = 5         5    6

Restart wins exactly when the incoming `cur` is negative (rows 1 and 3). At
row 4, `cur` stays positive through the `-1`, so the run keeps it.

Why it works: `cur` is the best sum of a subarray that must end at i. That
subarray is either `nums[i]` alone or an extension of the best one ending at
i-1. If `cur` has gone negative, dragging it along only hurts, so you restart.

The answer is the largest `cur` seen at any i. Starting from `nums[0]` rather
than 0 keeps all-negative arrays correct.

Time O(n), space O(1).

Next: LC 121 `08_greedy.py:132`, LC 152 `05_dp.py:101`


## 4. Adding a helper structure

### Hash map — LC 1 Two Sum

Tell: for each element, you need to know whether its complement appeared
earlier.

```python
def two_sum(nums, target):
    seen = {}                          # invariant: value -> index, for nums[0:i]
    for i in range(len(nums)):
        need = target - nums[i]
        if need in seen:
            return [seen[need], i]
        seen[nums[i]] = i              # insert AFTER the check: no self-pairing
    return []

assert two_sum([3, 3], 6) == [0, 1]                # duplicate values
```

Why it works: `nums[i]` needs the partner `target - nums[i]`. The map
remembers every value already passed, so the partner lookup is O(1) instead of
a rescan of the array.

Inserting after the check means an element can't pair with itself. Duplicates
like `[3, 3]` still work, because the first 3 is already in the map when the
second one arrives.

Time O(n), space O(n).

Next: LC 49 `14_strings.py:81`, LC 128 Longest Consecutive Sequence (no reference in the repo)

### Monotonic stack — LC 739 Daily Temperatures

Tell: "next greater" or "next smaller" element.

```python
def daily_temperatures(temps):
    ans = [0] * len(temps)
    stack = []                         # invariant: indices still waiting, temps decreasing
    for i in range(len(temps)):
        while stack and temps[stack[-1]] < temps[i]:
            j = stack.pop()
            ans[j] = i - j             # push indices, not values: you need the distance
        stack.append(i)
    return ans

assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]
```

Why it works: the stack holds the days that are still waiting for a warmer
day. Their temperatures never increase from bottom to top, because a warmer
day would already have resolved every cooler day above it.

When day i arrives, it pops and answers every waiting day it beats, starting
from the top. It stops at the first day that is at least as warm, since every
day below that one is at least as warm too.

Each index is pushed once and popped at most once. Time O(n), space O(n).

Next: LC 503 `10_stack.py:78`, LC 84 `10_stack.py:334`

### Monotonic deque — LC 239 Sliding Window Maximum

Tell: you need the max (or min) of every window of size k.

```python
from collections import deque

def max_sliding_window(nums, k):
    dq = deque()                       # invariant: indices in window, nums decreasing
    out = []
    for i in range(len(nums)):
        if dq and dq[0] <= i - k:      # front fell out of the window
            dq.popleft()
        while dq and nums[dq[-1]] <= nums[i]:
            dq.pop()                   # can never be a max while nums[i] is around
        dq.append(i)
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out

assert max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
```

Why it works: the deque holds only the indices that could still become a
window max, with values decreasing from front to back. When `nums[i]`
arrives, any smaller value at the back is both older and smaller than it, so
it can never be the max again, and it gets popped.

That leaves the front as the max of the current window. It only needs to be
evicted once its index slides out of the window.

Each index enters and leaves once. Time O(n), space O(k).

Next: `02_sliding_window.py:196`

### Heap — LC 215 Kth Largest Element

Tell: "k-th largest," "top k," or "k closest."

```python
import heapq

def find_kth_largest(nums, k):
    heap = []                          # invariant: min-heap of the k largest seen so far
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]

assert find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4
```

Why it works: keep a min-heap holding the k largest values seen so far. When
it grows to k+1, pop the smallest, since it can't be in the top k. At the end
the heap holds exactly the k largest values, and its minimum, `heap[0]`, is
the k-th largest.

It's a min-heap, not a max-heap, because the thing you keep throwing away is
the smallest.

Time O(n log k), space O(k).

Next: LC 347 `06_heap.py:33`, LC 973 `06_heap.py:49`


## 5. Using or creating order

### Sort first — LC 56 Merge Intervals

Tell: intervals, or pairs whose original order doesn't matter.

```python
def merge_intervals(intervals):
    intervals.sort(key=lambda iv: iv[0])
    merged = []
    for iv in intervals:
        if merged and iv[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], iv[1])   # max: iv may be nested inside
        else:
            merged.append([iv[0], iv[1]])
    return merged

assert merge_intervals([[1, 3], [8, 10], [2, 6], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
assert merge_intervals([[1, 10], [2, 3]]) == [[1, 10]]  # nested interval
```

Why it works: after sorting by start, any interval that overlaps the current
merged block must come right after it, because nothing later can start
earlier. That makes one pass enough.

If the next start is ≤ the current end, the two overlap, and you extend the
end with `max`. The `max` matters because a nested interval must not shrink
the end. Otherwise you start a new block.

Time O(n log n) for the sort, then O(n).

Next: LC 57 `08_greedy.py:48`, LC 455 `08_greedy.py:227`

### Binary search (lower bound) — LC 35 Search Insert Position

Tell: sorted input and an O(log n) requirement.

```python
def search_insert(nums, target):
    lo = 0
    hi = len(nums)                     # hi = n: the answer can be "past the end"
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo                          # first index with nums[i] >= target

assert search_insert([1, 3, 5, 6], 5) == 2
assert search_insert([1, 3, 5, 6], 7) == 4         # insert at end
```

Why it works: this is a lower bound, meaning it finds the first index where
`nums[i] >= target`. The loop keeps two facts true: everything before `lo` is
`< target`, and everything from `hi` onward is `>= target`. When they meet,
`lo` is the boundary.

If `nums[mid] < target`, the answer lies strictly right of `mid`. Otherwise
`mid` itself might be the answer, so `hi = mid`, not `mid - 1`. Starting with
`hi = n` covers a target larger than every element.

Time O(log n), space O(1).

Next: LC 34 `09_binary_search.py:367`, LC 153 `09_binary_search.py:137`, LC 33 `09_binary_search.py:107`

### Binary search on the answer — LC 875 Koko Eating Bananas

Tell: "minimum X such that..." or "minimize the maximum," where a larger X
never hurts.

```python
def min_eating_speed(piles, h):
    def can(speed):                    # monotone: if speed works, speed+1 works
        hours = 0
        for p in piles:
            hours += (p + speed - 1) // speed      # ceil division
        return hours <= h

    lo = 1
    hi = max(piles)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if can(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo

assert min_eating_speed([3, 6, 7, 11], 8) == 4
```

Why it works: nothing about the array is sorted, but the speeds are.
`can(speed)` is false for small speeds and true for large ones, and it flips
exactly once. Binary search finds the first speed where it's true, using the
same lower-bound template as LC 35.

The range is 1..max(piles) because at `max(piles)` each pile takes exactly one
hour, and the problem guarantees `h >= len(piles)`.

Time O(n log max(piles)), space O(1).

Next: LC 1011 `09_binary_search.py:212`, LC 410 `09_binary_search.py:243`

### Greedy scan — LC 55 Jump Game

Tell: you only need a yes/no answer or a count, and the best local move is
provably safe.

```python
def can_jump(nums):
    farthest = 0                       # invariant: max index reachable from nums[0:i]
    for i in range(len(nums)):
        if i > farthest:
            return False
        farthest = max(farthest, i + nums[i])
    return True

assert can_jump([2, 3, 1, 1, 4]) is True
assert can_jump([3, 2, 1, 0, 4]) is False
```

Why it works: `farthest` is the farthest index reachable from any position
seen so far. If i ever passes `farthest`, there's a gap no jump can cross.
Otherwise i is reachable, so you extend `farthest` from it.

You never need to know which path got you somewhere, because every index up
to `farthest` is reachable.

Time O(n), space O(1).

Next: LC 45 `08_greedy.py:111`, LC 134 `08_greedy.py:165`


## 6. Treating values as data

### XOR — LC 268 Missing Number

Tell: every value appears in pairs except one. Because x ^ x = 0, the pairs
cancel out.

```python
def missing_number(nums):
    x = len(nums)                      # the index n has no slot in the loop
    for i in range(len(nums)):
        x ^= i ^ nums[i]
    return x

assert missing_number([3, 0, 1]) == 2
assert missing_number([0]) == 1                    # missing value is n
```

Why it works: XOR together every index 0..n and every value. Each number that
is present appears twice, once as an index and once as a value, so it cancels
out. The missing number appears only as an index, so it's what remains.

`x` starts at n because the loop's indices only go up to n-1. The formula
`n(n+1)/2 - sum` also works, but it can overflow in Java/C++, and XOR can't.

Time O(n), space O(1).

Next: LC 136 `11_bits.py:11`, LC 137 `11_bits.py:45`

### Bitmask — LC 78 Subsets

Tell: n is at most about 20, and you want every subset.

```python
def subsets(nums):
    n = len(nums)
    out = []
    for mask in range(1 << n):         # bit i of mask = "take nums[i]"
        subset = []
        for i in range(n):
            if mask & (1 << i):
                subset.append(nums[i])
        out.append(subset)
    return out

assert len(subsets([1, 2, 3])) == 8
assert [] in subsets([1, 2, 3])
```

Why it works: each of the n elements is either in a subset or out of it, so
there are 2^n subsets. Those map one-to-one onto the integers 0..2^n-1
written in n bits, where bit i set means "take `nums[i]`".

Looping over every mask therefore produces every subset exactly once.

Time O(n · 2^n), the same as the output size.

Next: `07_backtracking.py:11` (the backtracking version)

### DP over indices — LC 198 House Robber

Tell: the choice at i depends only on the choices at i-1 and i-2.

```python
def rob(nums):
    prev2 = 0                          # best up to i-2
    prev1 = 0                          # best up to i-1
    for x in nums:
        cur = max(prev1, prev2 + x)    # skip this house, or take it
        prev2 = prev1
        prev1 = cur
    return prev1

assert rob([2, 7, 9, 3, 1]) == 12
assert rob([]) == 0                                # no houses
```

Trace of `rob([2, 7, 9, 3, 1])`:

    house  x   skip (prev1)  rob (prev2 + x)  cur
    0      2   0             0 + 2 = 2        2
    1      7   2             0 + 7 = 7        7
    2      9   7             2 + 9 = 11       11
    3      3   11            7 + 3 = 10       11    skipping wins
    4      1   11            11 + 1 = 12      12

Why it works: the best total through house i is one of two options. Either
you skip house i (best through i-1), or you rob it (x + best through i-2,
because i-1 has to be skipped).

Only the last two values are ever read, so two variables replace the whole dp
array. Starting both at 0 handles an empty list and a single house.

Time O(n), space O(1).

Next: LC 300 `05_dp.py:429`, LC 416 `05_dp.py:199`
