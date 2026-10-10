"""Fallbacks: the version to write when the optimal one won't come.

Every problem here already has a verified optimal solution elsewhere in
pattern_code/ — each section divider names the file it came from. These are
the versions to reach for once you have blanked for ten minutes: a correct
slow solution beats staring, and in an interview it is usually the sentence
that hands you the optimization. Say the brute force, name what it wastes,
then fix that waste.

The tell you need one: you recognized the pattern but cannot recover the
mechanism. That is a review signal, not a search-harder signal — write the
fallback, then put the problem back in tomorrow's rotation.

Each function's two comment lines carry its complexity and whether it submits
green on LeetCode or merely earns full credit in an interview. The same split
is tabulated in docs/daily_warmup.md.

Written deliberately plain (no defaultdict / setdefault / zip idioms) so the
logic ports 1:1 to Java, C++, Go, JS on a whiteboard.
Run: python 19_fallbacks.py
"""

from collections import deque


# -------------------------------------- scaffolding: node types and helpers
class TreeNode:
    __slots__ = ("val", "left", "right")

    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right


class ListNode:
    __slots__ = ("val", "next")

    def __init__(self, val=0, nxt=None):
        self.val, self.next = val, nxt


def from_list(vals: list[int]) -> ListNode | None:
    head = None
    for v in reversed(vals):
        head = ListNode(v, head)
    return head


def to_list(head: ListNode | None) -> list[int]:
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def same_counts(a: dict, b: dict) -> bool:
    # Do two count dicts describe the same multiset?
    if len(a) != len(b):
        return False
    for key in a:
        if key not in b:
            return False
        if a[key] != b[key]:
            return False
    return True


# ---------------------------------------------- optimal: 01_two_pointers.py
def two_sum_sorted(nums: list[int], target: int) -> list[int]:  # LC 167
    # Fallback: ignore sortedness entirely and test every pair.
    # O(n^2), n <= 3*10^4 — TLEs on LeetCode, full credit in an interview.
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i + 1, j + 1]      # LC 167 wants 1-indexed positions
    return []


# -------------------------------------------- optimal: 02_sliding_window.py
def longest_substring_no_repeat(s: str) -> int:  # LC 3
    # Fallback: from every start, extend while a seen-set stays clean.
    # O(n^2), n <= 5*10^4 — TLEs on LeetCode, full credit in an interview.
    best = 0
    for start in range(len(s)):
        seen = set()
        end = start
        while end < len(s) and s[end] not in seen:
            seen.add(s[end])
            end += 1
        if end - start > best:
            best = end - start
    return best


def min_subarray_len(target: int, nums: list[int]) -> int:  # LC 209
    # Fallback: from every start, extend until the running sum reaches target.
    # O(n^2), n <= 10^5 — TLEs on LeetCode, full credit in an interview.
    best = 0                               # 0 means "no feasible window", as LC wants
    for start in range(len(nums)):
        total = 0
        for end in range(start, len(nums)):
            total += nums[end]
            if total >= target:
                length = end - start + 1
                if best == 0 or length < best:
                    best = length
                break                      # extending this start only lengthens it
    return best


def longest_repeating_char_replacement(s: str, k: int) -> int:  # LC 424
    # Fallback: from every start, extend while length - majority count <= k.
    # O(n^2), n <= 10^5 — TLEs on LeetCode, full credit in an interview.
    best = 0
    for start in range(len(s)):
        counts = {}
        majority = 0
        for end in range(start, len(s)):
            ch = s[end]
            if ch in counts:
                counts[ch] = counts[ch] + 1
            else:
                counts[ch] = 1
            if counts[ch] > majority:
                majority = counts[ch]
            length = end - start + 1
            if length - majority > k:
                break   # length grows by 1, majority by at most 1: never recovers
            if length > best:
                best = length
    return best


def find_anagrams(s: str, p: str) -> list[int]:  # LC 438
    # Fallback: rebuild the window's counts from scratch at every start.
    # O(n * m) — TLEs on LeetCode, full credit in an interview.
    need = {}
    for i in range(len(p)):
        ch = p[i]
        if ch in need:
            need[ch] = need[ch] + 1
        else:
            need[ch] = 1
    res = []
    for start in range(len(s) - len(p) + 1):
        window = {}
        for i in range(start, start + len(p)):
            ch = s[i]
            if ch in window:
                window[ch] = window[ch] + 1
            else:
                window[ch] = 1
        if same_counts(window, need):
            res.append(start)
    return res


# ----------------------------------------------------- optimal: 03_trees.py
def level_order(root: TreeNode | None) -> list[list[int]]:  # LC 102
    # Fallback: DFS carrying its depth, appending each value into res[depth].
    # O(n) — a real alternative to BFS rather than a downgrade; preorder still
    # reaches each level's nodes left to right.
    res: list[list[int]] = []              # invariant: res[d] holds every node seen so far at depth d

    def walk(node: TreeNode | None, depth: int) -> None:
        if node is None:
            return
        if depth == len(res):              # first node ever seen at this depth
            res.append([])
        res[depth].append(node.val)
        walk(node.left, depth + 1)
        walk(node.right, depth + 1)

    walk(root, 0)
    return res


def is_valid_bst(root: TreeNode | None) -> bool:  # LC 98
    # Fallback: flatten with an inorder walk, then check it strictly increases.
    # O(n) time and space — skips the bounds-passing trick entirely.
    vals: list[int] = []                   # invariant: values visited so far, in inorder

    def inorder(node: TreeNode | None) -> None:
        if node is None:
            return
        inorder(node.left)
        vals.append(node.val)
        inorder(node.right)

    inorder(root)
    for i in range(1, len(vals)):
        if vals[i] <= vals[i - 1]:         # equal is a violation, not a tie
            return False
    return True


def lca(root: TreeNode | None, p: TreeNode, q: TreeNode) -> TreeNode | None:  # LC 236
    # Fallback: build the root-to-node path for each target, then walk the two
    # in step — the last node they agree on is the answer.
    # O(n) time and O(h) space, no postorder reasoning required.
    def path_to(node: TreeNode | None, target: TreeNode) -> list[TreeNode] | None:
        if node is None:
            return None
        if node is target:
            return [node]
        for child in (node.left, node.right):
            below = path_to(child, target)
            if below is not None:
                return [node] + below
        return None

    a = path_to(root, p)
    b = path_to(root, q)
    if a is None or b is None:
        return None
    best = None                            # invariant: deepest node the two paths have shared so far
    limit = min(len(a), len(b))
    for i in range(limit):
        if a[i] is not b[i]:
            break
        best = a[i]
    return best


# ---------------------------------------------------- optimal: 04_graphs.py
def oranges_rotting(grid: list[list[int]]) -> int:  # LC 994
    # Fallback: rescan the whole grid each minute, rotting every fresh cell
    # touching a rotten one, until a pass changes nothing.
    # O(minutes * rc) on a <= 10x10 grid — submits green.
    rows, cols = len(grid), len(grid[0])
    minutes = 0
    while True:
        to_rot = []   # collect first: a cell rotted THIS minute must not spread yet
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] != 1:
                    continue
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 2:
                        to_rot.append((r, c))
                        break
        if not to_rot:                     # a quiet pass means the spread is over
            break
        for r, c in to_rot:
            grid[r][c] = 2
        minutes += 1
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:            # never reached by any rot front
                return -1
    return minutes


def can_finish(num_courses: int, prerequisites: list[list[int]]) -> bool:  # LC 207
    # Fallback: Kahn's — emit any course whose prerequisites are all emitted,
    # freeing its dependents. Whatever never comes free is stuck in a cycle.
    # O(V + E), the same bound as the coloring DFS — write whichever you recall.
    graph = []                             # invariant: graph[p] = courses p unlocks
    for _ in range(num_courses):
        graph.append([])
    indegree = [0] * num_courses           # invariant: prerequisites of each course not yet emitted
    for course, pre in prerequisites:
        graph[pre].append(course)
        indegree[course] += 1
    q = deque()                            # invariant: courses with every prerequisite already emitted
    for c in range(num_courses):
        if indegree[c] == 0:
            q.append(c)
    emitted = 0
    while q:
        u = q.popleft()
        emitted += 1
        for v in graph[u]:
            indegree[v] -= 1
            if indegree[v] == 0:           # last unmet prerequisite just cleared
                q.append(v)
    return emitted == num_courses


def network_delay_time(times: list[list[int]], n: int, k: int) -> int:  # LC 743
    # Fallback: Bellman-Ford — relax every edge n-1 times. No heap, and no
    # ordering argument to get right.
    # O(V * E), n <= 100 — submits green.
    INF = float("inf")
    dist = [INF] * (n + 1)                 # invariant: 1-indexed; best distance using at most `round` edges
    dist[k] = 0
    for _ in range(n - 1):                 # a shortest path uses at most n-1 edges
        changed = False
        for u, v, w in times:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:                    # a quiet round means later rounds are quiet too
            break
    worst = 0
    for node in range(1, n + 1):
        if dist[node] == INF:              # unreachable: the signal never arrives
            return -1
        if dist[node] > worst:
            worst = dist[node]
    return worst


# -------------------------------------------------------- optimal: 05_dp.py
def max_subarray(nums: list[int]) -> int:  # LC 53
    # Fallback: every (start, end) pair with a running sum.
    # O(n^2), n <= 10^5 — TLEs on LeetCode, full credit in an interview.
    best = nums[0]                         # invariant: best sum over every pair examined so far
    for start in range(len(nums)):
        total = 0
        for end in range(start, len(nums)):
            total += nums[end]
            if total > best:
                best = total
    return best


def coin_change(coins: list[int], amount: int) -> int:  # LC 322
    # Fallback: top-down memoised recursion — "fewest coins to make `rest`?"
    # Same O(amount * len(coins)) as the loop and easier to derive cold, but
    # Python recurses `amount` deep worst case: raise the limit or write the loop.
    memo = {}                              # invariant: rest -> fewest coins for it, -1 if impossible

    def fewest(rest: int) -> int:
        if rest == 0:
            return 0
        if rest < 0:
            return -1
        if rest in memo:
            return memo[rest]
        best = -1
        for coin in coins:
            below = fewest(rest - coin)
            if below != -1 and (best == -1 or below + 1 < best):
                best = below + 1
        memo[rest] = best
        return best

    return fewest(amount)


# ------------------------------------------------------ optimal: 06_heap.py
def find_kth_largest(nums: list[int], k: int) -> int:  # LC 215
    # Fallback: sort and index.
    # O(n log n) — submits green; the size-k heap only buys O(n log k).
    ordered = sorted(nums)
    return ordered[len(ordered) - k]


def top_k_frequent(nums: list[int], k: int) -> list[int]:  # LC 347
    # Fallback: count, sort the distinct values by count, take the first k.
    # O(d log d) — submits green.
    counts = {}                            # invariant: value -> occurrences so far
    for x in nums:
        if x in counts:
            counts[x] = counts[x] + 1
        else:
            counts[x] = 1
    order = list(counts.keys())
    order.sort(key=lambda x: counts[x], reverse=True)
    return order[:k]


def min_meeting_rooms(intervals: list[list[int]]) -> int:  # LC 253
    # Fallback: sort starts and ends into two separate lists and sweep them —
    # a room opens on every start that outruns the earliest unfinished end.
    # O(n log n) and no heap — submits green.
    starts = []
    ends = []
    for iv in intervals:
        starts.append(iv[0])
        ends.append(iv[1])
    starts.sort()
    ends.sort()
    rooms = 0                              # invariant: meetings running at the current start
    best = 0                               # invariant: highest concurrency seen so far
    e = 0                                  # invariant: ends[:e] are meetings already finished
    for s in starts:
        while e < len(ends) and ends[e] <= s:   # frees up before this one begins
            e += 1
            rooms -= 1
        rooms += 1
        if rooms > best:
            best = rooms
    return best


# ---------------------------------------------- optimal: 07_backtracking.py
def subsets(nums: list[int]) -> list[list[int]]:  # LC 78
    # Fallback: iterative — for each num, duplicate every subset built so far
    # and append num to the copy. No recursion and no undo step to forget.
    # O(2^n), the same bound as the recursion and often easier to write cold.
    res = [[]]                             # invariant: every subset of the nums consumed so far
    for num in nums:
        width = len(res)                   # snapshot: res grows inside this loop
        for j in range(width):
            res.append(res[j] + [num])
    return res


# ---------------------------------------------------- optimal: 08_greedy.py
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:  # LC 56
    # Fallback: no sort — fuse any overlapping pair you can find and restart
    # the scan, stopping once a full pass finds nothing left to merge.
    # O(n^3) — TLEs on LeetCode, full credit in an interview.
    out = []
    for iv in intervals:
        out.append([iv[0], iv[1]])         # copy: the fusing mutates in place
    merged = True
    while merged:
        merged = False
        for i in range(len(out)):
            for j in range(i + 1, len(out)):
                if out[i][0] <= out[j][1] and out[j][0] <= out[i][1]:
                    out[i] = [min(out[i][0], out[j][0]),
                              max(out[i][1], out[j][1])]
                    out.pop(j)
                    merged = True
                    break
            if merged:
                break
    out.sort()   # LC accepts any order; sorting matches the greedy version's output
    return out


def can_jump(nums: list[int]) -> bool:  # LC 55
    # Fallback: DP over reachability — i is reachable if some reachable j
    # before it jumps at least as far as i.
    # O(n^2), n <= 10^4 — borderline TLE, full credit in an interview.
    reachable = [False] * len(nums)        # invariant: settled for every index below the current one
    reachable[0] = True
    for i in range(1, len(nums)):
        for j in range(i):
            if reachable[j] and j + nums[j] >= i:
                reachable[i] = True
                break
    return reachable[len(nums) - 1]


# --------------------------------------------- optimal: 09_binary_search.py
def search_insert(nums: list[int], target: int) -> int:  # LC 35
    # Fallback: linear scan for the first index holding a value >= target.
    # O(n), n <= 10^4 — submits green.
    for i in range(len(nums)):
        if nums[i] >= target:
            return i
    return len(nums)                       # target belongs past the end


def find_min_rotated(nums: list[int]) -> int:  # LC 153
    # Fallback: ignore the rotation and scan for the minimum.
    # O(n), n <= 5000 — submits green.
    best = nums[0]                         # invariant: smallest value seen so far
    for x in nums:
        if x < best:
            best = x
    return best


# ----------------------------------------------------- optimal: 10_stack.py
def daily_temperatures(temps: list[int]) -> list[int]:  # LC 739
    # Fallback: for each day, scan right for the first warmer one.
    # O(n^2), n <= 10^5 — TLEs on LeetCode, full credit in an interview.
    res = [0] * len(temps)                 # invariant: 0 means "no warmer day found", as LC wants
    for i in range(len(temps)):
        for j in range(i + 1, len(temps)):
            if temps[j] > temps[i]:
                res[i] = j - i
                break
    return res


# ------------------------------------------------------ optimal: 11_bits.py
def single_number(nums: list[int]) -> int:  # LC 136
    # Fallback: count occurrences in a hash map, return the one appearing once.
    # O(n) time and O(n) space — submits green; XOR only buys the O(1) space.
    counts = {}                            # invariant: value -> occurrences so far
    for x in nums:
        if x in counts:
            counts[x] = counts[x] + 1
        else:
            counts[x] = 1
    for x in counts:
        if counts[x] == 1:
            return x
    return 0


# ----------------------------------------------- optimal: 12_linked_list.py
def reverse_list(head: ListNode | None) -> ListNode | None:  # LC 206
    # Fallback: copy the values into an array, then write them back reversed.
    # No pointer rewiring at all, so there is nothing to lose track of.
    # O(n) time and O(n) space — submits green; the rewire only buys O(1) space.
    vals = []
    node = head
    while node:
        vals.append(node.val)
        node = node.next
    node = head                            # invariant: nodes before `node` already hold reversed values
    for i in range(len(vals) - 1, -1, -1):
        node.val = vals[i]
        node = node.next
    return head                            # the head node is unchanged: only values moved


# ---------------------------------------------- optimal: 13_array_matrix.py
def product_except_self(nums: list[int]) -> list[int]:  # LC 238
    # Fallback: explicit prefix and suffix arrays instead of folding both
    # sweeps into the output array.
    # O(n) space — submits green, losing only the O(1)-space follow-up.
    n = len(nums)
    prefix = [1] * n                       # invariant: prefix[i] = product of nums[:i]
    for i in range(1, n):
        prefix[i] = prefix[i - 1] * nums[i - 1]
    suffix = [1] * n                       # invariant: suffix[i] = product of nums[i+1:]
    for i in range(n - 2, -1, -1):
        suffix[i] = suffix[i + 1] * nums[i + 1]
    res = []
    for i in range(n):
        res.append(prefix[i] * suffix[i])
    return res


# --------------------------------------------------- optimal: 14_strings.py
def is_palindrome(s: str) -> bool:  # LC 125
    # Fallback: build a cleaned lowercase copy and compare it to its reverse.
    # O(n) — not even slower, just O(n) space where two pointers used O(1).
    cleaned = []
    for ch in s:
        if ch.isalnum():                   # drop punctuation and spaces
            cleaned.append(ch.lower())
    return cleaned == cleaned[::-1]


# ---------------------------------------------------- optimal: 15_design.py
class LRUCache:  # LC 146
    # Fallback: a dict for the values plus a plain list holding the key order,
    # moved to the front on every touch. Same behaviour, none of the wiring.
    # O(n) per op from the list scan — submits green at LeetCode's op counts.

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.values = {}                   # invariant: key -> value; its keys are exactly self.order
        self.order = []                    # invariant: keys, most recently used first

    def _touch(self, key: int) -> None:
        self.order.remove(key)             # the O(n) scan the linked list exists to remove
        self.order.insert(0, key)

    def get(self, key: int) -> int:
        if key not in self.values:
            return -1
        self._touch(key)
        return self.values[key]

    def put(self, key: int, value: int) -> None:
        if key in self.values:
            self._touch(key)
        else:
            self.order.insert(0, key)
        self.values[key] = value
        if len(self.order) > self.capacity:
            del self.values[self.order.pop()]   # least recent sits at the tail


# -------------------------------------- optimal: 16_composing_structures.py
def two_sum(nums: list[int], target: int) -> list[int]:  # LC 1
    # Fallback: for every i, rescan the rest for target - nums[i].
    # O(n^2), n <= 10^4 — submits green; the dict only buys the drop to O(n).
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []


# ------------------------------------------ optimal: 17_difference_array.py
def corp_flight_bookings(bookings: list[list[int]], n: int) -> list[int]:  # LC 1109
    # Fallback: add each booking's seats to every flight in its range.
    # O(n * k) — TLEs on LeetCode, full credit in an interview.
    res = [0] * n                          # invariant: seats booked on flight i+1 by the bookings so far
    for first, last, seats in bookings:
        for f in range(first, last + 1):
            res[f - 1] += seats            # bookings are 1-indexed, res is not
    return res


# ------------------------------------------------ optimal: 18_prefix_sum.py
def pivot_index(nums: list[int]) -> int:  # LC 724
    # Fallback: at every index, sum both sides from scratch.
    # O(n^2) — borderline TLE, full credit in an interview.
    for i in range(len(nums)):
        left = 0
        for j in range(i):
            left += nums[j]
        right = 0
        for j in range(i + 1, len(nums)):  # i itself belongs to neither side
            right += nums[j]
        if left == right:
            return i
    return -1


def subarray_sum_equals_k(nums: list[int], k: int) -> int:  # LC 560
    # Fallback: every (start, end) pair with a running sum.
    # O(n^2), n <= 2*10^4 — TLEs on LeetCode, full credit in an interview.
    count = 0
    for start in range(len(nums)):
        total = 0
        for end in range(start, len(nums)):
            total += nums[end]
            if total == k:
                count += 1                 # keep going: a later end may hit k again
    return count


if __name__ == "__main__":
    assert two_sum_sorted([2, 7, 11, 15], 9) == [1, 2]

    assert longest_substring_no_repeat("abcabcbb") == 3
    assert min_subarray_len(7, [2, 3, 1, 2, 4, 3]) == 2
    assert min_subarray_len(11, [1, 1, 1]) == 0            # unreachable target
    assert longest_repeating_char_replacement("AABABBA", 1) == 4
    assert find_anagrams("cbaebabacd", "abc") == [0, 6]
    assert find_anagrams("ab", "abc") == []                # p longer than s

    #        3                    5
    #       / \                  / \
    #      9  20                3   8
    #         / \              / \  / \
    #        15  7            2  4 7   9
    t = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    bst = TreeNode(5, TreeNode(3, TreeNode(2), TreeNode(4)),
                   TreeNode(8, TreeNode(7), TreeNode(9)))
    assert level_order(t) == [[3], [9, 20], [15, 7]]
    assert is_valid_bst(bst)
    assert not is_valid_bst(TreeNode(2, TreeNode(2), TreeNode(3)))  # duplicate: inorder not strict
    assert lca(t, t.left, t.right.left) is t
    assert lca(t, t.right.left, t.right.right) is t.right

    assert oranges_rotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]]) == 4
    assert oranges_rotting([[2, 1, 1], [0, 1, 1], [1, 0, 1]]) == -1  # bottom-left walled off
    assert can_finish(2, [[1, 0]]) and not can_finish(2, [[1, 0], [0, 1]])
    assert network_delay_time([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2) == 2
    assert network_delay_time([[1, 2, 1]], 2, 2) == -1     # node 1 unreachable from 2

    assert max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
    assert max_subarray([-3, -1, -2]) == -1                # all negative: best is one element
    assert coin_change([1, 2, 5], 11) == 3
    assert coin_change([2], 3) == -1                       # unmakeable amount

    assert find_kth_largest([3, 2, 1, 5, 6, 4], 2) == 5
    assert sorted(top_k_frequent([1, 1, 1, 2, 2, 3], 2)) == [1, 2]
    assert min_meeting_rooms([[0, 30], [5, 10], [15, 20]]) == 2
    assert min_meeting_rooms([[1, 5], [5, 9]]) == 1        # touching at 5 shares one room

    assert sorted(subsets([1, 2, 3])) == \
        [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
    assert subsets([]) == [[]]                             # the empty set still has one subset

    assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == \
        [[1, 6], [8, 10], [15, 18]]
    assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]   # touching counts as overlapping
    assert can_jump([2, 3, 1, 1, 4]) and not can_jump([3, 2, 1, 0, 4])
    assert can_jump([0])                                   # already at the last index

    assert search_insert([1, 3, 5, 6], 2) == 1
    assert search_insert([1, 3, 5, 6], 7) == 4             # inserts past the end
    assert find_min_rotated([3, 4, 5, 1, 2]) == 1
    assert find_min_rotated([1, 2, 3]) == 1                # zero rotation

    assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == \
        [1, 1, 4, 2, 1, 1, 0, 0]
    assert daily_temperatures([30, 30, 30]) == [0, 0, 0]   # equal is not warmer

    assert single_number([4, 1, 2, 1, 2]) == 4
    assert single_number([-1, -1, 7]) == 7                 # negatives need no sign fixup here

    assert to_list(reverse_list(from_list([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1]
    assert reverse_list(None) is None                      # empty list: the while never runs

    assert product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6]
    assert product_except_self([0, 4, 0]) == [0, 0, 0]     # two zeros: every slot is 0

    assert is_palindrome("A man, a plan, a canal: Panama")
    assert not is_palindrome("race a car")
    assert is_palindrome(" ,")                             # nothing survives cleaning: vacuously true

    lru = LRUCache(2)
    lru.put(1, 1); lru.put(2, 2)
    assert lru.get(1) == 1
    lru.put(3, 3)                          # evicts key 2 (least recent)
    assert lru.get(2) == -1 and lru.get(3) == 3
    lru.put(3, 30)                         # overwrite: updates in place, evicts nothing
    assert lru.get(3) == 30 and lru.get(1) == 1

    assert two_sum([2, 7, 11, 15], 9) == [0, 1]
    assert two_sum([3, 3], 6) == [0, 1]                    # duplicate values, distinct indices

    assert corp_flight_bookings([[1, 2, 10], [2, 3, 20], [2, 5, 25]], 5) == \
        [10, 55, 45, 25, 25]
    assert corp_flight_bookings([[1, 2, 10], [2, 2, 15]], 2) == [10, 25]

    assert pivot_index([1, 7, 3, 6, 5, 6]) == 3
    assert pivot_index([2, 1, -1]) == 0                    # empty left side is 0
    assert subarray_sum_equals_k([1, 1, 1], 2) == 2
    assert subarray_sum_equals_k([1, -1, 0], 0) == 3       # negatives: a window would be WRONG
    print("19_fallbacks: all checks passed")
