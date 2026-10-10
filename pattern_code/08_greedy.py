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
    """Collapse overlapping intervals into the fewest disjoint ones.
    Sorting by start makes overlap purely local: once starts are ordered, an
    interval can only overlap the block currently being built, never an
    earlier one — so a single `start <= merged[-1][1]` test decides everything.

    Naive: compare every interval against every other and merge transitively —
    O(n^2), plus the bookkeeping of merges that cascade into each other.

    Real life: booking a meeting room from a stack of requests sorted by start
    time — you only ever look at the booking you are currently extending."""
    intervals.sort()                       # invariant: ascending by start
    merged = [intervals[0][:]]             # invariant: disjoint and sorted; only merged[-1] can still grow
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:         # starts before current block ends
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def insert_interval(intervals: list[list[int]], new: list[int]) -> list[list[int]]:  # LC 57
    """Insert one interval into an already-sorted disjoint list, merging as needed.
    Sortedness splits the list into three runs — entirely before, overlapping,
    entirely after — so the answer is three loops with no comparisons repeated.
    The overlapping run is absorbed into `new` as you go, which is the merge.

    Naive: append and re-run LC 56 — O(n log n) to re-sort a list that was
    already sorted, when the three runs make it O(n).

    Real life: slotting one new appointment into a tidy diary — you skip the
    mornings it misses, swallow whatever it touches, and copy the rest."""
    res: list[list[int]] = []
    i, n = 0, len(intervals)               # invariant: intervals is sorted and pairwise disjoint
    while i < n and intervals[i][1] < new[0]:   # entirely before
        res.append(intervals[i])
        i += 1
    while i < n and intervals[i][0] <= new[1]:  # overlapping: absorb into new
        new = [min(new[0], intervals[i][0]), max(new[1], intervals[i][1])]
        i += 1
    res.append(new)
    return res + intervals[i:]


def min_groups(intervals: list[list[int]]) -> int:  # LC 2406 (sweep line)
    """Fewest groups such that no group holds two overlapping intervals.
    The reframe is the whole problem: minimum groups equals maximum
    concurrency. Once you see that, the intervals stop mattering — only the
    +1/-1 events do, and the answer is the running sum's peak.

    Naive: actually assign intervals to groups, scanning existing groups for
    a free one — O(n^2) and it builds an assignment nobody asked for.

    Real life: counting how many meeting rooms a day needs by walking the
    clock and tracking how many meetings are in progress at once."""
    events = sorted([(s, 1) for s, _ in intervals]
                    + [(e + 1, -1) for _, e in intervals])   # invariant: e+1 so touching intervals don't count as concurrent
    cur = best = 0                         # invariant: cur = intervals open at this instant
    for _, delta in events:
        cur += delta
        best = max(best, cur)
    return best


# --------------------------------------------------------------- Pattern 54
def can_jump(nums: list[int]) -> bool:  # LC 55
    """Can you reach the last index, each value being a max jump length?
    Reachability is an interval, not a set: if you can reach i you can reach
    everything before it, so one number — the farthest reachable index —
    holds the entire state. Falling behind it once means unreachable.

    Naive: DFS or DP over which indices are reachable — O(n^2) exploring
    individual jumps that the running maximum already summarizes.

    Real life: crossing a stream on stepping stones, tracking only how far
    ahead you could possibly land — not which stone you would use."""
    farthest = 0                           # invariant: every index <= farthest is reachable
    for i, x in enumerate(nums):
        if i > farthest:                   # this cell is unreachable
            return False
        farthest = max(farthest, i + x)
    return True


def min_jumps(nums: list[int]) -> int:  # LC 45 — implicit BFS over levels
    """Fewest jumps to reach the last index.
    This is BFS with the queue left implicit: everything reachable in j jumps
    forms a contiguous level, so the level boundary is one index. Hitting
    cur_end means the level is exhausted — bump the count, adopt the new edge.

    Naive: DP over min jumps to each index — O(n^2), computing per-index
    answers when only the level boundaries change the count.

    Real life: island-hopping where each hop must be booked a day ahead —
    you count days, and each day you may reach anywhere the fleet now covers."""
    jumps = cur_end = farthest = 0         # invariant: cur_end ends the current level, farthest ends the next
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == cur_end:                   # exhausted this BFS level
            jumps += 1
            cur_end = farthest             # next level's boundary
    return jumps


# --------------------------------------------------------------- Pattern 55
def max_profit_one(prices: list[int]) -> int:  # LC 121
    """Best profit from one buy and one later sell.
    Selling on day i, the best you could have done is buying at the cheapest
    day before it — so one running minimum answers "what was my best entry?"
    in O(1) per day. The ordering constraint is free because low trails i.

    Naive: check every (buy, sell) pair — O(n^2), where the inner scan just
    re-finds the minimum the running value already tracks.

    Real life: watching a stock ticker and remembering only the lowest price
    you have seen, because that is the only entry you would regret missing."""
    best, low = 0, prices[0]               # invariant: low = cheapest price strictly before today
    for p in prices[1:]:
        best = max(best, p - low)
        low = min(low, p)
    return best


def max_profit_unlimited(prices: list[int]) -> int:  # LC 122
    """Best profit with unlimited buys and sells, one share at a time.
    Any multi-day gain telescopes into the sum of its consecutive daily rises,
    so holding through a rise is worth exactly as much as selling and re-buying
    each day. Every positive step is therefore free money — take them all.

    Naive: DP over (day, holding?) states — correct and O(n), but it searches
    for a decision the telescoping shows was never a decision at all.

    Real life: a hill walk where you are paid for altitude gained — the total
    climb is the same whether you count it in one push or step by step."""
    return sum(max(0, b - a) for a, b in zip(prices, prices[1:]))


# --------------------------------------------------------------- Pattern 56
def can_complete_circuit(gas: list[int], cost: list[int]) -> int:  # LC 134
    """The station to start from to drive the whole circuit, or -1.
    Two separate facts: feasibility is GLOBAL (total gas >= total cost, else
    no start works), while the start is LOCAL. Running dry at i rules out
    every station in [start, i] at once — each had at least as much fuel.

    Naive: simulate a full lap from each of the n stations — O(n^2), redoing
    laps that the failure at i already proved impossible.

    Real life: a fuel-stop loop where running out between two towns tells you
    no earlier town in that stretch would have got you further either."""
    if sum(gas) < sum(cost):
        return -1                          # feasibility is global
    tank = start = 0                       # invariant: tank = fuel accumulated since start, never negative
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:                       # ran dry: NO station in [start, i]
            start, tank = i + 1, 0         # can work — skip them all
    return start


# --------------------------------------------------------------- Pattern 57
def least_interval(tasks: list[str], n: int) -> int:  # LC 621
    """Time to run all tasks with a cooldown of n between equal tasks.
    No simulation at all — the most frequent task is the bottleneck, forcing
    (max_freq - 1) frames of width n+1 plus a tail of the tied tasks. Other
    tasks either fit the idle gaps or, if too numerous, len(tasks) dominates.

    Naive: simulate the schedule slot by slot with a heap — O(total time),
    which the closed form skips entirely by counting the forced structure.

    Real life: a laundry run gated by the one machine with the longest cycle —
    everything else gets folded while you wait, so the cycle sets the clock."""
    counts = Counter(tasks)                # invariant: task -> how many times it must run
    max_freq = max(counts.values())
    n_max = sum(1 for c in counts.values() if c == max_freq)
    return max(len(tasks), (max_freq - 1) * (n + 1) + n_max)


def distant_barcodes(barcodes: list[int]) -> list[int]:  # LC 1054
    # Rearrange so no two adjacent barcodes are equal.
    # Identical greedy to reorganize_string in 06_heap.py: place the value
    # with the most copies left, bench the one just used for exactly one round.
    # Naive: shuffle and retest — unbounded; any greedy ignoring remaining
    # counts strands the surplus value in a run at the end.
    # Real life: dealing a deck so no two neighbouring cards share a suit.
    heap = [(-cnt, x) for x, cnt in Counter(barcodes).items()]   # invariant: negated counts, heap[0] is most frequent
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
    """Most children satisfiable, each needing a cookie of at least their size.
    Exchange argument: give the smallest adequate cookie to the least greedy
    child. Any optimal assignment can be rewritten this way without serving
    fewer children, so the greedy choice is provably never a loss.

    Naive: try all assignments — n! matchings, or bipartite matching for
    O(n^3), when both sides sorted make one linear sweep sufficient.

    Real life: handing out sandwiches by size to a queue sorted by appetite —
    the fussiest eater gets served last, if at all."""
    children.sort()                        # invariant: ascending greed
    cookies.sort()                         # invariant: ascending size
    i = 0                                  # invariant: children[:i] are all satisfied
    for c in cookies:                      # smallest cookie -> least greedy kid
        if i < len(children) and c >= children[i]:
            i += 1
    return i


def two_city_sched_cost(costs: list[list[int]]) -> int:  # LC 1029
    """Send exactly half the people to city A and half to B, cheapest total.
    Sorting by raw cost is the trap — what matters is REGRET, a - b, how much
    worse A is than B for that person. Sorted by regret, the people who lose
    least by flying to A are exactly the first half, and the split is forced.

    Naive: try all C(2n, n) balanced splits — exponential. Regret collapses a
    pairing problem into one sort because each person's trade-off is independent.

    Real life: assigning a team to two offices when everyone has a different
    commute penalty — you move whoever minds the far office least."""
    costs.sort(key=lambda ab: ab[0] - ab[1])   # invariant: ascending regret of choosing A over B
    half = len(costs) // 2
    return (sum(a for a, _ in costs[:half])
            + sum(b for _, b in costs[half:]))


def candy(ratings: list[int]) -> int:  # LC 135
    """Fewest candies so everyone gets one and beats a lower-rated neighbour.
    Two constraints pull in opposite directions, so solve each alone and take
    the max — the left-to-right pass satisfies every rising pair, the
    right-to-left pass every falling one, and max satisfies both at once.

    Naive: iterate fixing violations until nothing changes — O(n^2) in a long
    slope, since one fix cascades backwards through the whole run.

    Real life: seating bonuses along a row where each person must out-earn a
    weaker neighbour — you walk the row once each way and pay the higher claim."""
    n = len(ratings)
    give = [1] * n                         # invariant: after pass 1, rising pairs hold; after pass 2, both do
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

    Naive: search over which log to cut where — exponential. Capping every box
    at one x collapses that choice, leaving only the greedy fill per x.

    Real life: cutting timber to a single sawmill setting, where a bully takes
    the fattest half of the load — the setting that maximizes YOUR half is not
    the largest one, so you try each setting rather than climbing toward it.
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
