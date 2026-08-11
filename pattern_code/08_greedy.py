"""Patterns 53-58: Greedy.

Core idea: a locally best choice that PROVABLY never hurts (exchange
argument: any optimal solution can be rearranged to start with the greedy
choice). Sorting first is the most common enabler.
Run: python 08_greedy.py
"""
import heapq
from collections import Counter


# --------------------------------------------------------------- Pattern 53
# Sort by start: overlap becomes a purely local question.
"""
intervals = [[1,3],[2,6],[8,10],[15,18]]
merged = [[1,6],[8,10],[15,18]]

[[1,3]]
2, 6 if 2<=3 
[[1,6]]
8, 10 if 8<=6
[[1,6], [8,10]]
15, 18 if 15<=10
[[1,6], [8,10], [15, 18]]

"""
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:  # LC 56
    intervals.sort()
    merged = [intervals[0][:]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:         # starts before current block ends
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def insert_interval(intervals: list[list[int]], new: list[int]) -> list[list[int]]:  # LC 57
    res: list[list[int]] = []
    i, n = 0, len(intervals)
    while i < n and intervals[i][1] < new[0]:   # entirely before
        res.append(intervals[i])
        i += 1
    while i < n and intervals[i][0] <= new[1]:  # overlapping: absorb into new
        new = [min(new[0], intervals[i][0]), max(new[1], intervals[i][1])]
        i += 1
    res.append(new)
    return res + intervals[i:]


def min_groups(intervals: list[list[int]]) -> int:  # LC 2406 (sweep line)
    # Min groups = max concurrency: +1 at each start, -1 after each end.
    events = sorted([(s, 1) for s, _ in intervals]
                    + [(e + 1, -1) for _, e in intervals])
    cur = best = 0
    for _, delta in events:
        cur += delta
        best = max(best, cur)
    return best


# --------------------------------------------------------------- Pattern 54
def can_jump(nums: list[int]) -> bool:  # LC 55
    farthest = 0
    for i, x in enumerate(nums):
        if i > farthest:                   # this cell is unreachable
            return False
        farthest = max(farthest, i + x)
    return True


def min_jumps(nums: list[int]) -> int:  # LC 45 — implicit BFS over levels
    jumps = cur_end = farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == cur_end:                   # exhausted this BFS level
            jumps += 1
            cur_end = farthest             # next level's boundary
    return jumps


# --------------------------------------------------------------- Pattern 55
def max_profit_one(prices: list[int]) -> int:  # LC 121
    best, low = 0, prices[0]               # low = best buy day so far
    for p in prices[1:]:
        best = max(best, p - low)
        low = min(low, p)
    return best


def max_profit_unlimited(prices: list[int]) -> int:  # LC 122
    # Any multi-day gain = sum of its consecutive daily rises.
    return sum(max(0, b - a) for a, b in zip(prices, prices[1:]))


# --------------------------------------------------------------- Pattern 56
def can_complete_circuit(gas: list[int], cost: list[int]) -> int:  # LC 134
    if sum(gas) < sum(cost):
        return -1                          # feasibility is global
    tank = start = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:                       # ran dry: NO station in [start, i]
            start, tank = i + 1, 0         # can work — skip them all
    return start


# --------------------------------------------------------------- Pattern 57
def least_interval(tasks: list[str], n: int) -> int:  # LC 621
    # Most frequent task is the bottleneck; others fill its forced gaps.
    counts = Counter(tasks)
    max_freq = max(counts.values())
    n_max = sum(1 for c in counts.values() if c == max_freq)
    return max(len(tasks), (max_freq - 1) * (n + 1) + n_max)


def distant_barcodes(barcodes: list[int]) -> list[int]:  # LC 1054
    # Same greedy as reorganize-string: place most frequent, bench one round.
    heap = [(-cnt, x) for x, cnt in Counter(barcodes).items()]
    heapq.heapify(heap)
    out: list[int] = []
    prev = None
    while heap:
        cnt, x = heapq.heappop(heap)
        out.append(x)
        if prev:
            heapq.heappush(heap, prev)
        cnt += 1
        prev = (cnt, x) if cnt else None
    return out


# --------------------------------------------------------------- Pattern 58
# The insight is always WHAT TO SORT BY.
def assign_cookies(children: list[int], cookies: list[int]) -> int:  # LC 455
    children.sort()
    cookies.sort()
    i = 0
    for c in cookies:                      # smallest cookie -> least greedy kid
        if i < len(children) and c >= children[i]:
            i += 1
    return i


def two_city_sched_cost(costs: list[list[int]]) -> int:  # LC 1029
    # Sort by REGRET of choosing A over B; first half goes to A.
    costs.sort(key=lambda ab: ab[0] - ab[1])
    half = len(costs) // 2
    return (sum(a for a, _ in costs[:half])
            + sum(b for _, b in costs[half:]))


def candy(ratings: list[int]) -> int:  # LC 135
    # Two passes: each direction's constraint solved independently, take max.
    n = len(ratings)
    give = [1] * n
    for i in range(1, n):                  # left-to-right: rising pairs
        if ratings[i] > ratings[i - 1]:
            give[i] = give[i - 1] + 1
    for i in range(n - 2, -1, -1):         # right-to-left: falling pairs
        if ratings[i] > ratings[i + 1]:
            give[i] = max(give[i], give[i + 1] + 1)
    return sum(give)


# ------------------------------------------- Bonus: greedy under a SCANNED
# parameter — the problem that looks like binary search but isn't.
def secure_max_deliveries(logs: list[int], k: int) -> int:  # Amazon OA
    """
    CHOP   every pile into x-sized blocks, leftovers are slivers
    FILL   k boxes: all the blocks first, then the fattest slivers
    SORT   bully takes the fullest half
    SCORE  sum what's left
    Then: do that for every x, keep the best. That's the entire algorithm.

    Scoring logs=[3, 5, 9, 6], k=4 at each cap x:
        x   boxes                 score
        1    1   1   1  1           2
        2    2   2   2  2           4
        3    3   3   3  3           6
        4    4   4   4  4           8
        5   [4]  5   5  5           9   ← best
        6   [3] [5]  6  6           8
        7   [3] [5] [6] 7           8
        8   [3] [5] [6] 8           8
        9   [3] [5] [6] 9           8

    NOT binary search: 2,4,6,8,9,8,8,8,8 peaks rather than flipping
    false->true, so check(mid) can't say which half to keep. Scan every x.
    O(max(logs) · n log n) time, O(n + k) space.
    """
    if not logs:
        return 0

    def score(x: int) -> int:                       # best haul if every box is capped at x
        blocks = sum(a // x for a in logs)          # CHOP: pieces worth a full x
        slivers = sorted((a % x for a in logs), reverse=True)
        boxes = [x] * min(blocks, k)                # FILL: blocks first, always fatter
        boxes += slivers[:k - len(boxes)]           #       top up with the biggest slivers
        boxes += [0] * (k - len(boxes))             #       any box left over holds 0
        boxes.sort()                                # SORT: bully takes the fullest half
        return sum(boxes[:k // 2])                  # SCORE: you keep the smaller half

    # default=0 covers all-zero logs, where the x range is empty.
    return max((score(x) for x in range(1, max(logs) + 1)), default=0)


if __name__ == "__main__":
    assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == \
        [[1, 6], [8, 10], [15, 18]]
    assert insert_interval([[1, 3], [6, 9]], [2, 5]) == [[1, 5], [6, 9]]
    assert min_groups([[5, 10], [6, 8], [1, 5], [2, 3], [1, 10]]) == 3
    assert can_jump([2, 3, 1, 1, 4]) and not can_jump([3, 2, 1, 0, 4])
    assert min_jumps([2, 3, 1, 1, 4]) == 2
    assert max_profit_one([7, 1, 5, 3, 6, 4]) == 5
    assert max_profit_unlimited([7, 1, 5, 3, 6, 4]) == 7
    assert can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3
    assert least_interval(list("AAABBB"), 2) == 8
    db = distant_barcodes([1, 1, 1, 2, 2, 3])
    assert all(a != b for a, b in zip(db, db[1:]))
    assert assign_cookies([1, 2, 3], [1, 1]) == 1
    assert two_city_sched_cost([[10, 20], [30, 200], [400, 50], [30, 20]]) == 110
    assert candy([1, 0, 2]) == 5 and candy([1, 2, 2]) == 4
    assert secure_max_deliveries([3, 5, 9, 6], 4) == 9   # uneven 4,5,5,6 beats even 4,4,4,4
    assert secure_max_deliveries([6], 2) == 3            # one log split in half
    assert secure_max_deliveries([], 4) == 0             # nothing to deliver
    assert secure_max_deliveries([0, 0], 4) == 0         # empty x range
    print("08_greedy: all checks passed")
