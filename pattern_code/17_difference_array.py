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
    diff = [0] * (n + 1)                   # +1 slot so end+1 never overflows
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
    # Same primitive, 1-indexed input. n, seats <= 1e5 and 2e4 bookings ->
    # a single entry can reach 2e9 > 2^31-1. Accumulator must be 64-bit.
    diff = [0] * (n + 2)
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
    # Drop-off happens AT `to`, so the passenger is gone by then: -num at `to`,
    # not at `to + 1`. Half-open ranges are the rule for "location" problems.
    diff = [0] * 1001
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
    # String manipulation wearing a difference array: net shift per index.
    diff = [0] * (len(s) + 1)
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
    # Coordinates too large / sparse to index an array: hash the boundaries
    # and sort. O(k log k) instead of O(coordinate range).
    delta: dict[int, int] = defaultdict(int)
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
    # 2D: one corner stamp becomes four (inclusion-exclusion), then a prefix
    # sum along rows and another down columns.
    diff = [[0] * (n + 1) for _ in range(n + 1)]
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
    # THE case-classification drill. For each pair (a, b) and each candidate
    # target sum T, the cost is one of {0, 1, 2} — and each cost owns a
    # contiguous band of T. Stamp the bands, prefix-sum, take the min.
    #
    #   T in [2,           lo]          -> 2  (both must change)
    #   T in [lo + 1,      a + b - 1]   -> 1  (change one, downward)
    #   T == a + b                      -> 0
    #   T in [a + b + 1,   hi + limit]  -> 1  (change one, upward)
    #   T in [hi + limit + 1, 2*limit]  -> 2
    #
    # Start everything at 2, subtract 1 across the whole 1-band, subtract 1
    # more at the exact 0-point. Off-by-one on lo+1 / hi+limit is the bug.
    n = len(nums)
    diff = [0] * (2 * limit + 2)
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
    # Not a difference array — the OTHER half of the prompt. The answer is a
    # COUNT OF PAIRS: n = 1e5 gives ~5e9 pairs, which silently wraps in int32.
    # Return type must be long; `left`/`right` stay int.
    nums.sort()
    left, right, total = 0, len(nums) - 1, 0
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
