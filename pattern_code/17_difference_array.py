"""Patterns 100-106: Difference Array / Sweep + Case Classification.

Core idea: when an operation applies to a RANGE, don't touch every cell.
Record the change at the two boundaries (+x at start, -x just past end) and
recover the real array with one prefix sum. k range-updates on n cells:
O(n * k) becomes O(n + k).

The "classification" half: for each item, split the answer axis into a few
intervals where the cost is constant, then stamp each interval onto the
difference array. Getting the interval EDGES right is the whole problem.

Overflow note: every accumulator here is a running sum of ranges and is the
classic int32 trap in Java/C++ (use `long`). Python ints are arbitrary
precision, so the bug is invisible locally — see INTERVIEW_PREP.md.
Run: python 17_difference_array.py
"""
from collections import defaultdict


# -------------------------------------------------------------- Pattern 100
# The primitive. Everything below is this plus a way to pick the ranges.
def range_add(n: int, updates: list[list[int]]) -> list[int]:  # LC 370
    """Apply k "add val to range [start, end]" updates, return the final array.
    Store the DERIVATIVE, not the values: +val where the range opens and -val
    just past where it closes, so each update is two writes regardless of its
    width. One prefix sum integrates back to the real array.

    Naive: loop over every cell of every range — O(n * k), rewriting interior
    cells that only ever change at the two boundaries.

    Real life: a guest register noting arrivals and departures rather than
    who is present each hour — you re-derive occupancy by walking the day."""
    diff = [0] * (n + 1)                   # invariant: diff[i] = change entering cell i; +1 slot so end+1 always exists
    for start, end, val in updates:
        diff[start] += val
        diff[end + 1] -= val               # inclusive end -> cancel AFTER it
    out, running = [], 0
    for i in range(n):
        running += diff[i]                 # running is the accumulator: long
        out.append(running)
    return out


# -------------------------------------------------------------- Pattern 101
def corp_flight_bookings(bookings: list[list[int]], n: int) -> list[int]:  # LC 1109
    # Seats booked per flight, given k range bookings.
    # The LC 370 primitive with 1-indexed input, hence the n+2 sizing.
    # OVERFLOW: n, seats <= 1e5 with 2e4 bookings puts a single entry near
    # 2e9, past int32. `running` must be long in Java/C++ — Python hides it.
    # Naive: add seats to every flight in each range — O(n * k).
    # Real life: a seat ledger recording boarding and alighting, not headcount.
    diff = [0] * (n + 2)                   # invariant: 1-indexed, so last+1 fits without a bounds check
    for first, last, seats in bookings:
        diff[first] += seats
        diff[last + 1] -= seats
    running = 0
    res = []
    for i in range(1, n + 1):
        running += diff[i]
        res.append(running)
    return res


def car_pooling(trips: list[list[int]], capacity: int) -> bool:  # LC 1094
    """Can one car with a capacity serve all trips?
    Same sweep, but the range is HALF-OPEN: a passenger is already gone at
    `to`, so the -num lands there and not at to+1. That single index is the
    whole problem — get it wrong and two trips that merely touch collide.

    Naive: simulate each kilometre with a passenger count — O(range * trips),
    and it still needs the same boundary decision.

    Real life: a bus where riders step off AT their stop, so the seat is free
    for whoever boards at that very stop."""
    diff = [0] * 1001                      # invariant: diff[x] = net riders boarding at location x; -num at `to`, half-open
    for num, frm, to in trips:
        diff[frm] += num
        diff[to] -= num
    onboard = 0
    for delta in diff:
        onboard += delta
        if onboard > capacity:
            return False
    return True


# -------------------------------------------------------------- Pattern 102
def shifting_letters(s: str, shifts: list[list[int]]) -> str:  # LC 2381
    """Apply k range shifts (forward or backward) to a string's letters.
    A string problem in costume: only the NET shift per index matters, and
    shifts compose additively, so it is LC 370 with a modulo at the end. The
    modulo is where languages differ — a negative net shift must wrap up.

    Naive: rewrite every character in every range — O(n * k), when each range
    changes only two entries of the derivative.

    Real life: a dial you nudge back and forth many times — only the final
    reading matters, so you sum the nudges before turning it once."""
    diff = [0] * (len(s) + 1)              # invariant: diff[i] = change in net shift entering index i
    for start, end, direction in shifts:
        step = 1 if direction == 1 else -1
        diff[start] += step
        diff[end + 1] -= step
    out, running = [], 0
    for i, ch in enumerate(s):
        running += diff[i]
        # % 26 twice: Python's % is already non-negative, but be explicit for
        # the language where -1 % 26 == -1.
        out.append(chr((ord(ch) - 97 + running) % 26 + 97))
    return "".join(out)


# -------------------------------------------------------------- Pattern 103
def max_concurrent(intervals: list[list[int]]) -> int:
    """Maximum number of intervals overlapping at any single point.
    When coordinates are huge or sparse, an array indexed by position is
    unaffordable — so hash the boundaries and sort them. Only points where the
    count CHANGES matter, and there are at most 2k of those.

    Naive: allocate an array over the coordinate range — O(range) memory,
    unbounded when timestamps are epoch seconds. Comparing all pairs is O(k^2).

    Real life: counting the busiest moment in a diary by reading only the
    start and end times, in order, rather than minute by minute."""
    delta: dict[int, int] = defaultdict(int)   # invariant: coordinate -> net change in concurrency at that point
    for start, end in intervals:
        delta[start] += 1
        delta[end + 1] -= 1                # inclusive interval
    cur = best = 0
    for point in sorted(delta):
        cur += delta[point]
        best = max(best, cur)
    return best


# -------------------------------------------------------------- Pattern 104
def range_add_2d(n: int, queries: list[list[int]]) -> list[list[int]]:  # LC 2536
    """Apply k rectangle increments to an n x n grid.
    The 1-D pair of stamps becomes four by inclusion-exclusion: open at the
    top-left, close past each far edge, then ADD BACK the corner subtracted
    twice. Integrating means a prefix sum across rows and another down columns.

    Naive: increment every cell of every rectangle — O(n^2 * k), where each
    query touches only four entries of the derivative.

    Real life: shading regions on a map by marking their corners, then
    sweeping once left-to-right and once top-to-bottom to fill them in."""
    diff = [[0] * (n + 1) for _ in range(n + 1)]   # invariant: 2-D derivative; +1 margin so far edges always exist
    for r1, c1, r2, c2 in queries:
        diff[r1][c1] += 1
        diff[r1][c2 + 1] -= 1
        diff[r2 + 1][c1] -= 1
        diff[r2 + 1][c2 + 1] += 1          # double-subtracted corner, add back
    for r in range(n):
        for c in range(n):
            if r:
                diff[r][c] += diff[r - 1][c]
            if c:
                diff[r][c] += diff[r][c - 1]
            if r and c:
                diff[r][c] -= diff[r - 1][c - 1]
    return [row[:n] for row in diff[:n]]


# -------------------------------------------------------------- Pattern 105
def min_moves_complementary(nums: list[int], limit: int) -> int:  # LC 1674
    """Fewest changes so every pair nums[i] + nums[n-1-i] hits one target sum.
    THE case-classification drill: for each pair, the cost of a candidate
    target T is 0, 1 or 2 — and each cost owns a CONTIGUOUS band of T. Stamp
    the bands onto a difference array over T, integrate, take the min.

    Naive: for each candidate T, recheck every pair — O(limit * n). The bands
    let each pair contribute to all targets in O(1).

    Real life: pricing every possible settlement figure at once by recording,
    per debt, the ranges where it costs nothing, one payment, or two."""
    # The bands, for a pair (a, b) with lo = min, hi = max:
    #
    #   T in [2,              lo]          -> 2  (both must change)
    #   T in [lo + 1,         a + b - 1]   -> 1  (change one, downward)
    #   T == a + b                         -> 0
    #   T in [a + b + 1,      hi + limit]  -> 1  (change one, upward)
    #   T in [hi + limit + 1, 2 * limit]   -> 2
    #
    # Start everything at 2, subtract 1 across the whole 1-band, subtract 1
    # more at the exact 0-point. Off-by-one on lo+1 / hi+limit is the bug.
    n = len(nums)
    diff = [0] * (2 * limit + 2)           # invariant: derivative of total cost as T increases
    for i in range(n // 2):
        a, b = nums[i], nums[n - 1 - i]
        lo, hi = min(a, b), max(a, b)
        diff[lo + 1] -= 1                  # enter the "one move" band
        diff[hi + limit + 1] += 1          # leave it
        diff[a + b] -= 1                   # the single free point
        diff[a + b + 1] += 1
    best = n                               # worst case: 2 moves * n/2 pairs
    running = n                            # cost at T = 2 before any discount
    for target in range(2, 2 * limit + 1):
        running += diff[target]
        best = min(best, running)
    return best


# -------------------------------------------------------------- Pattern 106
def count_pairs_below(nums: list[int], bound: int) -> int:  # counting trap
    """Count pairs summing to less than bound.
    Not a difference array — it is here for the OVERFLOW lesson. Sorting makes
    the converging pointers work: if nums[left] + nums[right] fits, so does
    every j in (left, right], so one comparison counts a whole block of pairs.

    OVERFLOW: the answer counts PAIRS. n = 1e5 gives ~5e9 of them, which wraps
    silently in int32 — the return must be long, while left/right stay int.
    Python's unbounded ints hide this entirely; see INTERVIEW_PREP.md.

    Naive: test every pair — O(n^2), and it hits the same overflow.

    Real life: counting compatible seat pairings on a sorted guest list —
    once the extremes fit, everyone between them does too."""
    nums.sort()                            # invariant: ascending, so the block-count shortcut is valid
    left, right, total = 0, len(nums) - 1, 0   # invariant: total counts pairs already settled; long in Java/C++
    while left < right:
        if nums[left] + nums[right] < bound:
            total += right - left          # every j in (left, right] qualifies
            left += 1
        else:
            right -= 1
    return total


if __name__ == "__main__":
    assert range_add(5, [[1, 3, 2], [2, 4, 3], [0, 2, -2]]) == [-2, 0, 3, 5, 3]
    assert corp_flight_bookings([[1, 2, 10], [2, 3, 20], [2, 5, 25]], 5) == \
        [10, 55, 45, 25, 25]
    assert corp_flight_bookings([[1, 2, 10], [2, 2, 15]], 2) == [10, 25]
    assert not car_pooling([[2, 1, 5], [3, 3, 7]], 4)
    assert car_pooling([[2, 1, 5], [3, 3, 7]], 5)
    assert car_pooling([[2, 1, 5], [3, 5, 7]], 3)          # touching at 5 is OK
    assert shifting_letters("abc", [[0, 1, 0], [1, 2, 1], [0, 2, 1]]) == "ace"
    assert shifting_letters("dztz", [[0, 0, 0], [1, 1, 1]]) == "catz"
    assert max_concurrent([[5, 10], [6, 8], [1, 5], [2, 3], [1, 10]]) == 3
    assert range_add_2d(2, [[0, 0, 1, 1]]) == [[1, 1], [1, 1]]
    assert range_add_2d(3, [[1, 1, 2, 2], [0, 0, 1, 1]]) == \
        [[1, 1, 0], [1, 2, 1], [0, 1, 1]]
    assert min_moves_complementary([1, 2, 4, 3], 4) == 1
    assert min_moves_complementary([1, 2, 2, 1], 2) == 2
    assert min_moves_complementary([1, 2, 1, 2], 2) == 0
    assert count_pairs_below([1, 2, 3, 4], 6) == 4         # all but (2,4),(3,4)
    assert count_pairs_below([1, 1, 1, 1], 3) == 6         # n*(n-1)/2
    print("17_difference_array: all checks passed")
