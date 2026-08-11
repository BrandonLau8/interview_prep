"""Patterns 42-45: Heap (Priority Queue).

Core idea: you repeatedly need the current min/max of a CHANGING collection;
full sorting is overkill. For a final top-k, a size-k heap gives O(n log k).
Python's heapq is a MIN-heap; negate values for max-heap behavior.
Run: python 06_heap.py
"""
import heapq
from collections import Counter


# --------------------------------------------------------------- Pattern 42
# Min-heap of size k for the k LARGEST: root = weakest of the elite k.
def find_kth_largest(nums: list[int], k: int) -> int:  # LC 215
    heap = nums[:k]
    heapq.heapify(heap)
    for x in nums[k:]:
        if x > heap[0]:                    # beats the weakest -> evict it
            heapq.heapreplace(heap, x)
    return heap[0]


def top_k_frequent(nums: list[int], k: int) -> list[int]:  # LC 347
    counts = Counter(nums)
    return [x for x, _ in
            heapq.nlargest(k, counts.items(), key=lambda kv: kv[1])]


def k_closest(points: list[list[int]], k: int) -> list[list[int]]:  # LC 973
    # k CLOSEST -> max-heap of size k (negate distance).
    heap: list[tuple[int, list[int]]] = []
    for x, y in points:
        heapq.heappush(heap, (-(x * x + y * y), [x, y]))
        if len(heap) > k:
            heapq.heappop(heap)            # farthest of the k leaves
    return [p for _, p in heap]


class KthLargest:  # LC 703 — streaming: the size-k heap IS the answer state
    def __init__(self, k: int, nums: list[int]):
        self.k = k
        self.heap = nums
        heapq.heapify(self.heap)
        while len(self.heap) > k:
            heapq.heappop(self.heap)

    def add(self, val: int) -> int:
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)
        return self.heap[0]


# --------------------------------------------------------------- Pattern 43
class MedianFinder:  # LC 295
    """Max-heap lower half + min-heap upper half; median lives at the roots."""

    def __init__(self):
        self.lo: list[int] = []            # max-heap (negated)
        self.hi: list[int] = []            # min-heap

    def add_num(self, num: int) -> None:
        heapq.heappush(self.lo, -num)      # push low, then rebalance:
        heapq.heappush(self.hi, -heapq.heappop(self.lo))  # top of lo -> hi
        if len(self.hi) > len(self.lo):    # lo may hold one extra
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def find_median(self) -> float:
        if len(self.lo) > len(self.hi):
            return -self.lo[0]
        return (-self.lo[0] + self.hi[0]) / 2


# --------------------------------------------------------------- Pattern 44
# K-way merge: the global min must be one of the k current heads.
def merge_k_sorted(lists: list[list[int]]) -> list[int]:  # LC 23 (array form)
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(heap)
    out = []
    while heap:
        val, i, j = heapq.heappop(heap)    # pop the min head...
        out.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))  # ...reveal next
    return out


def kth_smallest_in_matrix(matrix: list[list[int]], k: int) -> int:  # LC 378
    n = len(matrix)
    heap = [(matrix[i][0], i, 0) for i in range(min(n, k))]
    heapq.heapify(heap)
    for _ in range(k - 1):
        _, i, j = heapq.heappop(heap)
        if j + 1 < n:
            heapq.heappush(heap, (matrix[i][j + 1], i, j + 1))
    return heap[0][0]


def smallest_range(lists: list[list[int]]) -> list[int]:  # LC 632
    # Range = [min of heads, max of heads]; only advancing the MIN can shrink it.
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists)]
    heapq.heapify(heap)
    hi = max(lst[0] for lst in lists)
    best = [heap[0][0], hi]
    while True:
        lo, i, j = heapq.heappop(heap)
        if hi - lo < best[1] - best[0]:
            best = [lo, hi]
        if j + 1 == len(lists[i]):         # one list exhausted: can't cover all
            return best
        nxt = lists[i][j + 1]
        hi = max(hi, nxt)
        heapq.heappush(heap, (nxt, i, j + 1))


# --------------------------------------------------------------- Pattern 45
# Scheduling: sort by start; heap = resources keyed by when they free up.
def min_meeting_rooms(intervals: list[list[int]]) -> int:  # LC 253
    intervals.sort()
    ends: list[int] = []                   # min-heap of room end times
    for start, end in intervals:
        if ends and ends[0] <= start:      # earliest-free room is free: reuse
            heapq.heapreplace(ends, end)
        else:
            heapq.heappush(ends, end)      # must open a new room
    return len(ends)                       # high-water mark of concurrency


def reorganize_string(s: str) -> str:  # LC 767
    # Greedy: always place the most frequent letter, holding back the one
    # just used for a round.
    heap = [(-cnt, ch) for ch, cnt in Counter(s).items()]
    heapq.heapify(heap)
    out: list[str] = []
    prev = None                            # (count_left, char) benched one turn
    while heap:
        cnt, ch = heapq.heappop(heap)
        out.append(ch)
        if prev:
            heapq.heappush(heap, prev)     # bench is over, back in the pool
        cnt += 1                           # one copy used (counts negative)
        prev = (cnt, ch) if cnt else None
    return "".join(out) if not prev else ""   # leftover = impossible


if __name__ == "__main__":
    assert find_kth_largest([3, 2, 1, 5, 6, 4], 2) == 5
    assert sorted(top_k_frequent([1, 1, 1, 2, 2, 3], 2)) == [1, 2]
    assert sorted(k_closest([[1, 3], [-2, 2]], 1)) == [[-2, 2]]
    kl = KthLargest(3, [4, 5, 8, 2])
    assert [kl.add(3), kl.add(5), kl.add(10)] == [4, 5, 5]
    mf = MedianFinder()
    for x in (1, 2):
        mf.add_num(x)
    assert mf.find_median() == 1.5
    mf.add_num(3)
    assert mf.find_median() == 2
    assert merge_k_sorted([[1, 4, 5], [1, 3, 4], [2, 6]]) == \
        [1, 1, 2, 3, 4, 4, 5, 6]
    assert kth_smallest_in_matrix([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8) == 13
    assert smallest_range([[4, 10, 15, 24, 26], [0, 9, 12, 20],
                           [5, 18, 22, 30]]) == [20, 24]
    assert min_meeting_rooms([[0, 30], [5, 10], [15, 20]]) == 2
    r = reorganize_string("aab")
    assert all(a != b for a, b in zip(r, r[1:])) and sorted(r) == ["a", "a", "b"]
    assert reorganize_string("aaab") == ""
    print("06_heap: all checks passed")
