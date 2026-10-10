"""Patterns 107-113: Prefix Sum.

Core idea: the exact inverse of 17_difference_array. There the WRITES were
ranges and the reads were points; here the writes are points and the READS
are ranges. Precompute one running total, then any range answer is a single
subtraction: sum(l..r) == pre[r + 1] - pre[l]. O(n) space buys O(1) queries.

The multiplier: once every subarray is a DIFFERENCE of two prefixes, the
question "is there a subarray with property P?" becomes "have I seen a
prefix value that pairs with this one?" — which is a hash map lookup. That
single reframe is patterns 108-110 and most of the interview value here.

Prefix sums work for any associative op with an inverse: + (subtract),
XOR (XOR itself), * (only when no zeros — usually not worth it).
Run: python 18_prefix_sum.py
"""


# -------------------------------------------------------------- Pattern 107
# The primitive. Everything below is this plus a way to pair up two prefixes.
def build_prefix(nums: list[int]) -> list[int]:
    """Running totals, the helper the rest of this file is built on.
    The n+1 sizing is the whole design: pre[0] = 0 is a real slot holding the
    empty prefix, which is what lets every range formula work at index 0
    without a special case. pre[i] means "sum of the FIRST i items".

    Naive: recompute each range sum on demand — O(n) per query, re-adding
    the same leading elements every time.

    Real life: a bank statement's running balance column — every transaction
    total between two dates is one subtraction, never a re-tally."""
    pre = [0] * (len(nums) + 1)            # invariant: pre[i] = sum of the first i items; pre[0] = empty prefix
    for i, num in enumerate(nums):
        pre[i + 1] = pre[i] + num          # pre[i] = sum of the FIRST i items
    return pre


def range_sum(pre: list[int], left: int, right: int) -> int:  # LC 303
    """Sum of nums[left..right] inclusive, for many queries on a fixed array.
    Read it as "everything up to r, minus everything before l". The array
    never changes, so pay O(n) once and answer each query with one
    subtraction. The shift is why the right index is r+1 and the left is l.

    Naive: sum the slice per query — O(n) each, O(nq) overall, re-adding the
    same elements for every overlapping query.

    Real life: quoting the rainfall between two dates off a cumulative chart
    — you read two points and subtract, never re-adding the days between."""
    #
    # Example: nums = [-2,  0,  3, -5,  2, -1]
    #           pre = [0, -2, -2,  1, -4, -2, -3]     <- one slot longer
    #      pre index   0   1   2   3   4   5   6
    #
    #   range_sum(0, 2) = pre[3] - pre[0] =  1 - ( 0) =  1   (-2 + 0 + 3)
    #   range_sum(2, 5) = pre[6] - pre[2] = -3 - (-2) = -1   (3 - 5 + 2 - 1)
    return pre[right + 1] - pre[left]


# -------------------------------------------------------------- Pattern 108
def subarray_sum_equals_k(nums: list[int], k: int) -> int:  # LC 560
    """Count contiguous subarrays summing to exactly k; values may be negative.
    THE prefix-sum problem. sum(i..j) == k <=> pre[i] == pre[j+1] - k, so at
    each j the question is "how many earlier prefixes equal running - k?" —
    a map lookup. Counting, so the map holds counts, not indices.

    Naive: sum every (start, end) pair — O(n^2). A sliding window is worse
    than slow, it is WRONG here: shrinking from the left assumes sums only
    grow, which needs all values >= 0 (see 09_binary_search.py's warning).

    Real life: a running expense tape — if it reads $12 today and read $7
    before, the days between cost exactly $5, however many refunds intervened."""
    # seen = {0: 1} seeds the empty prefix — without it every subarray that
    # starts at index 0 is missed. This is the bug, every time.
    #
    # Example: nums = [1, 2, 3], k = 3   ->   2
    #
    #   num  running  need=running-k  seen BEFORE update   hit
    #    1      1          -2         {0:1}                 -
    #    2      3           0         {0:1, 1:1}           yes  -> [1,2]
    #    3      6           3         {0:1, 1:1, 3:1}      yes  -> [3]
    #
    # The step-2 hit is the seed doing its job: need == 0 means "the
    # subarray starts at index 0". Drop {0: 1} and this returns 1.
    seen = {0: 1}                          # invariant: prefix value -> how many times seen, incl. the empty prefix
    running = count = 0                    # invariant: running = sum of everything consumed so far
    for num in nums:
        running += num
        count += seen.get(running - k, 0)   # every match is one valid start
        seen[running] = seen.get(running, 0) + 1
    return count


# -------------------------------------------------------------- Pattern 109
def subarrays_div_by_k(nums: list[int], k: int) -> int:  # LC 974
    """Count contiguous subarrays whose sum is divisible by k.
    Divisibility replaces equality: a subarray sum is a multiple of k exactly
    when its two prefixes share a REMAINDER. So bucket prefixes by remainder,
    and any two in one bucket define a valid subarray — LC 560 with a key change.

    Naive: sum every subarray and test the modulus — O(n^2), where bucketing
    pairs every arrival with all its predecessors at once.

    Real life: matching receipts that settle to a whole number of banknotes —
    two tapes ending on the same loose change cancel out between them."""
    # Python's % is already non-negative; in Java/C++ -1 % 5 == -1, so you
    # need ((r % k) + k) % k or the buckets split in two.
    #
    # Example: nums = [4, 5, 0, -2, -3, 1], k = 5   ->   7
    #
    #   num  running % 5  bucket size before  new pairs  total
    #    4        4              0               0         0
    #    5        4              1               1         1
    #    0        4              2               2         3
    #   -2        2              0               0         3
    #   -3        4              3               3         6
    #    1        0              1               1         7      <- seed
    #
    # Each arrival pairs with EVERY earlier prefix in its bucket, so a
    # bucket of size m contributes m*(m-1)/2 overall — that is why you add
    # the count before inserting, not after.
    seen = {0: 1}                          # invariant: remainder -> how many prefixes landed on it
    running = count = 0                    # invariant: running is a remainder in [0, k)
    for num in nums:
        running = (running + num) % k
        count += seen.get(running, 0)
        seen[running] = seen.get(running, 0) + 1
    return count


def check_subarray_sum(nums: list[int], k: int) -> bool:  # LC 523
    """Does a contiguous subarray of length >= 2 sum to a multiple of k?
    Two shifts from LC 974: existence rather than a count, and a minimum
    LENGTH — so the map stores indices instead of counts. Keep only the
    EARLIEST index per remainder, since that gives the widest span to clear.

    Naive: test every subarray of length >= 2 — O(n^2). Remainders answer it
    in one pass, provided you never overwrite an earlier sighting.

    Real life: asking whether any stretch of at least two days netted a whole
    number of banknotes — you remember the first day each remainder appeared."""
    #
    # Example: nums = [23, 2, 4, 6, 7], k = 6   ->   True
    #
    #   i  num  running % 6  first          gap        verdict
    #   0   23       5       {0:-1}         new -> 0    -
    #   1    2       1       {0:-1, 5:0}    new -> 1    -
    #   2    4       5       seen at 0      2 - 0 = 2   True -> [2,4] sums 6
    #
    # If that repeat had been at i = 1 the gap would be 1 and the scan must
    # CONTINUE, not return False — a later repeat can still be far enough.
    first = {0: -1}                        # invariant: remainder -> EARLIEST index; empty prefix "ends" before index 0
    running = 0                            # invariant: remainder of the prefix through index i
    for i, num in enumerate(nums):
        running = (running + num) % k
        if running in first:
            if i - first[running] >= 2:
                return True
        else:
            first[running] = i             # only on first sight
    return False


# -------------------------------------------------------------- Pattern 110
def contiguous_array(nums: list[int]) -> int:  # LC 525
    """Length of the longest subarray of 0s and 1s holding equal counts of each.
    "Equal counts" is not a sum condition until you remap 0 to -1. Then it
    becomes sum 0, i.e. two prefixes with the SAME value, and the longest such
    subarray is the widest gap between repeats — so keep the earliest index.

    Naive: check every subarray, counting both values — O(n^2) with running
    counts. The remap turns the whole question into prefix equality.

    Real life: sharing biscuits with a sibling, +1 you and -1 them — whenever
    the score revisits a number, the stretch between was perfectly fair."""
    # Same problem as find_max_length in 16_composing_structures.py, which
    # frames it as one-question-one-structure rather than as a prefix sum.
    #
    # Example: nums = [0, 0, 1, 0, 0, 0, 1, 1]   ->   6
    #
    #   i        0   1   2   3   4   5   6   7
    #   num      0   0   1   0   0   0   1   1
    #   step    -1  -1  +1  -1  -1  -1  +1  +1
    #   running -1  -2  -1  -2  -3  -4  -3  -2
    #   first    0   1   ^   ^   4   5   ^   ^
    #                    |                   |
    #                    +--- -2 first at i=1, again at i=7: 7 - 1 = 6
    #
    # That span is indices 2..7 = [1,0,0,0,1,1] — three of each. Note -1
    # also repeats (i=0, i=2) but only spans 2, so the max wins.
    first = {0: -1}                        # invariant: balance -> EARLIEST index; never overwritten
    running = best = 0                     # invariant: running = (count of 1s) - (count of 0s) so far
    for i, num in enumerate(nums):
        running += 1 if num == 1 else -1
        if running in first:
            best = max(best, i - first[running])
        else:
            first[running] = i             # longest -> keep the earliest only
    return best


# -------------------------------------------------------------- Pattern 111
def pivot_index(nums: list[int]) -> int:  # LC 724
    """Leftmost index where the sum strictly left equals the sum strictly right.
    You rarely need the whole prefix array — one running left sum plus the
    total gives the right side free: right == total - left - nums[i]. The
    pivot belongs to neither side, which is why left is updated AFTER the test.

    Naive: for each index, sum both sides — O(n^2), recomputing totals that
    shift by one element per step.

    Real life: finding the balance point of a loaded plank by walking along
    it with the weight behind you tallied and the total already known."""
    # An empty side sums to 0, so index 0 can qualify.
    #
    # Example: nums = [1, 7, 3, 6, 5, 6], total = 28   ->   3
    #
    #   i  num  left  right = 28 - left - num
    #   0    1     0    27
    #   1    7     1    20
    #   2    3     8    17
    #   3    6    11    11    <- balanced, and nums[3] itself counts as
    #                            neither side
    total, left = sum(nums), 0             # invariant: left = sum of everything strictly before i
    for i, num in enumerate(nums):
        if left == total - left - num:
            return i
        left += num                        # add AFTER the test: i is excluded
    return -1


def min_start_value(nums: list[int]) -> int:  # LC 1413
    """Smallest positive start value keeping the running total >= 1 throughout.
    Prefix MIN, not prefix sum: only the worst dip the total ever takes
    decides the answer, so one number summarizes the whole walk. Seeding
    lowest at 0 is what floors the result at 1 for an array that never dips.

    Naive: try candidate start values from 1 upward, simulating each —
    O(answer * n), where a single pass already reveals the binding constraint.

    Real life: deciding how much cash to start the day with, given the day's
    takings and payouts — only the moment the till runs lowest matters."""
    #
    # Example: nums = [-3, 2, -3, 4, 2]   ->   5
    #
    #   running   -3  -1  -4   0   2      lowest dip = -4
    #   start 5:   2   4   1   5   7      never below 1  (5 - 4 == 1)
    #   start 4:   1   3   0   4   6      hits 0 at step 3  -> too small
    running = lowest = 0                   # invariant: lowest = worst running total seen, never above 0
    for num in nums:
        running += num
        lowest = min(lowest, running)
    return 1 - lowest


# -------------------------------------------------------------- Pattern 112
def build_prefix_2d(matrix: list[list[int]]) -> list[list[int]]:  # LC 304
    """Cumulative sums over a grid, so any rectangle query costs O(1).
    Inclusion-exclusion in two dimensions: the arm above and the arm to the
    left both contain the top-left block, so subtract it back once. Exact
    mirror of range_add_2d in 17_difference_array.py — same identity, inverted.

    Naive: sum the rectangle's cells per query — O(rc) each, re-adding
    interior cells shared by every overlapping query.

    Real life: a cumulative rainfall map read from the origin — any region's
    total is four corner readings combined, never a cell-by-cell survey."""
    #
    # Example: matrix = [[1, 2],        pre = [[0, 0,  0],
    #                    [3, 4]]               [0, 1,  3],
    #                                          [0, 4, 10]]
    #
    #   pre[r][c] = sum of the rectangle from the origin up to (but not
    #   including) row r, col c.  pre[2][2] = 1+2+3+4 = 10.
    #
    #   Filling pre[2][2]:  matrix[1][1]  +  pre[1][2]  +  pre[2][1]  -  pre[1][1]
    #                            4        +      3      +      4      -      1     = 10
    #                       the cell      arm above      arm left     overlap
    rows, cols = len(matrix), len(matrix[0])
    pre = [[0] * (cols + 1) for _ in range(rows + 1)]   # invariant: pre[r][c] = sum of the block above-left, excluding row r and col c
    for r in range(rows):
        for c in range(cols):
            pre[r + 1][c + 1] = (matrix[r][c] + pre[r][c + 1]
                                 + pre[r + 1][c] - pre[r][c])
    return pre


def region_sum(pre: list[list[int]], r1: int, c1: int, r2: int, c2: int) -> int:
    # Sum of the rectangle (r1, c1) to (r2, c2), inclusive, in O(1).
    # Big rectangle, minus the strip above, minus the strip left, plus the
    # top-left block that both strips removed — the same inclusion-exclusion
    # that built the table, applied in reverse.
    # Naive: iterate the rectangle — O(rc) per query.
    # Real life: reading four corner totals off the rainfall map.
    #
    # Example: on the [[1, 2], [3, 4]] prefix above, region_sum(1, 0, 1, 1)
    # asks for the bottom row: pre[2][2] - pre[1][2] - pre[2][0] + pre[1][0]
    #                        =    10     -     3     -     0     +     0    = 7
    return pre[r2 + 1][c2 + 1] - pre[r1][c2 + 1] - pre[r2 + 1][c1] + pre[r1][c1]


def num_submatrix_sum_target(matrix: list[list[int]], target: int) -> int:
    """Count submatrices summing to target; LC 1074, i.e. LC 560 in two dimensions.
    The composition worth knowing: FIX a pair of rows, and every column strip
    between them collapses to one number — so the 2-D problem becomes pattern
    108 run once per row pair. O(rows^2 * cols), and identical rectangles at
    different positions count separately.

    Naive: enumerate all four corners and sum each rectangle — O(r^2 c^2 * rc),
    or O(r^2 c^2) with the prefix table but still without the hash-map trick.

    Real life: auditing a spreadsheet for blocks netting zero by fixing a band
    of rows, then sweeping across columns with a running tally."""
    #
    # Example: matrix = [[0, 1, 0],  target = 0   ->   4
    #                    [1, 1, 1],
    #                    [0, 1, 0]]
    #
    #   Row pair (0,0) — only row 0, strips [0, 1, 0], column prefixes
    #   0, 1, 1.  seen starts {0:1}:
    #       running 0 -> need 0, seen has it        -> the lone 0 at col 0
    #       running 1 -> need 1, not yet seen       -> -
    #       running 1 -> need 1, seen at col 1      -> the lone 0 at col 2
    #   Two more come from row pairs (1,1) and (2,2). The 3-row pairs all
    #   fail because every full column sums to 1.
    rows, cols = len(matrix), len(matrix[0])
    pre = build_prefix_2d(matrix)
    count = 0
    for top in range(rows):
        for bot in range(top, rows):
            seen = {0: 1}                  # reset per row pair, not per cell
            for c in range(cols):
                # Already a prefix over columns — no separate accumulator.
                running = pre[bot + 1][c + 1] - pre[top][c + 1]
                count += seen.get(running - target, 0)
                seen[running] = seen.get(running, 0) + 1
    return count


# -------------------------------------------------------------- Pattern 113
def xor_queries(arr: list[int], queries: list[list[int]]) -> list[int]:  # LC 1310
    """XOR of arr[left..right] for each query — LC 303 with the operator swapped.
    Nothing in the technique needs addition; it needs an associative operation
    with an INVERSE. XOR is its own inverse, so the "subtraction" step is
    another XOR. That is the whole generalization, and why this file ends here.

    Naive: XOR the slice per query — O(n) each, re-folding the same leading
    elements for every overlapping query.

    Real life: parity checks along a tape — combining two checkpoints cancels
    everything they share, leaving only the stretch between them."""
    #
    # Example: arr = [1, 3, 4, 8]
    #          pre = [0, 1, 2, 6, 14]        pre[i+1] = pre[i] ^ arr[i]
    #
    #   query [1, 2] -> pre[3] ^ pre[1] = 6 ^ 1 = 7   (and 3 ^ 4 == 7)
    #
    # The cancellation is the point: pre[3] already contains 1^3^4, and
    # XOR-ing pre[1] == 1 back in deletes the 1, leaving 3^4.
    pre = [0] * (len(arr) + 1)             # invariant: pre[i] = XOR of the first i items; pre[0] = 0 is the identity
    for i, num in enumerate(arr):
        pre[i + 1] = pre[i] ^ num
    return [pre[right + 1] ^ pre[left] for left, right in queries]


if __name__ == "__main__":
    pre = build_prefix([-2, 0, 3, -5, 2, -1])
    assert range_sum(pre, 0, 2) == 1
    assert range_sum(pre, 2, 5) == -1
    assert range_sum(pre, 0, 5) == -3       # full range, exercises pre[0]
    assert range_sum(pre, 3, 3) == -5       # single element

    assert subarray_sum_equals_k([1, 1, 1], 2) == 2
    assert subarray_sum_equals_k([1, 2, 3], 3) == 2
    assert subarray_sum_equals_k([1, 2, 3], 6) == 1   # needs the {0: 1} seed
    assert subarray_sum_equals_k([-1, -1, 1], 0) == 1  # window would miss it
    assert subarray_sum_equals_k([1, -1, 0], 0) == 3

    assert subarrays_div_by_k([4, 5, 0, -2, -3, 1], 5) == 7
    assert subarrays_div_by_k([5], 9) == 0
    assert check_subarray_sum([23, 2, 4, 6, 7], 6)
    assert check_subarray_sum([23, 2, 6, 4, 7], 6)     # whole array, sum 42
    assert not check_subarray_sum([23, 2, 6, 4, 7], 13)
    assert check_subarray_sum([0, 0], 1)               # length rule, not value
    assert not check_subarray_sum([0], 1)

    assert contiguous_array([0, 1]) == 2
    assert contiguous_array([0, 1, 0]) == 2
    assert contiguous_array([0, 0, 1, 0, 0, 0, 1, 1]) == 6
    assert contiguous_array([1, 1, 1]) == 0

    assert pivot_index([1, 7, 3, 6, 5, 6]) == 3
    assert pivot_index([1, 2, 3]) == -1
    assert pivot_index([2, 1, -1]) == 0                # empty left side is 0
    assert min_start_value([-3, 2, -3, 4, 2]) == 5
    assert min_start_value([1, 2]) == 1                # never dips -> floor 1
    assert min_start_value([1, -2, -3]) == 5

    grid = [[3, 0, 1, 4, 2],
            [5, 6, 3, 2, 1],
            [1, 2, 0, 1, 5],
            [4, 1, 0, 1, 7],
            [1, 0, 3, 0, 5]]
    grid_pre = build_prefix_2d(grid)
    assert region_sum(grid_pre, 2, 1, 4, 3) == 8
    assert region_sum(grid_pre, 1, 1, 2, 2) == 11
    assert region_sum(grid_pre, 1, 2, 2, 4) == 12
    assert region_sum(grid_pre, 0, 0, 0, 0) == 3
    assert num_submatrix_sum_target([[0, 1, 0], [1, 1, 1], [0, 1, 0]], 0) == 4
    assert num_submatrix_sum_target([[1, -1], [-1, 1]], 0) == 5
    assert num_submatrix_sum_target([[904]], 0) == 0

    assert xor_queries([1, 3, 4, 8], [[0, 1], [1, 2], [0, 3], [3, 3]]) == \
        [2, 7, 14, 8]
    print("18_prefix_sum: all checks passed")
