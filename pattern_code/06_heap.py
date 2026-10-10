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
    """kth largest value, counting duplicates.
    Keep a MIN-heap of size k holding the best k seen: its root is the weakest
    of the elite, so one comparison decides whether a newcomer joins. The
    inversion is the whole trick — you need a min to guard a set of maxima.

    Naive: sort and index — O(n log n), and it orders the n-k elements you
    never look at. The size-k heap costs O(n log k).

    Real life: a talent shortlist of k names where the only person you ever
    compare against is the weakest one on it — anyone better bumps them."""
    heap = nums[:k]                        # invariant: the k largest seen so far, weakest at heap[0]
    heapq.heapify(heap)
    for x in nums[k:]:
        if x > heap[0]:                    # beats the weakest -> evict it
            heapq.heapreplace(heap, x)
    return heap[0]


def top_k_frequent(nums: list[int], k: int) -> list[int]:  # LC 347
    """The k values that occur most often.
    Two questions, two structures: the counter answers "how often?", the
    size-k selection answers "which are the top?". nlargest is LC 215's heap
    with a key — and the counting must finish before the selection can start.

    Naive: sort every distinct value by count — O(d log d) when only k of
    them will ever be read.

    Real life: tallying votes on a sheet, then reading off the k tallest
    columns instead of ranking every candidate."""
    counts = Counter(nums)                 # invariant: value -> total occurrences, counting complete
    return [x for x, _ in
            heapq.nlargest(k, counts.items(), key=lambda kv: kv[1])]


def k_closest(points: list[list[int]], k: int) -> list[list[int]]:  # LC 973
    """The k points nearest the origin.
    Mirror image of LC 215: for the k SMALLEST you need a MAX-heap, so the
    root is the worst of what you are keeping. Negating the distance turns
    heapq's min-heap into that max-heap; squared distance skips the sqrt.

    Naive: sort all n points by distance — O(n log n) to answer a question
    that only concerns k of them.

    Real life: a shortlist of the k nearest restaurants where the only entry
    you ever check is the current farthest — anything closer knocks it off."""
    heap: list[tuple[int, list[int]]] = []   # invariant: the k closest so far, farthest at heap[0]
    for x, y in points:
        heapq.heappush(heap, (-(x * x + y * y), [x, y]))
        if len(heap) > k:
            heapq.heappop(heap)            # farthest of the k leaves
    return [p for _, p in heap]


class KthLargest:  # LC 703 — streaming: the size-k heap IS the answer state
    """Report the kth largest value after every add, on an endless stream.
    The size-k min-heap is the entire answer state: anything that falls out
    of the top k can never re-enter it, so it is safe to forget forever.
    That makes each query an O(1) root read and each add O(log k).

    Naive: retain every value and re-select per query — O(n log n) each time,
    with memory growing without bound on a stream that never ends.

    Real life: a leaderboard with exactly k slots — a new score either makes
    the board and pushes the last one off, or is discarded on the spot."""

    def __init__(self, k: int, nums: list[int]):
        self.k = k
        self.heap = nums                   # invariant: the k largest seen, kth largest at heap[0]
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
    """Streaming median: take numbers one at a time, report the middle on demand.
    Two heaps split the data at the median — a max-heap of the lower half, a
    min-heap of the upper — so both candidates sit at a root. Push to lo, move
    lo's top to hi to force the ordering, then rebalance so lo leads by at
    most one — which is what gives an odd count a single middle.

    Naive: keep a sorted list and insert in place — O(n) per add from the
    shifting; re-sorting per query is O(n log n).

    Real life: two piles of index cards, low and high, each stacked so the
    relevant extreme faces up — you only ever read the two facing cards."""

    def __init__(self):
        self.lo: list[int] = []            # invariant: lower half, negated so lo[0] is its max
        self.hi: list[int] = []            # invariant: upper half, hi[0] is its min; len(lo) - len(hi) in {0, 1}

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
    """Merge k sorted lists into one sorted list.
    The global minimum must be the head of some list — nothing sitting behind
    a head can beat it — so a heap over just the k heads answers "what comes
    next?" in O(log k). Popping a head reveals exactly one replacement.

    Naive: concatenate everything and sort — O(N log N), throwing away the
    sortedness you were handed. Rescanning all k heads each step is O(Nk).

    Real life: merging sorted card piles by always taking the smallest
    face-up card, then flipping the next card from that same pile."""
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]   # invariant: one entry per non-exhausted list, its current head
    heapq.heapify(heap)
    out = []
    while heap:
        val, i, j = heapq.heappop(heap)    # pop the min head...
        out.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))  # ...reveal next
    return out


def kth_smallest_in_matrix(matrix: list[list[int]], k: int) -> int:  # LC 378
    """kth smallest in a matrix with every row and column sorted.
    The same k-way merge as LC 23 with rows playing the lists, stopped after
    k pops instead of drained. Seeding only min(n, k) rows is the detail that
    matters: row k and beyond cannot supply a value that early.

    Naive: flatten the matrix and sort — O(n^2 log n) to learn one position.

    Real life: merging sorted score sheets but shutting the folder the moment
    you have counted out k names."""
    n = len(matrix)
    heap = [(matrix[i][0], i, 0) for i in range(min(n, k))]   # invariant: current head of each row still in play
    heapq.heapify(heap)
    for _ in range(k - 1):
        _, i, j = heapq.heappop(heap)
        if j + 1 < n:
            heapq.heappush(heap, (matrix[i][j + 1], i, j + 1))
    return heap[0][0]


def smallest_range(lists: list[list[int]]) -> list[int]:  # LC 632
    """Smallest range covering at least one number from every list.
    Any candidate range spans [min of heads, max of heads]. Only advancing the
    MINIMUM head can shrink it — moving any other head raises the max and
    helps nothing — so each step has exactly one forced move, which the heap picks.

    Naive: try every pair of values as a range and test coverage — O(V^2 * k).
    The heads already enumerate the only ranges worth considering.

    Real life: k friends on separate trails meeting at the tightest cluster of
    milestones — you only ever tell whoever is furthest behind to move up."""
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists)]   # invariant: one current head per list
    heapq.heapify(heap)
    hi = max(lst[0] for lst in lists)      # invariant: largest head currently in the heap
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
    """Fewest rooms that can hold every meeting.
    Sorting by start makes arrivals chronological; a heap keyed by end time
    answers "has any room freed up?" by reading a single number. The heap's
    final size is the concurrency high-water mark, which is the answer.

    Naive: for each meeting, scan all the others for overlap — O(n^2), and it
    still doesn't hand you the peak overlap directly.

    Real life: a receptionist holding room keys ordered by when each room
    frees up — only the key coming back soonest is ever worth checking."""
    intervals.sort()                       # invariant: meetings processed in start order
    ends: list[int] = []                   # min-heap of room end times
    for start, end in intervals:
        if ends and ends[0] <= start:      # earliest-free room is free: reuse
            heapq.heapreplace(ends, end)
        else:
            heapq.heappush(ends, end)      # must open a new room
    return len(ends)                       # high-water mark of concurrency


def reorganize_string(s: str) -> str:  # LC 767
    """Rearrange s so no two adjacent chars match, or "" if impossible.
    Whichever letter has the most copies LEFT is the most urgent — deferring
    it is exactly what strands a run at the end. So place the current max and
    bench the letter just used for one round, which is what forbids a repeat.

    Naive: generate permutations and test each — factorial. A greedy driven by
    anything other than remaining count leaves the surplus letter stuck last.

    Real life: handing out chores so nobody draws two in a row — you assign
    whoever has the most left, and they sit out the very next slot."""
    heap = [(-cnt, ch) for ch, cnt in Counter(s).items()]   # invariant: negated counts, so heap[0] is the most frequent
    heapq.heapify(heap)
    out: list[str] = []
    prev = None                            # invariant: (count_left, char) benched for exactly this round
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
    assert reorganize_string("aaab") == ""     # majority letter exceeds the gaps: impossible
    print("06_heap: all checks passed")
