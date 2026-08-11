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
    # Asks: nothing on its own — this is the helper the rest of the file
    # builds on. Given an array, return the running totals.
    pre = [0] * (len(nums) + 1)            # pre[0] = 0 is the empty prefix
    for i, num in enumerate(nums):
        pre[i + 1] = pre[i] + num          # pre[i] = sum of the FIRST i items
    return pre


def range_sum(pre: list[int], left: int, right: int) -> int:  # LC 303
    # Asks: given a fixed array and MANY queries, return the sum of the
    # elements from index left to index right, inclusive. The array never
    # changes, so pay O(n) once up front and answer each query in O(1).
    #
    # Inclusive [left, right]. The n+1 sizing is what makes left == 0 work
    # without a special case — pre[0] is a real slot, not an off-by-one.
    #
    # Example: nums = [-2,  0,  3, -5,  2, -1]
    #           pre = [0, -2, -2,  1, -4, -2, -3]     <- one slot longer
    #      pre index   0   1   2   3   4   5   6
    #
    #   range_sum(0, 2) = pre[3] - pre[0] =  1 - ( 0) =  1   (-2 + 0 + 3)
    #   range_sum(2, 5) = pre[6] - pre[2] = -3 - (-2) = -1   (3 - 5 + 2 - 1)
    #
    # Read it as "everything up to r, minus everything before l". The shift
    # is why the right index is r + 1 and the left index is l, not l - 1.
    return pre[right + 1] - pre[left]


# -------------------------------------------------------------- Pattern 108
def subarray_sum_equals_k(nums: list[int], k: int) -> int:  # LC 560
    # Asks: count HOW MANY contiguous subarrays sum to exactly k. Not
    # whether one exists, not where it is — the total count. Values may be
    # negative, which is the detail that rules out a sliding window.
    #
    # THE prefix-sum problem. sum(i..j) == k  <=>  pre[j+1] - pre[i] == k
    # <=> pre[i] == pre[j+1] - k. So at each j, ask how many earlier prefixes
    # equal running - k. Counting, so the map holds counts, not indices.
    #
    # seen = {0: 1} seeds the empty prefix — without it every subarray that
    # starts at index 0 is missed. This is the bug, every time.
    #
    # Note the sliding window in Exercise/Hashing.py solves a WEAKER problem:
    # shrinking from the left assumes sums only grow, which needs all values
    # >= 0. With negatives it silently returns wrong answers. Prefix + hash
    # map has no sign restriction — that is the whole reason it exists.
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
    seen = {0: 1}
    running = count = 0
    for num in nums:
        running += num
        count += seen.get(running - k, 0)   # every match is one valid start
        seen[running] = seen.get(running, 0) + 1
    return count


# -------------------------------------------------------------- Pattern 109
def subarrays_div_by_k(nums: list[int], k: int) -> int:  # LC 974
    # Asks: count how many contiguous subarrays have a sum divisible by k.
    # Same counting shape as 560, but the target is "any multiple of k"
    # instead of one exact value — so you bucket rather than look up.
    #
    # Divisibility instead of equality: the subarray sum is a multiple of k
    # <=> the two prefixes share a remainder. Bucket by remainder, then any
    # two prefixes in the same bucket define a valid subarray.
    #
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
    seen = {0: 1}
    running = count = 0
    for num in nums:
        running = (running + num) % k
        count += seen.get(running, 0)
        seen[running] = seen.get(running, 0) + 1
    return count


def check_subarray_sum(nums: list[int], k: int) -> bool:  # LC 523
    # Asks: does there EXIST a contiguous subarray of length at least 2
    # whose sum is a multiple of k? True/False only. Two shifts from 974:
    # existence instead of a count, and a minimum length — so the map now
    # stores indices (to measure length) instead of counts.
    #
    # Same remainder idea, but existence with a LENGTH constraint (>= 2), so
    # store the EARLIEST index per remainder and never overwrite — the
    # earliest gives the longest span and the best shot at clearing the gap.
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
    first = {0: -1}                        # empty prefix "ends" before index 0
    running = 0
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
    # Asks: given an array of only 0s and 1s, return the LENGTH of the
    # longest contiguous subarray containing an equal number of each.
    # Length, not the subarray itself; 0 if none exists.
    #
    # "Equal counts of 0 and 1" is not a sum condition until you remap 0 to
    # -1. Then equal counts == sum 0 == two prefixes with the SAME value, and
    # the longest such subarray is the widest gap between repeats.
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
    first = {0: -1}
    running = best = 0
    for i, num in enumerate(nums):
        running += 1 if num == 1 else -1
        if running in first:
            best = max(best, i - first[running])
        else:
            first[running] = i             # longest -> keep the earliest only
    return best


# -------------------------------------------------------------- Pattern 111
def pivot_index(nums: list[int]) -> int:  # LC 724
    # Asks: find the LEFTMOST index where the sum of everything strictly to
    # its left equals the sum of everything strictly to its right. The
    # pivot element itself belongs to neither side. Return -1 if no such
    # index exists. An empty side sums to 0, so index 0 can qualify.
    #
    # You rarely need the whole prefix array — one running left sum plus the
    # total gives the right side for free: right == total - left - nums[i].
    #
    # Example: nums = [1, 7, 3, 6, 5, 6], total = 28   ->   3
    #
    #   i  num  left  right = 28 - left - num
    #   0    1     0    27
    #   1    7     1    20
    #   2    3     8    17
    #   3    6    11    11    <- balanced, and nums[3] itself counts as
    #                            neither side
    total, left = sum(nums), 0
    for i, num in enumerate(nums):
        if left == total - left - num:
            return i
        left += num                        # add AFTER the test: i is excluded
    return -1


def min_start_value(nums: list[int]) -> int:  # LC 1413
    # Asks: you walk the array adding each element to a running total.
    # Return the SMALLEST positive starting value that keeps that total at
    # 1 or above at every single step. Note "positive" — the answer is
    # never below 1, even when the array never dips.
    #
    # Prefix MIN rather than prefix sum: the worst dip the running total ever
    # takes decides the starting value. Answer is 1 - lowest, floored at 1
    # (lowest starts at 0, so a never-negative array yields exactly 1).
    #
    # Example: nums = [-3, 2, -3, 4, 2]   ->   5
    #
    #   running   -3  -1  -4   0   2      lowest dip = -4
    #   start 5:   2   4   1   5   7      never below 1  (5 - 4 == 1)
    #   start 4:   1   3   0   4   6      hits 0 at step 3  -> too small
    running = lowest = 0
    for num in nums:
        running += num
        lowest = min(lowest, running)
    return 1 - lowest


# -------------------------------------------------------------- Pattern 112
def build_prefix_2d(matrix: list[list[int]]) -> list[list[int]]:  # LC 304
    # Asks: same deal as 303 but on a grid — a fixed matrix and many
    # queries, each naming a rectangle by its top-left and bottom-right
    # corners, wanting the sum inside. Build once, answer each in O(1).
    #
    # Inclusion-exclusion: the two overlapping arms double-count the corner
    # block, so subtract it back. Mirror of the four-corner stamp in
    # 17_difference_array.range_add_2d — same identity, opposite direction.
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
    pre = [[0] * (cols + 1) for _ in range(rows + 1)]
    for r in range(rows):
        for c in range(cols):
            pre[r + 1][c + 1] = (matrix[r][c] + pre[r][c + 1]
                                 + pre[r + 1][c] - pre[r][c])
    return pre


def region_sum(pre: list[list[int]], r1: int, c1: int, r2: int, c2: int) -> int:
    # Big rectangle, minus the strip above, minus the strip left, plus the
    # top-left block that both strips removed.
    #
    # Example: on the [[1, 2], [3, 4]] prefix above, region_sum(1, 0, 1, 1)
    # asks for the bottom row: pre[2][2] - pre[1][2] - pre[2][0] + pre[1][0]
    #                        =    10     -     3     -     0     +     0    = 7
    return pre[r2 + 1][c2 + 1] - pre[r1][c2 + 1] - pre[r2 + 1][c1] + pre[r1][c1]


def num_submatrix_sum_target(matrix: list[list[int]], target: int) -> int:
    # Asks: count how many submatrices (any rectangle, any size) sum to
    # target. Rectangles at different positions count separately even if
    # identical. This is 560's question with two dimensions of freedom.
    #
    # LC 1074. The composition worth knowing: fix a pair of rows, and every
    # column strip between them collapses to a single number -> the 2D
    # problem IS pattern 108 run once per row pair. O(rows^2 * cols).
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
    # Asks: for each query [left, right], return the XOR of every element
    # from left to right inclusive. Return one answer per query, in order.
    # Structurally identical to 303 — only the operator changed.
    #
    # Nothing about the technique needs addition — it needs an associative op
    # with an inverse. XOR is its own inverse, so "subtract" is another XOR.
    #
    # Example: arr = [1, 3, 4, 8]
    #          pre = [0, 1, 2, 6, 14]        pre[i+1] = pre[i] ^ arr[i]
    #
    #   query [1, 2] -> pre[3] ^ pre[1] = 6 ^ 1 = 7   (and 3 ^ 4 == 7)
    #
    # The cancellation is the point: pre[3] already contains 1^3^4, and
    # XOR-ing pre[1] == 1 back in deletes the 1, leaving 3^4.
    pre = [0] * (len(arr) + 1)
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
