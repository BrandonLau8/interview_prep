"""
Course Schedule II (LC 210, Amazon OA favorite, Medium)
https://leetcode.com/problems/course-schedule-ii/

n courses labeled 0..n-1 and a list of pairs [a, b] meaning "take b BEFORE a."
Return any valid order to finish all courses, or [] if it is impossible.

Core insight
------------
Kahn's algorithm: repeatedly take any course with zero remaining prerequisites,
then decrement the prerequisite count of everything it unblocks. A node enters
the queue exactly when its LAST blocker clears.

If the queue empties before all n courses are emitted, the leftovers form a
cycle — every one of them is waiting on another leftover. Cycle detection is
therefore just `len(order) != n`; no colors, no recursion stack.

Complexity: O(n + m) time — each node is dequeued once, each edge relaxed once.
O(n + m) space for the adjacency list.

The edge direction is THE bug in this problem: [a, b] means b -> a, because b
must finish first and its completion is what unblocks a. Reversing it produces
a plausible-looking order that is wrong.

More examples, as reference:
    n  prerequisites          out            why
    2  [[1, 0]]               [0, 1]         0 unblocks 1
    2  [[1, 0], [0, 1]]       []             deadlock
    4  [[1,0],[2,0],[3,1]]    [0,1,2,3]      or [0,2,1,3] — any valid order
    1  [[0, 0]]               []             self-loop, indegree never hits 0
    3  []                     [0, 1, 2]      no constraints at all
"""

from collections import deque
from typing import List


def find_order(n: int, prerequisites: List[List[int]]) -> List[int]:
    """Return a topological order of 0..n-1, or [] if a cycle exists."""
    graph = [[] for _ in range(n)]
    indegree = [0] * n
    for course, need in prerequisites:      # [a, b] = take b BEFORE a
        graph[need].append(course)          # edge points need -> course
        indegree[course] += 1

    # Seed with EVERY zero-indegree node, which handles disconnected
    # components with no special case.
    q = deque(i for i in range(n) if indegree[i] == 0)

    order = []
    while q:
        node = q.popleft()
        order.append(node)
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:          # last blocker just cleared
                q.append(nxt)

    # Invariant: anything still holding indegree > 0 is inside a cycle.
    return order if len(order) == n else []


def _is_valid_order(n: int, prerequisites: List[List[int]], order: List[int]) -> bool:
    """Test helper: the order is a permutation of 0..n-1 respecting every edge."""
    if sorted(order) != list(range(n)):
        return False
    position = {course: i for i, course in enumerate(order)}
    return all(position[need] < position[course] for course, need in prerequisites)


if __name__ == "__main__":
    # Simple chain.
    assert find_order(2, [[1, 0]]) == [0, 1]

    # Two-node cycle.
    assert find_order(2, [[1, 0], [0, 1]]) == []

    # Self-loop: indegree of 0 never reaches 0.
    assert find_order(1, [[0, 0]]) == []

    # No prerequisites: every node starts unblocked.
    assert find_order(3, []) == [0, 1, 2]

    # Diamond — several valid answers, so check the property, not one output.
    prereqs = [[1, 0], [2, 0], [3, 1], [3, 2]]
    assert _is_valid_order(4, prereqs, find_order(4, prereqs))

    # Disconnected components.
    prereqs = [[1, 0], [3, 2]]
    assert _is_valid_order(4, prereqs, find_order(4, prereqs))

    # A cycle hiding among otherwise-fine nodes.
    assert find_order(4, [[1, 0], [2, 3], [3, 2]]) == []

    # Single course.
    assert find_order(1, []) == [0]

    # Deep chain — BFS has no recursion limit; a naive DFS at n = 2e5 would
    # blow the Python stack.
    n = 200_000
    chain = [[i + 1, i] for i in range(n - 1)]
    assert find_order(n, chain) == list(range(n))

    print("all tests passed")
