"""
Package Delivery System (Amazon OA, Medium)
https://www.fastprep.io/problems/amazon-package-delivery-system

Each scenario has a list of truck capacities and a list of package weights.
A truck may deliver any package whose weight does not exceed its CURRENT
capacity. After a successful delivery that truck's capacity becomes
floor(capacity / 2). Return 1 if every package in the scenario can be
delivered, else 0 — one answer per scenario.

Core insight
------------
Deliver the heaviest remaining package with the truck that currently has the
largest capacity.

Why greedy is safe: the heaviest package is the hardest to place, so if the
biggest truck can't take it nothing can and the scenario is infeasible. And
because halving is monotone (a >= b  =>  a//2 >= b//2), spending the biggest
truck on the biggest package never leaves the fleet worse off than spending a
smaller truck on it. A max-heap keeps "current largest capacity" O(log t).

Complexity per scenario: O(n log n + n log t)  time, O(t) space
  n = packages, t = trucks.
  
  

More examples, as reference:
    capacities  weights       out  why
    [10, 5]     [5, 5]        1    10 takes one 5 (-> 5), truck 5 the other
    [10, 5]     [10, 5]       1    10 must take the 10 (-> 5), then 5 -> 5
    [8]         [8, 4, 2, 1]  1    halving chain: c, c//2, c//4, ...
    [8]         [8, 8]        0    capacity c can't serve two loads > c//2
"""


import heapq
from typing import List


def can_deliver(capacities: List[int], weights: List[int]) -> int:
    """Return 1 if all `weights` can be delivered by `capacities`, else 0."""
    if not weights:
        return 1
    if not capacities:
        return 0

    # Max-heap via negation (heapq is a min-heap).
    heap = [-c for c in capacities]
    heapq.heapify(heap)

    for w in sorted(weights, reverse=True):
        largest = -heap[0]
        if largest < w:
            # Invariant: heap[0] is the best capacity available. If the best
            # can't take the heaviest remaining package, nothing can.
            return 0
        # Pop + push in one sift: the truck delivers, then halves.
        heapq.heapreplace(heap, -(largest // 2))

    return 1


def package_delivery(
    truck_capacities: List[List[int]],
    package_weights: List[List[int]],
) -> List[int]:
    """Solve every scenario; returns a list of 1/0 flags."""
    return [
        can_deliver(caps, weights)
        for caps, weights in zip(truck_capacities, package_weights)
    ]


if __name__ == "__main__":
    # Example 1: truck 7 delivers 4 -> capacity 3 -> delivers 3. Feasible.
    assert package_delivery([[7]], [[4, 3]]) == [1]

    # 7 -> 3 after delivering 4, so a second 4 has nowhere to go.
    assert package_delivery([[7]], [[4, 4]]) == [0]

    # Two trucks handle the pair of 4s.
    assert package_delivery([[7, 4]], [[4, 4]]) == [1]

    # Package heavier than any truck.
    assert package_delivery([[3, 2]], [[5]]) == [0]

    # Multiple scenarios at once.
    assert package_delivery(
        [[7], [7], [8, 5]],
        [[4, 3], [4, 4], [5, 5, 4]],
    ) == [1, 0, 1]

    # No trucks but packages exist.
    assert package_delivery([[]], [[1]]) == [0]

    # No packages is trivially feasible.
    assert package_delivery([[]], [[]]) == [1]


    print("all tests passed")
