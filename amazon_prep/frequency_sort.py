"""
Frequency Sort (Amazon OA, Easy)

Reorder an array so the most frequent values come first. Ties may be broken in
any order.

    [1, 1, 2, 2, 2, 3] -> [2, 2, 2, 1, 1, 3]

Core insight
------------
Count, then sort the DISTINCT keys — not the elements. There may be far fewer
distinct values than elements, and expanding each key back out by its count is
linear.

The tie-break, stated: this implementation keeps first-appearance order for
equal counts. That falls out of two Python guarantees — `Counter` iterates in
insertion order, and `sorted` is stable. Java and C++ give you no such
guarantee; there you must sort on the explicit pair (-count, first_index) or
ties come out scrambled.

Complexity: O(n log n) time — the sort over distinct keys dominates, counting
is O(n). O(n) space.

More examples, as reference:
    nums                out                     why
    [1]                 [1]                     nothing to sort
    [1, 2, 3]           [1, 2, 3]               all counts 1, stable = original
    [-1, -1, 3, 3, 5]   [-1, -1, 3, 3, 5]       tie at 2, -1 appeared first
    [9, 9, 1, 1, 1]     [1, 1, 1, 9, 9]         count beats position
"""

from collections import Counter
from typing import List


def frequency_sort(nums: List[int]) -> List[int]:
    """Sort by descending frequency; equal counts keep first-appearance order."""
    count = Counter(nums)

    # Sort the distinct keys only. Key is -count (descending); `sorted` is
    # stable, so Counter's insertion order survives as the tie-break.
    order = sorted(count, key=lambda v: -count[v])
    
    out = []
    for v in order:
        out.extend([v] * count[v])
    return out


def frequency_sort_explicit(nums: List[int]) -> List[int]:
    """Same result, tie-break spelled out — the version to write in Java/C++.

    Nothing here relies on dict ordering or sort stability.
    """
    count = Counter(nums)
    first_index = {}
    for i, v in enumerate(nums):
        if v not in first_index:
            first_index[v] = i

    order = sorted(count, key=lambda v: (-count[v], first_index[v]))

    out = []
    for v in order:
        out.extend([v] * count[v])
    return out


if __name__ == "__main__":
    for solve in (frequency_sort, frequency_sort_explicit):
        # The basic shape: biggest pile first.
        assert solve([1, 1, 2, 2, 2, 3]) == [2, 2, 2, 1, 1, 3]

        # Single element.
        assert solve([1]) == [1]

        # All distinct: every count is 1, so a stable sort returns the input.
        assert solve([4, 2, 7]) == [4, 2, 7]

        # Negative values work as hash keys — never index an array by value.
        assert solve([-1, 3, -1, 3, 5]) == [-1, -1, 3, 3, 5]

        # Values up to 1e9: a count array of that size blows memory, a hash
        # map does not.
        assert solve([10**9, 10**9, 7]) == [10**9, 10**9, 7]

        # Count outranks position.
        assert solve([9, 9, 1, 1, 1]) == [1, 1, 1, 9, 9]

        # Empty input.
        assert solve([]) == []

    print("all tests passed")
