"""Patterns 59-63: Binary Search.

Core idea: any MONOTONE predicate over an ordered domain is searchable in
O(log n) — the domain needn't be an array. Frame everything as: check(x)
flips false->true exactly once; find the boundary. Invariant discipline
(lo always false-side, hi always true-side) kills off-by-ones.
The tell: "sorted" anywhere in the statement, or an optimization phrased
"minimize the largest / find the smallest x such that ..." whose
feasibility check is monotone (more of x never hurts).

The tell LIES when the score is not monotone in x. "Maximize the k/2
smallest warehouse loads" (Amazon OA) reads exactly like LC 875, but
scoring each cap x on [3, 5, 9, 6], k=4 gives 2,4,6,8,9,8,8,8,8 — a
peak, not a false->true flip, so check(mid) cannot say which half to
keep. Confirm monotonicity before committing to the template; when it
fails, scan x instead (secure_max_deliveries in 08_greedy.py).

Written deliberately plain (no bisect module, no clever expressions) so
the logic ports 1:1 to Java, C++, Go, JS on a whiteboard.
Run: python 09_binary_search.py
"""


# --------------------------------------------------------------- Pattern 59
import math


def lower_bound(nums: list[int], target: int) -> int:
    """Leftmost index where nums[i] >= target.
    THE reusable primitive — search-insert, first-bad-version and first/last
    occurrence are all this. The predicate reads false...false,true...true
    over a sorted array, so one probe at mid kills half the range.

    Naive: scan until nums[i] >= target — O(n). Each step re-asks "past the
    boundary yet?" for ONE element; a mid probe answers it for half at once.

    Real life: finding where a word goes in a dictionary — one glance at the
    middle page says before or after, and half the book is gone (a B-tree
    index seek locating the first row >= a key)."""
    lo, hi = 0, len(nums)                  # invariant: everything left of lo is false, everything from hi on is true
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1                   # mid is in the "too small" zone
        else:
            hi = mid                       # mid could be the answer: keep it
    return lo


def search_insert(nums: list[int], target: int) -> int:  # LC 35
    # lower_bound verbatim: the insert position IS the leftmost i with
    # nums[i] >= target, whether or not target is present.
    # Naive: scan for the first element >= target, O(n).
    # Real life: same dictionary flip — the page you'd slot the new word into.
    return lower_bound(nums, target)


def my_sqrt(x: int) -> int:  # LC 69
    """Integer square root: the largest m with m*m <= x.
    The domain is the ANSWER space, not an array. "m*m > x" flips false->true
    exactly once as m grows, so lower_bound over it finds the first too-big m
    and floor sqrt is one less — no candidates are ever materialized.

    Naive: count up 0, 1, 2, ... until m*m exceeds x — O(sqrt x) probes, each
    ruling out a single candidate where a mid guess rules out half.

    Real life: the higher/lower guessing game — square your guess, and the
    over/under reply discards half the range each turn (finding a maximum
    supported load in the fewest trial runs)."""
    lo, hi = 0, x + 1                      # find leftmost m with m*m > x, -1
    while lo < hi:
        mid = (lo + hi) // 2
        if mid * mid <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo - 1


def search_matrix(matrix: list[list[int]], target: int) -> bool:  # LC 74
    """Is target present in a row-major sorted matrix?
    The matrix IS one sorted array in disguise — each row starts after the
    previous ends, so global order holds. divmod maps a flat index back to
    (row, col) in O(1), so the search runs on a virtual array never built.

    Naive: scan all cells at O(mn), or binary-search each row at O(m log n) —
    both waste the fact that the rows chain into a single order.

    Real life: an encyclopedia numbered straight through every volume — page
    612 over pages-per-volume gives the volume and the offset inside it, so
    the set searches like one book (block = offset // size, slot = offset % size)."""
    rows, cols = len(matrix), len(matrix[0])
    lo, hi = 0, rows * cols                # invariant: virtual flat array [0, rows*cols), answer in [lo, hi)
    while lo < hi:
        mid = (lo + hi) // 2
        val = matrix[mid // cols][mid % cols]
        if val == target:
            return True
        if val < target:
            lo = mid + 1
        else:
            hi = mid
    return False


# --------------------------------------------------------------- Pattern 60
def search_rotated(nums: list[int], target: int) -> int:  # LC 33
    """Index of target in a sorted array that was rotated, or -1.
    Rotation breaks GLOBAL order but not local order: cut anywhere and at
    least one half is fully sorted. Ask which half that is and whether target
    fits between its endpoints — either way half the range dies, no pivot hunt.

    Naive: linear scan, O(n). Plain binary search's "which side?" test LIES on
    a rotated array; the sorted-half endpoint test is what restores it.

    Real life: an alphabetized shelf someone rotated to M-Z then A-L —
    wherever you split it one side is still in order, and its two end labels
    say whether your book belongs there (a log that wrapped in a ring buffer)."""
    lo, hi = 0, len(nums) - 1              # invariant: target, if present, in [lo, hi]
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:          # left half is the sorted one
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1               # target inside the CERTAIN half
            else:
                lo = mid + 1
        else:                              # right half is the sorted one
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1


def find_min_rotated(nums: list[int]) -> int:  # LC 153
    """Smallest value in a rotated sorted array.
    The min IS the rotation point, and "nums[i] <= nums[hi]" is monotone:
    false along the first run, true from the min onward. Comparing mid to the
    RIGHT end is what makes it monotone — against lo it is ambiguous and breaks.

    Naive: scan for the single drop where nums[i] < nums[i-1] — O(n), asking
    "has the wrap happened?" one index at a time.

    Real life: a guest log that wrapped past midnight — if an entry is LATER
    than the final entry, the wrap point lies to its right (locating where a
    circular log actually begins)."""
    lo, hi = 0, len(nums) - 1              # invariant: the min is in [lo, hi]
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:           # min is to the right of mid
            lo = mid + 1
        else:
            hi = mid                       # mid could be the min
    return nums[lo]


def find_peak_element(nums: list[int]) -> int:  # LC 162
    """Index of any element greater than both its neighbours.
    No sortedness required — only a DIRECTION. Climbing to the right means a
    peak lies that way, since the array ends in a virtual -inf cliff. That ANY
    peak is acceptable is exactly what makes discarding half safe unsorted.

    Naive: walk until nums[i] > nums[i+1] — O(n), asking "still climbing?"
    one element at a time where a mid probe answers it for half the ridge.

    Real life: dropped on a mountain range in fog — feel which way the ground
    slopes and head uphill; you must top out somewhere (hill climbing where
    any local optimum is good enough)."""
    lo, hi = 0, len(nums) - 1              # invariant: some peak is in [lo, hi]
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:      # uphill to the right ->
            lo = mid + 1                   # some peak lies that way
        else:
            hi = mid
    return lo


# --------------------------------------------------------------- Pattern 61
# Binary search ON THE ANSWER: optimization -> monotone decision problem.
def min_eating_speed(piles: list[int], h: int) -> int:  # LC 875
    """Slowest eating speed that clears all piles within h hours.
    Turn the optimization into a DECISION: "can speed s finish?" is monotone,
    because eating faster never hurts. Then it is lower_bound over speeds,
    with the O(n) feasibility check standing in for the comparison.

    Naive: try speeds 1, 2, 3, ... until one works — O(max(piles)) checks of
    O(n) each, settling a single speed per step instead of half of them.

    Real life: finding the slowest treadmill setting that still finishes
    inside the hour — trial a middle speed and halve the dial each time
    (capacity planning: fewest servers meeting the SLA, probed by load test)."""
    def can_finish(speed: int) -> bool:    # monotone: faster always works
        total_hours = 0
        for p in piles:
            hours_for_this_pile = math.ceil(p/speed)
            total_hours += hours_for_this_pile
        return total_hours <= h # did we fit in the time limit

    lo, hi = 1, max(piles)                 # invariant: answer in [lo, hi]; hi always feasible
    while lo < hi:
        mid = (lo + hi) // 2
        if can_finish(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def ship_within_days(weights: list[int], days: int) -> int:  # LC 1011
    """Smallest ship capacity that moves all weights, in order, within D days.
    Same answer-space search as LC 875; the new piece is the GREEDY check —
    packing each day as full as the order permits uses the fewest days, so
    can_ship is exact, and monotone since a bigger ship never needs more days.

    Naive: try capacities max(weights), +1, +2, ... up to sum(weights) — that
    many O(n) simulations, where binary search needs only log of them.

    Real life: renting the smallest truck that still finishes in D trips —
    load boxes in order until full, count trips, resize (smallest batch size
    that clears a job queue by its deadline)."""
    def can_ship(cap: int) -> bool:        # greedy check: fill each day
        used, load = 1, 0
        for w in weights:
            load += w
            if load > cap:
                used += 1
                load = w
        return used <= days

    lo, hi = max(weights), sum(weights)    # invariant: answer in [lo, hi]; heaviest item is the floor, one-day haul the ceiling
    while lo < hi:
        mid = (lo + hi) // 2
        if can_ship(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def split_array(nums: list[int], k: int) -> int:  # LC 410
    # Same skeleton as LC 1011 with the story stripped off: days -> k parts,
    # ship capacity -> largest part sum. "Minimize the maximum" is the tell.
    # Naive: DP over split points, O(n^2 * k); monotone check gives O(n log sum).
    # Real life: same truck problem relabeled — k trucks, make the heaviest
    # load as light as possible.
    def can_split(cap: int) -> bool:
        parts, cur = 1, 0
        for x in nums:
            cur += x
            if cur > cap:
                parts += 1
                cur = x
        return parts <= k

    lo, hi = max(nums), sum(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if can_split(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def smallest_divisor(nums: list[int], threshold: int) -> int:  # LC 1283
    """Smallest divisor making the sum of ceil(x/d) fit under threshold.
    The check is a SUM OF CEILINGS, not a greedy packing loop, and ceil(x/d)
    never grows as d grows — so the total only falls and lower_bound applies.
    Worth its own entry: "sum(ceil(item/x)) <= budget" recurs constantly, and
    LC 875 above is this exact shape with the divisor renamed "speed".

    Naive: try divisors 1, 2, 3, ... until the sum drops under threshold —
    O(max(nums)) passes of O(n), settling one divisor per step.

    Real life: picking the biggest crate size that keeps shipping inside your
    load budget — a part-filled crate still costs a whole crate (right-sizing
    a batch when every partial batch still costs a full round trip)."""
    def sum_of_ceils(d: int) -> int:       # monotone: bigger d, smaller sum
        total = 0
        for x in nums:
            total += math.ceil(x/d)        # a partial group still costs one
        return total

    lo, hi = 1, max(nums)                  # invariant: answer in [lo, hi]; hi always feasible, every term collapses to 1
    while lo < hi:
        mid = (lo + hi) // 2
        if sum_of_ceils(mid) <= threshold:
            hi = mid
        else:
            lo = mid + 1
    return lo


def min_segment_repeats(s: str, k: int) -> int:  # Amazon OA
    """Fewest repeats m of a length-k segment covering every char's frequency in s.
    Another sum-of-ceilings check, same family as LC 1283: with m repeats,
    char c needs ceil(count[c]/m) slots, so m works iff the total is <= k.
    The guard is the real lesson — every distinct char costs one slot forever,
    so more distinct chars than k is impossible and the search would never find it.

    Naive: try m = 1, 2, 3, ... until the slots fit — O(max count) passes,
    settling one candidate per step where the monotone check halves them.

    Real life: sizing a repeating stamp so a run of impressions covers an
    order — a character needing one slot per press is what binds, not the
    length of the order.

    Feasibility traces; '?' marks a spare slot, fillable with anything:

      s = "aaabb", k = 3  ->  2          counts   a:3  b:2
        m=1   ceil(3/1) + ceil(2/1) = 5   > 3     segment too wide
        m=2   ceil(3/2) + ceil(2/2) = 3  <= 3     "aab" x2 = "aabaab"
        Overshoot is fine: that gives 4 a's for the 3 needed.

      s = "abc", k = 3  ->  1            counts   a:1  b:1  c:1
        m=1        1 + 1 + 1        = 3  <= 3     "abc" x1
        k already holds one of each, so one press covers it.

      s = "abc", k = 2  ->  -1           counts   a:1  b:1  c:1
        Every char costs >= 1 slot no matter how big m grows, so the sum
        bottoms out at 3 and never reaches 2. The guard catches this
        up front; binary search would never find it.

      s = "aabbcc", k = 4  ->  2         counts   a:2  b:2  c:2
        m=1        2 + 2 + 2        = 6   > 4
        m=2        1 + 1 + 1        = 3  <= 4     "abc?" x2 = "abc?abc?"
        3 slots of 4 used: the test is <= k, the segment need not fill k.

      s = "aaaaaaab", k = 3  ->  4       counts   a:7  b:1
        m=1   ceil(7/1) + ceil(1/1) = 8   > 3
        m=2   ceil(7/2) + ceil(1/2) = 5   > 3
        m=3   ceil(7/3) + ceil(1/3) = 4   > 3
        m=4   ceil(7/4) + ceil(1/4) = 3  <= 3     "aab" x4 = "aabaabaabaab"
        THE case to remember: 'b' costs one slot forever, so the 7 a's
        must fit the 2 slots left -> ceil(7/2) = 4 repeats. What binds is
        one skewed count against the one-slot-per-distinct floor, not the
        length of s."""
    count = {}                             # invariant: char -> its frequency in s
    for ch in s:
        if ch in count:
            count[ch] += 1
        else:
            count[ch] = 1
    if len(count) > k:                     # every distinct char needs >= 1 slot
        return -1                          # no m, however large, can fit

    def slots_needed(m: int) -> int:       # segment length required for m repeats
        total = 0
        for c in count:
            total += math.ceil(count[c]/m)
        return total

    lo, hi = 1, max(count.values())        # hi feasible: every term collapses to 1
    while lo < hi:
        mid = (lo + hi) // 2
        if slots_needed(mid) <= k:
            hi = mid
        else:
            lo = mid + 1
    return lo


# --------------------------------------------------------------- Pattern 62
def search_range(nums: list[int], target: int) -> list[int]:  # LC 34
    """First and last index of target in a sorted array, or [-1, -1].
    Both ends from ONE primitive: first = lower_bound(target), last =
    lower_bound(target + 1) - 1, since the first index past all targets sits
    exactly one after the last. No separate upper-bound template to misplace.

    Naive: scan for the first and last match — O(n), worst when the whole
    array IS the target. Two boundary searches replace it with O(log n).

    Real life: finding every "Smith" in a phone book — flip to the first
    Smith, then to the first name AFTER Smith and back up one line (a
    time-range query: seek first >= start, first >= end)."""
    left = lower_bound(nums, target)
    if left == len(nums) or nums[left] != target:
        return [-1, -1]
    return [left, lower_bound(nums, target + 1) - 1]


# --------------------------------------------------------------- Pattern 63
def find_median_sorted_arrays(a: list[int], b: list[int]) -> float:  # LC 4
    """Median of two sorted arrays in O(log min(m, n)).
    Don't search a value — search the CUT. Pick i elements of a for the left
    half and j = half - i is forced; the cut is valid iff every left element
    <= every right one, which only the four border values decide. "a gave too
    much" is monotone in i, so binary search over i in the SMALLER array.

    Naive: merge and index the middle — O(m + n). The merge ranks every
    element when the question is only whether one cut is balanced.

    Real life: two sorted queues filing into a front and back room, half
    each — slide the divider in the SHORT queue and the other is forced; the
    split is right when the tallest at the front is <= the shortest at back."""
    if len(a) > len(b):
        a, b = b, a                        # search the smaller array
    m, n = len(a), len(b)
    half = (m + n + 1) // 2
    lo, hi = 0, m                          # invariant: valid cut i is in [lo, hi]
    while True:
        i = (lo + hi) // 2                 # a contributes i to the left half
        j = half - i                       # b contributes the rest
        a_left = a[i - 1] if i else float("-inf")
        a_right = a[i] if i < m else float("inf")
        b_left = b[j - 1] if j else float("-inf")
        b_right = b[j] if j < n else float("inf")
        if a_left <= b_right and b_left <= a_right:   # valid partition
            if (m + n) % 2:
                return max(a_left, b_left)
            return (max(a_left, b_left) + min(a_right, b_right)) / 2
        if a_left > b_right:               # a gave too much to the left
            hi = i - 1
        else:
            lo = i + 1


if __name__ == "__main__":
    assert lower_bound([1, 3, 5, 6], 5) == 2
    assert search_insert([1, 3, 5, 6], 2) == 1
    assert my_sqrt(8) == 2 and my_sqrt(16) == 4  # floor between squares / exact square
    assert search_matrix([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 3)
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 0) == 4
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 3) == -1  # absent: fits neither sorted half
    assert find_min_rotated([3, 4, 5, 1, 2]) == 1
    assert find_peak_element([1, 2, 3, 1]) == 2
    assert min_eating_speed([3, 6, 7, 11], 8) == 4
    assert ship_within_days([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5) == 15
    assert split_array([7, 2, 5, 10, 8], 2) == 18
    assert smallest_divisor([1, 2, 5, 9], 6) == 5
    assert min_segment_repeats("aaabb", 3) == 2   # segment "aab" twice covers 3a, 2b
    assert min_segment_repeats("abc", 3) == 1     # k fits one of each: no repeat needed
    assert min_segment_repeats("abc", 2) == -1    # 3 distinct chars can't share 2 slots
    assert min_segment_repeats("aabbcc", 4) == 2  # "abc?" x2: check is <= k, not == k
    assert min_segment_repeats("aaaaaaab", 3) == 4  # lone 'b' eats a slot -> ceil(7/2)
    assert search_range([5, 7, 7, 8, 8, 10], 8) == [3, 4]
    assert find_median_sorted_arrays([1, 3], [2]) == 2      # odd total: max of left borders
    assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5  # even total: average across the cut
    print("09_binary_search: all checks passed")
