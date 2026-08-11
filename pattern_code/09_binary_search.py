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
    """Leftmost index where nums[i] >= target. THE reusable primitive:
    search-insert, first-bad-version, first/last occurrence are all this.
    The predicate "nums[i] >= target" reads false...false,true...true over
    a sorted array; one probe at mid tells which side of the flip we're
    on, so half the range dies per step. Sync invariant: everything left
    of lo is known-false, everything from hi on is known-true.

    Naive: scan left to right until nums[i] >= target — O(n). Each scan
    step re-asks "past the boundary yet?" for ONE element; a mid probe
    answers it for half the remaining range at once.

    Real life: finding where a word goes in a dictionary — open to the
    middle, one glance says "before or after this page", half the book is
    gone; you never leaf page by page (a B-tree index seek finding the
    first row >= a key)."""
    lo, hi = 0, len(nums)                  # hi is exclusive; answer in [lo, hi]
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
    """Same template, but the domain is the ANSWER space, not an array.
    The predicate "m*m > x" flips false->true exactly once as m grows;
    lower_bound over it finds the first too-big m, and floor sqrt is one
    less. Nothing here needs the candidates materialized — check(mid)
    computes membership on demand.

    Naive: count up 0, 1, 2, ... until m*m exceeds x — O(sqrt x) probes,
    each ruling out a single candidate; a mid guess rules out half of
    what's left.

    Real life: the higher/lower number-guessing game — guess a number,
    square it, and the over/under reply discards half the range every
    turn (finding a max supported load with the fewest trial runs)."""
    lo, hi = 0, x + 1                      # find leftmost m with m*m > x, -1
    while lo < hi:
        mid = (lo + hi) // 2
        if mid * mid <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo - 1


def search_matrix(matrix: list[list[int]], target: int) -> bool:  # LC 74
    """Row-major sorted matrix IS one sorted array in disguise: each row
    starts after the previous row ends, so global order holds. divmod maps
    a flat index to (row, col) in O(1), and plain binary search runs on
    the virtual array without ever building it.

    Naive: scan all cells O(mn), or binary-search each row O(m log n) —
    both waste the fact that rows chain into one order; a single search
    over rows*cols flat indices is O(log mn).

    Real life: an encyclopedia set with pages numbered straight through
    every volume — page 612 divided by pages-per-volume gives the volume
    and the offset inside it, so the whole set searches like one book
    (paged storage: block = offset // block_size, slot = offset %
    block_size)."""
    rows, cols = len(matrix), len(matrix[0])
    lo, hi = 0, rows * cols                # virtual flat array [0, rows*cols)
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
    """Rotation breaks GLOBAL order but not local order: cut [lo, hi]
    anywhere and at least one half is fully sorted. Per step ask "which
    half is the sorted one, and does target's value fit between its
    endpoints?" — if it fits, search there; if not, the target can only
    be in the messy half. Either way half the range dies, no need to
    locate the pivot first.

    Naive: linear scan, O(n) — plain binary search's "which side?" test
    lies on a rotated array; the sorted-half endpoint test restores a
    trustworthy answer at every step.

    Real life: an alphabetized bookshelf someone rotated (M-Z then A-L):
    wherever you split it, one side is still alphabetized, and its two
    end labels tell you whether your book belongs there (searching a
    sorted log that wrapped around in a ring buffer)."""
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
    """The min is the rotation point, and "nums[i] <= nums[hi]" is a
    monotone predicate: false along the first (larger) run, true from the
    min onward — so lower_bound-style search finds the flip. Comparing
    mid to the RIGHT end is what makes the test monotone; comparing to lo
    is ambiguous and breaks it.

    Naive: scan for the one drop where nums[i] < nums[i-1], O(n). Each
    step asks "has the wrap happened yet?" for one index; one mid-vs-hi
    comparison answers it for half the range.

    Real life: a guest log that wrapped around midnight — compare any
    entry's timestamp to the final entry's: if it's LATER, the wrap point
    (and the oldest entry) lies to its right (finding where a wrapped
    circular log begins)."""
    lo, hi = 0, len(nums) - 1              # invariant: the min is in [lo, hi]
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:           # min is to the right of mid
            lo = mid + 1
        else:
            hi = mid                       # mid could be the min
    return nums[lo]


def find_peak_element(nums: list[int]) -> int:  # LC 162
    """No sortedness required — only a DIRECTION. If nums[mid] <
    nums[mid+1] the terrain climbs to the right, and since the array ends
    in a virtual -inf cliff, some peak must lie that way; otherwise mid
    itself sits on a downhill, so a peak lies at mid or left. ANY peak is
    accepted, which is exactly what makes discarding half safe on
    unsorted data.

    Naive: walk until nums[i] > nums[i+1], O(n). Each step asks "still
    climbing?" one element at a time; a mid probe answers it for half the
    remaining ridge.

    Real life: dropped on a mountain range in fog — feel which way the
    ground slopes and head uphill; you must top out somewhere, and
    jumping to the middle of the remaining ridge each time tops out in
    log steps (hill climbing when any local optimum is good enough)."""
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
    """Turn the optimization "min speed to finish in h hours" into the
    decision "can speed s finish?" — monotone, because eating faster
    never hurts. Then it's lower_bound over speeds: the O(n) greedy check
    plays the role of the comparison, and the flip point is the answer.

    Naive: try speeds 1, 2, 3, ... until one works — O(max(piles)) checks
    of O(n) each. Each unit step re-asks "fast enough yet?" for a single
    speed; a mid-speed check settles half the remaining speeds at once.

    Real life: finding the slowest treadmill speed that still finishes
    the workout inside your hour — trial-run a middle speed and halve the
    dial range on the result, instead of nudging it up by 1 (capacity
    planning: fewest servers that still meet the SLA, probed by load
    test)."""
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
    """Same answer-space search; the new piece is the GREEDY feasibility
    check: for a fixed capacity, packing each day as full as the order
    allows uses the fewest possible days, so can_ship is exact — and
    monotone, since a bigger ship never needs more days. Bounds fall out
    of the problem: at least the heaviest single item, at most everything
    in one day.

    Naive: try capacities max(weights), +1, +2, ... up to sum(weights) —
    that many O(n) simulations; binary search needs only log of them.

    Real life: renting the smallest moving truck that finishes in D
    trips — pick a size, load boxes in order until full, count trips;
    too many trips means go bigger, few enough means try smaller
    (choosing the smallest batch size that clears a job queue by its
    deadline)."""
    def can_ship(cap: int) -> bool:        # greedy check: fill each day
        used, load = 1, 0
        for w in weights:
            load += w
            if load > cap:
                used += 1
                load = w
        return used <= days

    lo, hi = max(weights), sum(weights)    # answer bounds: one item / one day
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
    """The check is a SUM OF CEILINGS, not a greedy packing loop — and
    ceil(x/d) never grows as d grows, so the total only falls: monotone,
    lower_bound applies. Worth its own entry because the shape
    "sum(ceil(item / x)) <= budget" recurs constantly (LC 875 is this with
    the divisor named "speed"), and spotting the ceiling sum saves you
    from inventing a feasibility check.

    Naive: try divisors 1, 2, 3, ... until the sum drops under the
    threshold — O(max(nums)) passes of O(n). Each unit step re-asks "small
    enough yet?" for a single divisor; a mid probe settles half of them.

    Real life: choosing the biggest crate size so that shipping every
    order still fits in your truck-load budget — a partly filled crate
    still costs a whole crate, so test a middle size and halve the
    catalogue on the result (right-sizing a batch/page size when every
    partial batch still costs a full round trip)."""
    def sum_of_ceils(d: int) -> int:       # monotone: bigger d, smaller sum
        total = 0
        for x in nums:
            total += math.ceil(x/d)        # a partial group still costs one
        return total

    lo, hi = 1, max(nums)                  # hi always feasible: every term is 1
    while lo < hi:
        mid = (lo + hi) // 2
        if sum_of_ceils(mid) <= threshold:
            hi = mid
        else:
            lo = mid + 1
    return lo


def min_segment_repeats(s: str, k: int) -> int:  # Amazon OA
    """Given a string and segment size K, build a length-K segment and
    repeat it the fewest times m so the result holds at least the
    frequency of every character in the given string.

    Feasibility check: with m repeats, char c needs ceil(count[c] / m)
    slots in the segment, so m works iff sum(ceil(count[c] / m)) <= k.
    Below, '?' marks a spare slot — fill it with any character.

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
    """Both ends from ONE primitive: first occurrence = lower_bound(target),
    last = lower_bound(target + 1) - 1 — the first index past all targets
    is exactly one after the last target. No separate upper-bound template
    to get the off-by-ones wrong in.

    Naive: scan for the first and last match, O(n) — worst when the whole
    array IS the target. Two O(log n) boundary searches replace the scan.

    Real life: finding every "Smith" in the phone book — flip to the first
    Smith, then to the first name AFTER Smith and back up one line; the
    block between is the answer (time-range query on sorted log
    timestamps: seek first >= start, first >= end)."""
    left = lower_bound(nums, target)
    if left == len(nums) or nums[left] != target:
        return [-1, -1]
    return [left, lower_bound(nums, target + 1) - 1]


# --------------------------------------------------------------- Pattern 63
def find_median_sorted_arrays(a: list[int], b: list[int]) -> float:  # LC 4
    """Don't search a value — search the CUT. Pick i elements of a for the
    combined left half; j = half - i is forced. The cut is valid iff
    every left element <= every right element, which only needs the four
    border values. "a gave too much" (a_left > b_right) is monotone in i,
    so binary search over i in the SMALLER array finds the valid cut in
    O(log min(m, n)); the median reads straight off the borders.

    Naive: merge both arrays and index the middle — O(m + n). The merge
    computes every element's rank, but the question is only "is this one
    cut balanced?", and four comparisons answer that.

    Real life: two sorted lines of kids filing into a front room and a
    back room, half in each — slide the divider in the SHORT line (the
    other divider is forced by the head count): the split is right when
    the tallest kid up front is <= the shortest in back, and nobody had
    to merge into one line (median across two sorted DB shards without
    shipping the rows)."""
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
